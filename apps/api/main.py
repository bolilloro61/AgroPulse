"""AgroPulse API: crop catalog, recommendations, farms, plots and measurements."""

from __future__ import annotations

import logging
import os
import secrets
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any, Literal
from uuid import uuid4

import firebase_admin
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.api_core.exceptions import AlreadyExists
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
logger = logging.getLogger(__name__)

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


def get_verified_claims(
    token: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict[str, Any]:
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere iniciar sesión.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        claims = firebase_auth.verify_id_token(
            token.credentials,
            app=get_firebase_app(),
            clock_skew_seconds=60,
        )
    except (ValueError, firebase_exceptions.FirebaseError) as exc:
        cause = getattr(exc, "cause", exc.__cause__)
        message = str(exc).lower()
        cause_message = str(cause).lower() if cause else ""
        if 'incorrect "aud"' in message:
            reason = "audience_mismatch"
        elif 'incorrect "iss"' in message:
            reason = "issuer_mismatch"
        elif "incorrect algorithm" in message:
            reason = "algorithm_mismatch"
        elif "used too early" in cause_message:
            reason = "token_issued_in_future"
        elif "token expired" in cause_message:
            reason = "token_expired"
        elif "wrong audience" in cause_message:
            reason = "audience_mismatch"
        elif "key type does not match" in cause_message:
            reason = "certificate_algorithm_mismatch"
        elif "unsupported signature algorithm" in cause_message:
            reason = "unsupported_algorithm"
        elif "no \"kid\"" in message:
            reason = "missing_key_id"
        elif "custom token" in message:
            reason = "custom_token"
        elif "subject" in message:
            reason = "invalid_subject"
        else:
            reason = "invalid_token"
        logger.warning(
            "Firebase ID token verification failed (%s; reason=%s; cause=%s)",
            type(exc).__name__,
            reason,
            type(cause).__name__ if cause else "none",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token de Firebase no es válido o expiró.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
    if not isinstance(claims.get("uid"), str) or not claims["uid"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token no contiene un usuario válido.",
        )
    return claims


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
                    "Firebase no está configurado. Configura Application Default "
                    "Credentials o define FIREBASE_SERVICE_ACCOUNT_PATH/"
                    "GOOGLE_APPLICATION_CREDENTIALS para desarrollo local."
                ),
            ) from exc


def get_firestore() -> Any:
    return firestore.client(get_firebase_app())


def get_current_user_role(
    claims: dict[str, Any] = Depends(get_verified_claims),
    db: Any = Depends(get_firestore),
) -> str:
    role = claims.get("role")
    if role not in {"Gerente", "Trabajador"}:
        role = _get_user_profile(db, str(claims["uid"])).get("role")
    if role not in {"Gerente", "Trabajador"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta no tiene un rol válido asignado.",
        )
    return role


def get_current_user_id(
    claims: dict[str, Any] = Depends(get_verified_claims),
) -> str:
    user_id = claims.get("uid")
    if not isinstance(user_id, str) or not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token no contiene un usuario válido.",
        )
    return user_id


def _get_user_profile(db: Any, user_id: str) -> dict[str, Any]:
    snapshot = db.collection("users").document(user_id).get()
    return snapshot.to_dict() or {} if snapshot.exists else {}


def _require_manager(role: str) -> None:
    if role != "Gerente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Esta operación está disponible solo para gerentes.",
        )


def _require_measurement_edit_permission(
    role: str, user_id: str, measurement: dict[str, Any]
) -> None:
    if (
        role == "Trabajador"
        and measurement.get("createdById", measurement.get("userId")) != user_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la medición solicitada.",
        )


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


class UserRegistrationInput(BaseModel):
    role: Literal["Gerente", "Trabajador"]
    display_name: str = Field(alias="displayName", min_length=1, max_length=100)
    worker_code: str | None = Field(default=None, alias="workerCode", pattern=r"^[0-9]{6}$")

    @field_validator("display_name")
    @classmethod
    def trim_display_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("El nombre no puede estar vacío.")
        return value


class WorkerJoinInput(BaseModel):
    worker_code: str = Field(alias="workerCode", pattern=r"^[0-9]{6}$")


class WorkerAssignmentsInput(BaseModel):
    plot_ids: list[str] = Field(alias="plotIds")

    @field_validator("plot_ids")
    @classmethod
    def unique_plot_ids(cls, value: list[str]) -> list[str]:
        if len(set(value)) != len(value):
            raise ValueError("La lista de parcelas no puede contener duplicados.")
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
        **{
            key: value
            for key, value in farm_data.items()
            if key not in {"workerCode", "userId"}
        },
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


