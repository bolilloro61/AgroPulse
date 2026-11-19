import os
from datetime import datetime, timezone
import firebase_admin
from firebase_admin import credentials, firestore

crops = [
    {
        "id": "tomate-saladette",
        "name": "Tomate Saladette",
        "scientificName": "Solanum lycopersicum",
        "category": "Hortaliza / Solanácea",
        "icon": "🍅",
        "thresholds": {
            "temperature": {
                "min": 18,
                "max": 27,
                "minLetal": 2,
                "maxCrit": 32
            },
            "humidity": {
                "min": 60,
                "max": 80,
                "minCrit": 45,
                "maxCrit": 85
            }
        },
        "description": "Solanácea de clima templado-cálido sumamente vulnerable a las bajas temperaturas y heladas. A 0°C sufre muerte celular irreversible."
    },
    {
        "id": "maiz-grano",
        "name": "Maíz Grano",
        "scientificName": "Zea mays",
        "category": "Cereal / Gramínea",
        "icon": "🌽",
        "thresholds": {
            "temperature": {
                "min": 20,
                "max": 30,
                "minLetal": 0,
                "maxCrit": 35
            },
            "humidity": {
                "min": 50,
                "max": 70,
                "minCrit": 35,
                "maxCrit": 75
            }
        },
        "description": "Gramínea de estación cálida, sensible a sequía en floración y heladas tempranas."
    },
    {
        "id": "aguacate-hass",
        "name": "Aguacate Hass",
        "scientificName": "Persea americana",
        "category": "Frutal perenne",
        "icon": "🥑",
        "thresholds": {
            "temperature": {
                "min": 15,
                "max": 26,
                "minLetal": 0,
                "maxCrit": 32
            },
            "humidity": {
                "min": 55,
                "max": 75,
                "minCrit": 40,
                "maxCrit": 80
            }
        },
        "description": "Árbol frutal con raíces superficiales altamente susceptibles a asfixia radicular y Phytophthora."
    },
    {
        "id": "vid-uva",
        "name": "Vid / Uva",
        "scientificName": "Vitis vinifera",
        "category": "Frutal leñoso",
        "icon": "🍇",
        "thresholds": {
            "temperature": {
                "min": 16,
                "max": 28,
                "minLetal": -1,
                "maxCrit": 35
            },
            "humidity": {
                "min": 40,
                "max": 65,
                "minCrit": 25,
                "maxCrit": 70
            }
        },
        "description": "Cultivo rústico adaptado a menor humedad, vulnerable a heladas tardías en brotación."
    },
    {
        "id": "chile-jalapeno",
        "name": "Chile Jalapeño",
        "scientificName": "Capsicum annuum",
        "category": "Hortaliza / Solanácea",
        "icon": "🌶️",
        "thresholds": {
            "temperature": {
                "min": 18,
                "max": 28,
                "minLetal": 2,
                "maxCrit": 34
            },
            "humidity": {
                "min": 60,
                "max": 75,
                "minCrit": 45,
                "maxCrit": 85
            }
        },
        "description": "Solanácea exigente en calor y humedad moderada; susceptible a flor caída por choque térmico."
    }
]

def seed_crops():
    default_credential_path = os.path.join(
        os.path.dirname(__file__), "..", "firebase", "serviceAccountKey.json"
    )
    credential_path = os.environ.get(
        "GOOGLE_APPLICATION_CREDENTIALS", default_credential_path
    )
    credential_path = os.path.abspath(credential_path)
    if not os.path.isfile(credential_path):
        raise FileNotFoundError(
            "No se encontró el archivo de credenciales. Configura "
            "GOOGLE_APPLICATION_CREDENTIALS o colócalo en firebase/serviceAccountKey.json."
        )

    credential = credentials.Certificate(credential_path)
    firebase_admin.initialize_app(credential)
    db = firestore.client()
    batch = db.batch()
    now = datetime.now(timezone.utc).isoformat()

    print("Iniciando carga de cultivos a Firebase Cloud Firestore...")
    for crop in crops:
        doc_ref = db.collection("crops").document(crop["id"])
        batch.set(doc_ref, {**crop, "updatedAt": now}, merge=True)
        print(f" - Preparando cultivo: {crop['name']} (ID: {crop['id']})")

    batch.commit()
    print("¡Todos los cultivos se subieron exitosamente a la colección 'crops' en Firestore!")


if __name__ == "__main__":
    seed_crops()
