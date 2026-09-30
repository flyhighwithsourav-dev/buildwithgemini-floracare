import os
import subprocess
import google.auth
from google.cloud import firestore
from google.oauth2.credentials import Credentials

# HARDCODED PROJECT ID - Required for Agent Platform / Agent Engine compatibility
FIRESTORE_PROJECT = "qwiklabs-gcp-02-23618b5bca3a"


def get_firestore_client() -> firestore.Client:
    """Returns a Firestore client initialized with the hardcoded project ID."""
    try:
        token = subprocess.check_output(
            ["gcloud", "auth", "print-access-token"], text=True
        ).strip()
        if token:
            return firestore.Client(
                project=FIRESTORE_PROJECT, credentials=Credentials(token)
            )
    except Exception:
        pass
    return firestore.Client(project=FIRESTORE_PROJECT)


def seed_database():
    db = get_firestore_client()
    plants_ref = db.collection("plants")

    initial_plants = [
        {
            "id": "monstera-1",
            "name": "Monstera Deliciosa",
            "species": "Monstera deliciosa",
            "location": "Living Room South Window",
            "watering_frequency_days": 7,
            "last_watered": "2026-09-24",
            "health_status": "Healthy",
            "notes": "Prefers indirect bright light. Wipe leaves weekly.",
        },
        {
            "id": "peace-lily-1",
            "name": "Peace Lily",
            "species": "Spathiphyllum",
            "location": "Greenhouse Section A",
            "watering_frequency_days": 4,
            "last_watered": "2026-09-28",
            "health_status": "Moist & Thriving",
            "notes": "Sensitive to tap water chemicals. Use filtered or rainwater.",
        },
        {
            "id": "snake-plant-1",
            "name": "Snake Plant",
            "species": "Sansevieria trifasciata",
            "location": "Office Desk",
            "watering_frequency_days": 14,
            "last_watered": "2026-09-15",
            "health_status": "Low Maintenance",
            "notes": "Drought tolerant. Allow soil to dry completely between waterings.",
        },
        {
            "id": "fiddle-leaf-1",
            "name": "Fiddle Leaf Fig",
            "species": "Ficus lyrata",
            "location": "Sunroom East",
            "watering_frequency_days": 10,
            "last_watered": "2026-09-20",
            "health_status": "Needs Misting",
            "notes": "Keep away from cold drafts. Rotate 90 degrees monthly for even growth.",
        },
    ]

    print(f"Seeding Firestore collection 'plants' in project '{FIRESTORE_PROJECT}'...")
    for plant in initial_plants:
        doc_id = plant["id"]
        plants_ref.document(doc_id).set(plant)
        print(f"  - Seeded plant: {plant['name']} (ID: {doc_id})")

    print("Database seeding completed successfully!")


if __name__ == "__main__":
    seed_database()