def _new_worker_code(db: Any, farm_id: str) -> str:
    for _ in range(10):
        code = f"{secrets.randbelow(1_000_000):06d}"
        try:
            db.collection("workerCodes").document(code).create({"farmId": farm_id})
            return code
        except AlreadyExists:
            continue
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail="No se pudo generar un código único para la finca.",
    )


def _get_farm_by_worker_code(db: Any, code: str) -> Any:
    code_snapshot = db.collection("workerCodes").document(code).get()
    farm_id = (code_snapshot.to_dict() or {}).get("farmId") if code_snapshot.exists else None
    farm_snapshot = db.collection("farms").document(farm_id).get() if farm_id else None
    if farm_snapshot is None or not farm_snapshot.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El código de finca no es válido.",
        )
    return farm_snapshot


def _get_accessible_farm(
    db: Any, farm_id: str, user_id: str, role: str
) -> dict[str, Any]:
    if role == "Gerente":
        return _get_owned_farm(db, farm_id, user_id)
    profile = _get_user_profile(db, user_id)
    if farm_id not in profile.get("farmIds", []):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la finca solicitada.",
        )
    snapshot = db.collection("farms").document(farm_id).get()
    if not snapshot.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la finca solicitada.",
        )
    crops_by_name = {crop.name: crop for crop in _list_crops(db)}
    return _farm_from_snapshot(snapshot, crops_by_name)


def _get_accessible_plot(
    db: Any, farm_id: str, plot_id: str, user_id: str, role: str
) -> tuple[dict[str, Any], dict[str, Any]]:
    farm = _get_accessible_farm(db, farm_id, user_id, role)
    plot = next((item for item in farm["plots"] if item.get("id") == plot_id), None)
    if plot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la parcela solicitada.",
        )
    if role == "Trabajador":
        assignments = _get_user_profile(db, user_id).get("plotAssignments", {})
        if plot_id not in assignments.get(farm_id, []):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No se encontró la parcela solicitada.",
            )
    return farm, plot


@app.get("/")
def read_root() -> dict[str, str]:
    return {"status": "online", "service": "AgroPulse API", "version": "1.0.0"}


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/api/crops")
def list_crops(db: Any = Depends(get_firestore)) -> list[dict[str, Any]]:
    return [_crop_data(crop) for crop in _list_crops(db)]


@app.post("/api/auth/register")
def register_profile(
    registration: UserRegistrationInput,
    claims: dict[str, Any] = Depends(get_verified_claims),
    db: Any = Depends(get_firestore),
) -> dict[str, Any]:
    user_id = str(claims["uid"])
    profile_ref = db.collection("users").document(user_id)
    existing = profile_ref.get()
    existing_profile = existing.to_dict() or {} if existing.exists else {}
    if existing_profile.get("role") not in (None, registration.role):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="La cuenta ya tiene asignado otro rol.",
        )

    farm_id = None
    farm_ids = list(existing_profile.get("farmIds", []))
    assignments = dict(existing_profile.get("plotAssignments", {}))
    if registration.role == "Trabajador":
        if not registration.worker_code:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Se requiere el código de seis dígitos de una finca.",
            )
        farm_snapshot = _get_farm_by_worker_code(db, registration.worker_code)
        farm_id = farm_snapshot.id
        if farm_id not in farm_ids:
            farm_ids.append(farm_id)
        assignments.setdefault(farm_id, [])
    elif registration.worker_code:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Los gerentes no deben registrar un código de finca.",
        )

    profile = {
        "email": claims.get("email", existing_profile.get("email", "")),
        "displayName": registration.display_name,
        "role": registration.role,
        "farmIds": farm_ids,
        "plotAssignments": assignments,
        "createdAt": existing_profile.get(
            "createdAt", datetime.now(timezone.utc).isoformat()
        ),
    }
    profile_ref.set(profile, merge=True)
    firebase_auth.set_custom_user_claims(user_id, {"role": registration.role})
    return {
        "uid": user_id,
        "email": profile["email"],
        "displayName": profile["displayName"],
        "role": registration.role,
        "farmId": farm_id,
    }


