import unittest

from fastapi.testclient import TestClient

from fastapi import HTTPException

from main import (
    app,
    get_current_user_id,
    get_current_user_role,
    get_firestore,
    _require_measurement_edit_permission,
)
from recommendations import CropThresholds, evaluate_measurement


THRESHOLDS = CropThresholds.model_validate(
    {
        "temperature": {"min": 18, "max": 27, "minLetal": 2, "maxCrit": 32},
        "humidity": {"min": 60, "max": 80, "minCrit": 45, "maxCrit": 85},
    }
)


class FakeDocument:
    def __init__(self, document_id: str, data: dict[str, object]) -> None:
        self.id = document_id
        self._data = data
        self.exists = True

    def get(self) -> "FakeDocument":
        return self

    def to_dict(self) -> dict[str, object]:
        return self._data


class FakeCollection:
    def __init__(self, documents: dict[str, dict[str, object]]) -> None:
        self.documents = documents

    def stream(self) -> list[FakeDocument]:
        return [
            FakeDocument(document_id, data)
            for document_id, data in self.documents.items()
        ]

    def document(self, document_id: str) -> FakeDocument:
        return FakeDocument(document_id, self.documents[document_id])


class FakeFirestore:
    def collection(self, collection_name: str) -> FakeCollection:
        if collection_name != "crops":
            raise AssertionError(f"Unexpected collection: {collection_name}")
        return FakeCollection(
            {
                "tomate-saladette": {
                    "name": "Tomate Saladette",
                    "icon": "🍅",
                    "thresholds": THRESHOLDS.model_dump(by_alias=True),
                }
            }
        )


class AccessSnapshot:
    def __init__(self, document_id: str, data: dict[str, object] | None) -> None:
        self.id = document_id
        self._data = data
        self.exists = data is not None

    def get(self) -> "AccessSnapshot":
        return self

    def to_dict(self) -> dict[str, object] | None:
        return self._data


class AccessCollection:
    def __init__(self, documents: dict[str, dict[str, object]]) -> None:
        self.documents = documents

    def document(self, document_id: str) -> AccessSnapshot:
        return AccessSnapshot(document_id, self.documents.get(document_id))

    def stream(self) -> list[AccessSnapshot]:
        return [
            AccessSnapshot(document_id, data)
            for document_id, data in self.documents.items()
        ]


class AccessFirestore:
    def __init__(self, assigned_plot_ids: list[str]) -> None:
        self.collections = {
            "users": {
                "worker-1": {
                    "role": "Trabajador",
                    "farmIds": ["farm-1"],
                    "plotAssignments": {"farm-1": assigned_plot_ids},
                }
            },
            "farms": {
                "farm-1": {
                    "userId": "manager-1",
                    "workerCode": "314159",
                    "name": "Finca de prueba",
                    "location": "Sector norte",
                    "plots": [
                        {
                            "id": "plot-1",
                            "name": "Lote 1",
                            "cropId": "tomate-saladette",
                            "cropType": "Tomate Saladette",
                        }
                    ],
                }
            },
            "crops": {
                "tomate-saladette": {
                    "name": "Tomate Saladette",
                    "icon": "🍅",
                    "thresholds": THRESHOLDS.model_dump(by_alias=True),
                }
            },
        }

    def collection(self, collection_name: str) -> AccessCollection:
        return AccessCollection(self.collections.get(collection_name, {}))


class RecommendationTests(unittest.TestCase):
    def test_api_evaluates_using_crop_thresholds_from_firestore(self) -> None:
        app.dependency_overrides[get_firestore] = lambda: FakeFirestore()
        try:
            with TestClient(app) as client:
                response = client.post(
                    "/api/recommendations/evaluate",
                    json={
                        "cropId": "tomate-saladette",
                        "humidity": 70,
                        "temperature": 23,
                        "situation": "Condición estable",
                    },
                )
        finally:
            app.dependency_overrides.clear()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["tipo"], "optimo")

    def test_lethal_temperature_takes_priority(self) -> None:
        result = evaluate_measurement("Tomate Saladette", 70, 2, "Condición estable", THRESHOLDS)

        self.assertEqual(result.tipo, "helada")
        self.assertEqual(result.nivel, "Emergencia por Helada")

    def test_sudden_humidity_drop_is_critical_even_inside_optimal_range(self) -> None:
        result = evaluate_measurement(
            "Tomate Saladette", 70, 23, "Caída brusca de humedad (-15%)", THRESHOLDS
        )

        self.assertEqual(result.tipo, "critico")

    def test_high_humidity_recommends_drainage_and_pausing_irrigation(self) -> None:
        result = evaluate_measurement("Tomate Saladette", 81, 23, "Condición estable", THRESHOLDS)

        self.assertEqual(result.nivel, "Precaución por Sobresaturación")
        self.assertIn("drenaje", result.accion)

    def test_values_inside_crop_thresholds_are_optimal(self) -> None:
        result = evaluate_measurement("Tomate Saladette", 70, 23, "Condición estable", THRESHOLDS)

        self.assertEqual(result.tipo, "optimo")


