"""AgroPulse API: crop catalog, recommendations, farms, plots and measurements."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any
from uuid import uuid4

import firebase_admin
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from firebase_admin import auth as firebase_auth
from firebase_admin import credentials as firebase_credentials
from firebase_admin import exceptions as firebase_exceptions
from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from pydantic import BaseModel, Field, ValidationError, field_validator

from recommendations import (
    Crop,
    CropThresholds,
    MeasurementValues,
    Recommendation,
    evaluate_measurement,
)

API_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = API_DIR.parents[1]
load_dotenv(API_DIR / ".env")

app = FastAPI(
    title="AgroPulse API",
    description="API para catálogo de cultivos, parcelas y recomendaciones agronómicas",
    version="1.0.0",
)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "FRONTEND_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000"
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

bearer_scheme = HTTPBearer(auto_error=False)


def _credential_path() -> Path | None:
    configured_path = (
        os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
        or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    )
    if configured_path:
        path = Path(configured_path).expanduser()
        candidates = (
            [path]
            if path.is_absolute()
            else [API_DIR / path, REPOSITORY_ROOT / path]
        )
        for candidate in candidates:
            resolved = candidate.resolve()
            if resolved.is_file():
                return resolved
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se encontró el archivo de credenciales de Firebase configurado.",
        )

    default_path = REPOSITORY_ROOT / "firebase" / "serviceAccountKey.json"
    return default_path if default_path.is_file() else None


@lru_cache(maxsize=1)
def get_firebase_app() -> firebase_admin.App:
    try:
        return firebase_admin.get_app()
    except ValueError:
        credential_path = _credential_path()
        try:
            if credential_path:
                credential = firebase_credentials.Certificate(str(credential_path))
                return firebase_admin.initialize_app(credential)
            return firebase_admin.initialize_app()
        except (ValueError, firebase_exceptions.FirebaseError) as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Firebase no está configurado. Define "
                    "FIREBASE_SERVICE_ACCOUNT_PATH o GOOGLE_APPLICATION_CREDENTIALS."
                ),
            ) from exc


def get_firestore() -> Any:
    return firestore.client(get_firebase_app())


def get_current_user_id(
    token: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere iniciar sesión.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        claims = firebase_auth.verify_id_token(
            token.credentials, app=get_firebase_app()
        )
    except (ValueError, firebase_exceptions.FirebaseError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token de Firebase no es válido o expiró.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    user_id = claims.get("uid")
    if not isinstance(user_id, str) or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token no contiene un usuario válido.",
        )
    return user_id


class FarmInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    location: str = Field(min_length=1, max_length=200)

    @field_validator("name", "location")
    @classmethod
    def trim_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Este campo no puede estar vacío.")
        return value


class PlotInput(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    crop_id: str = Field(alias="cropId", min_length=1)

    @field_validator("name", "crop_id")
    @classmethod
    def trim_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Este campo no puede estar vacío.")
        return value


class MeasurementInput(MeasurementValues):
    date: str = Field(min_length=1)
    notes: str = Field(default="", max_length=1000)

    @field_validator("date")
    @classmethod
    def validate_date(cls, value: str) -> str:
        try:
            datetime.fromisoformat(value)
        except ValueError as exc:
            raise ValueError("La fecha debe ser una fecha ISO válida.") from exc
        return value


class RecommendationInput(MeasurementValues):
    crop_id: str = Field(alias="cropId", min_length=1)


def _crop_from_snapshot(snapshot: Any) -> Crop:
    if not snapshot.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el cultivo solicitado.",
        )
    data = snapshot.to_dict() or {}
    data["id"] = snapshot.id
    try:
        return Crop.model_validate(data)
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"El documento del cultivo {snapshot.id} tiene datos inválidos.",
        ) from exc


def _list_crops(db: Any) -> list[Crop]:
    crops = [_crop_from_snapshot(snapshot) for snapshot in db.collection("crops").stream()]
    return sorted(crops, key=lambda crop: crop.name.casefold())


def _get_crop(db: Any, crop_id: str) -> Crop:
    snapshot = db.collection("crops").document(crop_id).get()
    return _crop_from_snapshot(snapshot)


def _crop_data(crop: Crop) -> dict[str, Any]:
    return crop.model_dump(by_alias=True, exclude_none=True)


def _enrich_plot(plot_data: dict[str, Any], crops_by_name: dict[str, Crop]) -> dict[str, Any]:
    enriched = dict(plot_data)
    crop = crops_by_name.get(str(enriched.get("cropType", "")))
    if crop is None:
        crop_id = enriched.get("cropId")
        if isinstance(crop_id, str):
            crop = next((item for item in crops_by_name.values() if item.id == crop_id), None)
    if crop is not None:
        enriched.setdefault("cropId", crop.id)
        enriched.setdefault("cropType", crop.name)
        enriched.setdefault("cropIcon", crop.icon)
        enriched.setdefault("thresholds", crop.model_dump(by_alias=True)["thresholds"])
    return enriched


def _farm_from_snapshot(snapshot: Any, crops_by_name: dict[str, Crop]) -> dict[str, Any]:
    farm_data = snapshot.to_dict() or {}
    plots = farm_data.get("plots", [])
    if not isinstance(plots, list):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"La finca {snapshot.id} tiene una lista de parcelas inválida.",
        )
    return {
        "id": snapshot.id,
        **farm_data,
        "plots": [
            _enrich_plot(plot, crops_by_name)
            for plot in plots
            if isinstance(plot, dict)
        ],
    }


def _get_owned_farm(db: Any, farm_id: str, user_id: str) -> dict[str, Any]:
    snapshot = db.collection("farms").document(farm_id).get()
    if not snapshot.exists or (snapshot.to_dict() or {}).get("userId") != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la finca solicitada.",
        )
    crops_by_name = {crop.name: crop for crop in _list_crops(db)}
    return _farm_from_snapshot(snapshot, crops_by_name)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "online", "service": "AgroPulse API", "version": "1.0.0"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/api/crops")
def list_crops(db: Any = Depends(get_firestore)) -> list[dict[str, Any]]:
    return [_crop_data(crop) for crop in _list_crops(db)]


@app.post("/api/recommendations/evaluate", response_model=Recommendation)
def evaluate_recommendation(
    measurement: RecommendationInput,
    db: Any = Depends(get_firestore),
) -> Recommendation:
    crop = _get_crop(db, measurement.crop_id)
    return evaluate_measurement(
        crop.name,
        measurement.humidity,
        measurement.temperature,
        measurement.situation,
        crop.thresholds,
    )


@app.get("/api/farms")
def list_farms(
    user_id: str = Depends(get_current_user_id),
    db: Any = Depends(get_firestore),
) -> list[dict[str, Any]]:
    snapshots = (
        db.collection("farms")
        .where(filter=FieldFilter("userId", "==", user_id))
        .stream()
    )
    crops_by_name = {crop.name: crop for crop in _list_crops(db)}
    farms = [_farm_from_snapshot(snapshot, crops_by_name) for snapshot in snapshots]
    return sorted(farms, key=lambda farm: str(farm.get("name", "")).casefold())


@app.post("/api/farms", status_code=status.HTTP_201_CREATED)
def create_farm(
    farm_input: FarmInput,
    user_id: str = Depends(get_current_user_id),
    db: Any = Depends(get_firestore),
) -> dict[str, Any]:
    farm_ref = db.collection("farms").document()
    farm_data = {
        "name": farm_input.name,
        "location": farm_input.location,
        "userId": user_id,
        "plots": [],
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    farm_ref.set(farm_data)
    return {"id": farm_ref.id, **farm_data}


@app.put("/api/farms/{farm_id}", status_code=status.HTTP_200_OK)
def update_farm(
    farm_id: str,
    farm_input: FarmInput,
    user_id: str = Depends(get_current_user_id),
    db: Any = Depends(get_firestore),
) -> dict[str, Any]:
    farm = _get_owned_farm(db, farm_id, user_id)
    farm_update = {
        "name": farm_input.name,
        "location": farm_input.location,
    }
    db.collection("farms").document(farm_id).update(farm_update)
    updated = db.collection("farms").document(farm_id).get()
    return {"id": updated.id, **updated.to_dict()}


@app.delete("/api/farms/{farm_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_farm(
    farm_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Any = Depends(get_firestore),
) -> None:
    farm = _get_owned_farm(db, farm_id, user_id)
    db.collection("farms").document(farm_id).delete()
    measurements = (
        db.collection("measurements")
        .where(filter=FieldFilter("farmId", "==", farm_id))
        .stream()
    )
    for snapshot in measurements:
        db.collection("measurements").document(snapshot.id).delete()


@app.put(
    "/api/farms/{farm_id}/plots/{plot_id}",
    status_code=status.HTTP_200_OK,
)
def update_plot(
    farm_id: str,
    plot_id: str,
    plot_input: PlotInput,
    user_id: str = Depends(get_current_user_id),
    db: Any = Depends(get_firestore),
) -> dict[str, Any]:
    farm, plot = _get_owned_plot(db, farm_id, plot_id, user_id)
    crop = _get_crop(db, plot_input.crop_id)
    plot.update(
        {
            "name": plot_input.name,
            "cropId": crop.id,
            "cropType": crop.name,
            "cropIcon": crop.icon,
            "thresholds": crop.model_dump(by_alias=True)["thresholds"],
        }
    )
    db.collection("farms").document(farm_id).update(
        {"plots": [p if p.get("id") != plot_id else plot for p in farm["plots"]]}
    )
    farm_updated = _get_owned_farm(db, farm_id, user_id)
    return {"farm": farm_updated, "plot": next(p for p in farm_updated["plots"] if p.get("id") == plot_id)}


@app.delete(
    "/api/farms/{farm_id}/plots/{plot_id}",
)
def delete_plot(
    farm_id: str,
    plot_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Any = Depends(get_firestore),
) -> dict[str, bool]:
    farm, plot = _get_owned_plot(db, farm_id, plot_id, user_id)
    db.collection("farms").document(farm_id).update(
        {"plots": [p for p in farm["plots"] if p.get("id") != plot_id]}
    )
    return {"deleted": True}


@app.post(
    "/api/farms/{farm_id}/plots",
    status_code=status.HTTP_201_CREATED,
)
def create_plot(
    farm_id: str,
    plot_input: PlotInput,
    user_id: str = Depends(get_current_user_id),
    db: Any = Depends(get_firestore),
) -> dict[str, Any]:
    farm = _get_owned_farm(db, farm_id, user_id)
    crop = _get_crop(db, plot_input.crop_id)
    plot = {
        "id": uuid4().hex,
        "name": plot_input.name,
        "cropId": crop.id,
        "cropType": crop.name,
        "cropIcon": crop.icon,
        "thresholds": crop.model_dump(by_alias=True)["thresholds"],
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    db.collection("farms").document(farm_id).update(
        {"plots": firestore.ArrayUnion([plot])}
    )
    return {**farm, "plots": [*farm["plots"], plot]}


@app.get("/api/farms/{farm_id}/plots/{plot_id}")
def get_plot(
    farm_id: str,
    plot_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Any = Depends(get_firestore),
) -> dict[str, Any]:
    farm = _get_owned_farm(db, farm_id, user_id)
    plot = next((item for item in farm["plots"] if item.get("id") == plot_id), None)
    if plot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la parcela solicitada.",
        )
    return {"farm": farm, "plot": plot}


def _get_owned_plot(
    db: Any, farm_id: str, plot_id: str, user_id: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    farm = _get_owned_farm(db, farm_id, user_id)
    plot = next((item for item in farm["plots"] if item.get("id") == plot_id), None)
    if plot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la parcela solicitada.",
        )
    return farm, plot


@app.get("/api/farms/{farm_id}/plots/{plot_id}/measurements")
def list_measurements(
    farm_id: str,
    plot_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Any = Depends(get_firestore),
) -> list[dict[str, Any]]:
    _get_owned_plot(db, farm_id, plot_id, user_id)
    snapshots = (
        db.collection("measurements")
        .where(filter=FieldFilter("userId", "==", user_id))
        .stream()
    )
    measurements = [
        {"id": snapshot.id, **(snapshot.to_dict() or {})}
        for snapshot in snapshots
        if (snapshot.to_dict() or {}).get("farmId") == farm_id
        and (snapshot.to_dict() or {}).get("plotId") == plot_id
    ]
    return sorted(
        measurements,
        key=lambda item: str(item.get("date", "")),
        reverse=True,
    )


@app.post(
    "/api/farms/{farm_id}/plots/{plot_id}/measurements",
    status_code=status.HTTP_201_CREATED,
)
def create_measurement(
    farm_id: str,
    plot_id: str,
    measurement: MeasurementInput,
    user_id: str = Depends(get_current_user_id),
    db: Any = Depends(get_firestore),
) -> dict[str, Any]:
    farm, plot = _get_owned_plot(db, farm_id, plot_id, user_id)
    crop_id = plot.get("cropId")
    if not isinstance(crop_id, str):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La parcela no tiene un cultivo asignado. Vuelve a seleccionarlo.",
        )
    crop = _get_crop(db, crop_id)
    try:
        thresholds = CropThresholds.model_validate(
            plot.get("thresholds", crop.model_dump(by_alias=True)["thresholds"])
        )
    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Los umbrales de la parcela son inválidos.",
        ) from exc

    recommendation = evaluate_measurement(
        crop.name,
        measurement.humidity,
        measurement.temperature,
        measurement.situation,
        thresholds,
    )
    measurement_data = {
        "userId": user_id,
        "farmId": farm_id,
        "plotId": plot_id,
        "farmName": farm["name"],
        "plotName": plot["name"],
        "cropType": crop.name,
        "date": measurement.date,
        "humidity": measurement.humidity,
        "temperature": measurement.temperature,
        "situation": measurement.situation,
        "notes": measurement.notes,
        "recommendation": recommendation.model_dump(by_alias=True),
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    measurement_ref = db.collection("measurements").document()
    measurement_ref.set(measurement_data)
    return {"id": measurement_ref.id, **measurement_data}


@app.delete("/api/measurements/{measurement_id}")
def delete_measurement(
    measurement_id: str,
    user_id: str = Depends(get_current_user_id),
    db: Any = Depends(get_firestore),
) -> dict[str, bool]:
    measurement_ref = db.collection("measurements").document(measurement_id)
    snapshot = measurement_ref.get()
    if not snapshot.exists or (snapshot.to_dict() or {}).get("userId") != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la medición solicitada.",
        )
    measurement_ref.delete()
    return {"deleted": True}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8000")),
        reload=True,
    )