@app.get("/api/auth/profile")
def get_profile(
    claims: dict[str, Any] = Depends(get_verified_claims),
    db: Any = Depends(get_firestore),
) -> dict[str, Any]:
    user_id = str(claims["uid"])
    profile = _get_user_profile(db, user_id)
    role = claims.get("role") or profile.get("role")
    if role not in {"Gerente", "Trabajador"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La cuenta no tiene un rol válido asignado.",
        )
    return {
        "uid": user_id,
        "email": claims.get("email", profile.get("email", "")),
        "displayName": profile.get("displayName", ""),
        "role": role,
    }


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
    role: str = Depends(get_current_user_role),
    db: Any = Depends(get_firestore),
) -> list[dict[str, Any]]:
    if role == "Gerente":
        snapshots = (
            db.collection("farms")
            .where(filter=FieldFilter("userId", "==", user_id))
            .stream()
        )
    else:
        farm_ids = _get_user_profile(db, user_id).get("farmIds", [])
        snapshots = [
            db.collection("farms").document(farm_id).get()
            for farm_id in farm_ids
        ]
    crops_by_name = {crop.name: crop for crop in _list_crops(db)}
    farms = [
        _farm_from_snapshot(snapshot, crops_by_name)
        for snapshot in snapshots
        if snapshot.exists
    ]
    if role == "Trabajador":
        assignments = _get_user_profile(db, user_id).get("plotAssignments", {})
        for farm in farms:
            assigned_plot_ids = assignments.get(farm["id"], [])
            for plot in farm["plots"]:
                plot["assigned"] = plot["id"] in assigned_plot_ids
    return sorted(farms, key=lambda farm: str(farm.get("name", "")).casefold())


@app.post("/api/farms", status_code=status.HTTP_201_CREATED)
def create_farm(
    farm_input: FarmInput,
    user_id: str = Depends(get_current_user_id),
    role: str = Depends(get_current_user_role),
    db: Any = Depends(get_firestore),
) -> dict[str, Any]:
    _require_manager(role)
    farm_ref = db.collection("farms").document()
    farm_data = {
        "name": farm_input.name,
        "location": farm_input.location,
        "userId": user_id,
        "workerCode": _new_worker_code(db, farm_ref.id),
        "plots": [],
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    farm_ref.set(farm_data)
    return {
        "id": farm_ref.id,
        **{
            key: value
            for key, value in farm_data.items()
            if key not in {"workerCode", "userId"}
        },
    }


@app.get("/api/farms/{farm_id}/worker-code")
def get_farm_worker_code(
    farm_id: str,
    user_id: str = Depends(get_current_user_id),
    role: str = Depends(get_current_user_role),
    db: Any = Depends(get_firestore),
) -> dict[str, str]:
    _require_manager(role)
    farm = _get_owned_farm(db, farm_id, user_id)
    farm_ref = db.collection("farms").document(farm_id)
    snapshot = farm_ref.get()
    farm_data = snapshot.to_dict() or {}
    code = farm_data.get("workerCode")
    if not isinstance(code, str) or len(code) != 6 or not code.isascii() or not code.isdigit():
        code = _new_worker_code(db, farm_id)
        farm_ref.update({"workerCode": code})
    return {"code": code}


@app.post("/api/workers/farms", status_code=status.HTTP_200_OK)
def join_farm_with_code(
    join: WorkerJoinInput,
    user_id: str = Depends(get_current_user_id),
    role: str = Depends(get_current_user_role),
    db: Any = Depends(get_firestore),
) -> dict[str, str]:
    if role != "Trabajador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los trabajadores pueden vincular una finca con un código.",
        )
    farm_snapshot = _get_farm_by_worker_code(db, join.worker_code)
    farm_id = farm_snapshot.id
    profile = _get_user_profile(db, user_id)
    if farm_id in profile.get("farmIds", []):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta finca ya está vinculada a tu cuenta.",
        )
    db.collection("users").document(user_id).update(
        {
            "farmIds": firestore.ArrayUnion([farm_id]),
            f"plotAssignments.{farm_id}": [],
        }
    )
    return {"farmId": farm_id, "farmName": (farm_snapshot.to_dict() or {}).get("name", "")}