class AccessControlTests(unittest.TestCase):
    def _get_plot(self, assigned_plot_ids: list[str]):
        app.dependency_overrides[get_current_user_id] = lambda: "worker-1"
        app.dependency_overrides[get_current_user_role] = lambda: "Trabajador"
        app.dependency_overrides[get_firestore] = lambda: AccessFirestore(assigned_plot_ids)
        try:
            with TestClient(app) as client:
                return client.get("/api/farms/farm-1/plots/plot-1")
        finally:
            app.dependency_overrides.clear()

    def test_worker_can_open_assigned_plot(self) -> None:
        response = self._get_plot(["plot-1"])
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["plot"]["id"], "plot-1")

    def test_worker_cannot_open_unassigned_plot(self) -> None:
        response = self._get_plot([])
        self.assertEqual(response.status_code, 404)

    def test_worker_can_see_farm_and_all_plot_names_without_access_to_all_measurements(self) -> None:
        app.dependency_overrides[get_current_user_id] = lambda: "worker-1"
        app.dependency_overrides[get_current_user_role] = lambda: "Trabajador"
        app.dependency_overrides[get_firestore] = lambda: AccessFirestore([])
        try:
            with TestClient(app) as client:
                response = client.get("/api/farms")
        finally:
            app.dependency_overrides.clear()

        self.assertEqual(response.status_code, 200)
        farm = response.json()[0]
        self.assertEqual(farm["plots"][0]["id"], "plot-1")
        self.assertFalse(farm["plots"][0]["assigned"])
        self.assertNotIn("workerCode", farm)
        self.assertNotIn("userId", farm)

    def test_worker_cannot_create_a_farm(self) -> None:
        app.dependency_overrides[get_current_user_id] = lambda: "worker-1"
        app.dependency_overrides[get_current_user_role] = lambda: "Trabajador"
        app.dependency_overrides[get_firestore] = lambda: AccessFirestore([])
        try:
            with TestClient(app) as client:
                response = client.post(
                    "/api/farms",
                    json={"name": "Finca ajena", "location": "Sector norte"},
                )
        finally:
            app.dependency_overrides.clear()

        self.assertEqual(response.status_code, 403)

    def test_worker_cannot_delete_measurements(self) -> None:
        app.dependency_overrides[get_current_user_id] = lambda: "worker-1"
        app.dependency_overrides[get_current_user_role] = lambda: "Trabajador"
        app.dependency_overrides[get_firestore] = lambda: AccessFirestore([])
        try:
            with TestClient(app) as client:
                response = client.delete("/api/measurements/measurement-1")
        finally:
            app.dependency_overrides.clear()

        self.assertEqual(response.status_code, 403)

    def test_manager_cannot_assign_a_plot_from_another_farm(self) -> None:
        app.dependency_overrides[get_current_user_id] = lambda: "manager-1"
        app.dependency_overrides[get_current_user_role] = lambda: "Gerente"
        app.dependency_overrides[get_firestore] = lambda: AccessFirestore([])
        try:
            with TestClient(app) as client:
                response = client.put(
                    "/api/farms/farm-1/workers/worker-1/assignments",
                    json={"plotIds": ["foreign-plot"]},
                )
        finally:
            app.dependency_overrides.clear()

        self.assertEqual(response.status_code, 422)

    def test_worker_cannot_edit_another_workers_measurement(self) -> None:
        with self.assertRaises(HTTPException) as raised:
            _require_measurement_edit_permission(
                "Trabajador", "worker-1", {"createdById": "worker-2"}
            )
        self.assertEqual(raised.exception.status_code, 404)

    def test_manager_can_edit_measurement_created_by_worker(self) -> None:
        _require_measurement_edit_permission(
            "Gerente", "manager-1", {"createdById": "worker-1"}
        )


if __name__ == "__main__":
    unittest.main()
