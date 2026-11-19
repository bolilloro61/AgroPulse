import unittest

from fastapi.testclient import TestClient

from main import app, get_firestore
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


if __name__ == "__main__":
    unittest.main()