@app.get("/api/farms/{farm_id}/workers")
def list_farm_workers(
    farm_id: str,
    user_id: str = Depends(get_current_user_id),
    role: str = Depends(get_current_user_role),
    db: Any = Depends(get_firestore),
) -> list[dict[str, Any]]:
    _require_manager(role)
    farm = _get_owned_farm(db, farm_id, user_id)
    workers = (
        db.collection("users")
        .where(filter=FieldFilter("farmIds", "array_contains", farm_id))
        .stream()
    )
    return [
        {
            "uid": snapshot.id,
            "email": profile.get("email", ""),
            "displayName": profile.get("displayName", ""),
            "plotIds": profile.get("plotAssignments", {}).get(farm_id, []),
        }
        for snapshot in workers
        if (profile := snapshot.to_dict() or {}).get("role") == "Trabajador"
        and farm_id in profile.get("farmIds", [])
    ]


@app.put("/api/farms/{farm_id}/workers/{worker_id}/assignments")
def update_worker_assignments(
    farm_id: str,
    worker_id: str,
    assignments: WorkerAssignmentsInput,
    user_id: str = Depends(get_current_user_id),
    role: str = Depends(get_current_user_role),
    db: Any = Depends(get_firestore),
) -> dict[str, list[str]]:
    _require_manager(role)
    farm = _get_owned_farm(db, farm_id, user_id)
    valid_plot_ids = {plot["id"] for plot in farm["plots"]}
    if not set(assignments.plot_ids).issubset(valid_plot_ids):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Solo puedes asignar parcelas pertenecientes a esta finca.",
        )
    worker_ref = db.collection("users").document(worker_id)
    worker_snapshot = worker_ref.get()
    worker = worker_snapshot.to_dict() or {}
    if (
        not worker_snapshot.exists
        or worker.get("role") != "Trabajador"
        or farm_id not in worker.get("farmIds", [])
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró el trabajador en esta finca.",
        )
    worker_ref.update({f"plotAssignments.{farm_id}": assignments.plot_ids})
    return {"plotIds": assignments.plot_ids}


@app.put("/api/farms/{farm_id}", status_code=status.HTTP_200_OK)
def update_farm(
    farm_id: str,
    farm_input: FarmInput,
    user_id: str = Depends(get_current_user_id),
    role: str = Depends(get_current_user_role),
    db: Any = Depends(get_firestore),
) -> dict[str, Any]:
    _require_manager(role)
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
    role: str = Depends(get_current_user_role),
    db: Any = Depends(get_firestore),
) -> None:
    _require_manager(role)
    farm = _get_owned_farm(db, farm_id, user_id)
    farm_ref = db.collection("farms").document(farm_id)
    farm_code = (farm_ref.get().to_dict() or {}).get("workerCode")
    farm_ref.delete()
    if farm_code:
        db.collection("workerCodes").document(farm_code).delete()
    measurements = (
        db.collection("measurements")
        .where(filter=FieldFilter("farmId", "==", farm_id))
        .stream()
    )
    for snapshot in measurements:
        db.collection("measurements").document(snapshot.id).delete()
    workers = (
        db.collection("users")
        .where(filter=FieldFilter("farmIds", "array_contains", farm_id))
        .stream()
    )
    for snapshot in workers:
        profile = snapshot.to_dict() or {}
        farm_ids = [item for item in profile.get("farmIds", []) if item != farm_id]
        assignments = dict(profile.get("plotAssignments", {}))
        assignments.pop(farm_id, None)
        db.collection("users").document(snapshot.id).update(
            {"farmIds": farm_ids, "plotAssignments": assignments}
        )


@app.put(
    "/api/farms/{farm_id}/plots/{plot_id}",
    status_code=status.HTTP_200_OK,
)
def update_plot(
    farm_id: str,
    plot_id: str,
    plot_input: PlotInput,
    user_id: str = Depends(get_current_user_id),
    role: str = Depends(get_current_user_role),
    db: Any = Depends(get_firestore),
) -> dict[str, Any]:
    _require_manager(role)
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
    role: str = Depends(get_current_user_role),
    db: Any = Depends(get_firestore),
) -> dict[str, bool]:
    _require_manager(role)
    farm, plot = _get_owned_plot(db, farm_id, plot_id, user_id)
    db.collection("farms").document(farm_id).update(
        {"plots": [p for p in farm["plots"] if p.get("id") != plot_id]}
    )
    workers = (
        db.collection("users")
        .where(filter=FieldFilter("farmIds", "array_contains", farm_id))
        .stream()
    )
    for snapshot in workers:
        profile = snapshot.to_dict() or {}
        assignments = dict(profile.get("plotAssignments", {}))
        assignments[farm_id] = [
            item for item in assignments.get(farm_id, []) if item != plot_id
        ]
        db.collection("users").document(snapshot.id).update(
            {"plotAssignments": assignments}
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
    role: str = Depends(get_current_user_role),
    db: Any = Depends(get_firestore),
) -> dict[str, Any]:
    _require_manager(role)
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
    role: str = Depends(get_current_user_role),
    db: Any = Depends(get_firestore),
) -> dict[str, Any]:
    farm, plot = _get_accessible_plot(db, farm_id, plot_id, user_id, role)
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
    role: str = Depends(get_current_user_role),
    db: Any = Depends(get_firestore),
) -> list[dict[str, Any]]:
    _get_accessible_plot(db, farm_id, plot_id, user_id, role)
    snapshots = (
        db.collection("measurements")
        .where(filter=FieldFilter("farmId", "==", farm_id))
        .stream()
    )
    measurements = []
    creator_profiles: dict[str, dict[str, Any]] = {}
    for snapshot in snapshots:
        data = snapshot.to_dict() or {}
        if data.get("farmId") != farm_id or data.get("plotId") != plot_id:
            continue
        creator_id = data.get("createdById", data.get("userId", ""))
        data["createdById"] = creator_id
        if creator_id and not data.get("createdByName"):
            if creator_id not in creator_profiles:
                creator_profiles[creator_id] = _get_user_profile(db, creator_id)
            creator_profile = creator_profiles[creator_id]
            data["createdByName"] = (
                creator_profile.get("displayName")
                or str(creator_profile.get("email", "")).split("@", 1)[0]
                or "Usuario anterior"
            )
        measurements.append({"id": snapshot.id, **data})
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
    role: str = Depends(get_current_user_role),
    db: Any = Depends(get_firestore),
) -> dict[str, Any]:
    farm, plot = _get_accessible_plot(db, farm_id, plot_id, user_id, role)
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
    profile = _get_user_profile(db, user_id)
    display_name = (
        profile.get("displayName")
        or str(profile.get("email", "")).split("@", 1)[0]
        or user_id
    )
    measurement_data = {
        "userId": user_id,
        "createdById": user_id,
        "createdByName": display_name,
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


@app.put("/api/farms/{farm_id}/plots/{plot_id}/measurements/{measurement_id}")
def update_measurement(
    farm_id: str,
    plot_id: str,
    measurement_id: str,
    measurement: MeasurementInput,
    user_id: str = Depends(get_current_user_id),
    role: str = Depends(get_current_user_role),
    db: Any = Depends(get_firestore),
) -> dict[str, Any]:
    farm, plot = _get_accessible_plot(db, farm_id, plot_id, user_id, role)
    measurement_ref = db.collection("measurements").document(measurement_id)
    snapshot = measurement_ref.get()
    existing = snapshot.to_dict() or {}
    if (
        not snapshot.exists
        or existing.get("farmId") != farm_id
        or existing.get("plotId") != plot_id
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la medición solicitada.",
        )
    _require_measurement_edit_permission(role, user_id, existing)

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
    creator_id = existing.get("createdById", existing.get("userId", user_id))
    creator_profile = _get_user_profile(db, creator_id)
    measurement_data = {
        "userId": existing.get("userId", existing.get("createdById", user_id)),
        "createdById": creator_id,
        "createdByName": (
            existing.get("createdByName")
            or creator_profile.get("displayName")
            or str(creator_profile.get("email", "")).split("@", 1)[0]
            or "Usuario anterior"
        ),
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
        "createdAt": existing.get("createdAt", datetime.now(timezone.utc).isoformat()),
    }
    measurement_ref.set(measurement_data)
    return {"id": measurement_id, **measurement_data}


@app.delete("/api/measurements/{measurement_id}")
def delete_measurement(
    measurement_id: str,
    user_id: str = Depends(get_current_user_id),
    role: str = Depends(get_current_user_role),
    db: Any = Depends(get_firestore),
) -> dict[str, bool]:
    _require_manager(role)
    measurement_ref = db.collection("measurements").document(measurement_id)
    snapshot = measurement_ref.get()
    measurement = snapshot.to_dict() or {}
    if (
        not snapshot.exists
        or not isinstance(measurement.get("farmId"), str)
        or measurement.get("plotId") is None
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró la medición solicitada.",
        )
    _get_owned_farm(db, measurement["farmId"], user_id)
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
