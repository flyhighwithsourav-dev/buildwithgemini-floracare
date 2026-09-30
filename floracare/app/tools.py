import datetime
import json
import os
import subprocess
import urllib.parse
import urllib.request
from typing import Any, Dict, List

from dotenv import load_dotenv
from google import genai
from google.adk.tools import ToolContext
from google.cloud import firestore, storage
from google.genai import types
from google.oauth2.credentials import Credentials

# Load environment variables from .env file
load_dotenv()

# HARDCODED PROJECT ID AND BUCKET NAME - Required for Agent Platform compatibility
# (google.auth.default() inside Agent Platform returns project number, breaking Firestore)
FIRESTORE_PROJECT = "qwiklabs-gcp-02-23618b5bca3a"
MEDIA_BUCKET = "floracare-media-qwiklabs-gcp-02-23618b5bca3a"


def _get_db() -> firestore.Client:
    """Helper to initialize Firestore client with explicit project ID string."""
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


def list_plants() -> List[Dict[str, Any]]:
    """List all plants in the greenhouse garden inventory from Firestore.

    Returns:
        A list of dictionaries containing plant records (id, name, species, location, watering_frequency_days, last_watered, health_status, notes).
    """
    db = _get_db()
    docs = db.collection("plants").stream()
    plants = []
    for doc in docs:
        data = doc.to_dict()
        data["id"] = doc.id
        plants.append(data)
    return plants


def get_plant_details(plant_name_or_id: str) -> str:
    """Get detailed information about a specific plant by name or document ID.

    Args:
        plant_name_or_id: The name or document ID of the plant (e.g. 'monstera-1' or 'Peace Lily').

    Returns:
        A formatted string with the plant details or an error message if not found.
    """
    db = _get_db()
    doc_ref = db.collection("plants").document(plant_name_or_id.lower().replace(" ", "-"))
    doc = doc_ref.get()
    if doc.exists:
        data = doc.to_dict()
        return (
            f"Plant Found: {data.get('name')} (ID: {doc.id})\n"
            f"Species: {data.get('species')}\n"
            f"Location: {data.get('location')}\n"
            f"Watering Frequency: Every {data.get('watering_frequency_days')} days\n"
            f"Last Watered: {data.get('last_watered')}\n"
            f"Health Status: {data.get('health_status')}\n"
            f"Notes: {data.get('notes')}"
        )

    docs = db.collection("plants").stream()
    for d in docs:
        p = d.to_dict()
        if plant_name_or_id.lower() in p.get("name", "").lower() or plant_name_or_id.lower() in d.id.lower():
            return (
                f"Plant Found: {p.get('name')} (ID: {d.id})\n"
                f"Species: {p.get('species')}\n"
                f"Location: {p.get('location')}\n"
                f"Watering Frequency: Every {p.get('watering_frequency_days')} days\n"
                f"Last Watered: {p.get('last_watered')}\n"
                f"Health Status: {p.get('health_status')}\n"
                f"Notes: {p.get('notes')}"
            )

    return f"No plant found matching '{plant_name_or_id}' in the greenhouse inventory."


def add_plant(
    name: str,
    species: str,
    location: str,
    watering_frequency_days: int = 7,
    notes: str = "",
) -> str:
    """Add a new plant to the greenhouse inventory in Firestore.

    Args:
        name: Common name of the plant (e.g. 'Pothos', 'Boston Fern').
        species: Botanical/species name (e.g. 'Epipremnum aureum').
        location: Where the plant is kept (e.g. 'Kitchen Shelf', 'Greenhouse Bench 2').
        watering_frequency_days: Days between waterings (default: 7).
        notes: Special care instructions or notes.

    Returns:
        Confirmation message with the new plant ID.
    """
    db = _get_db()
    doc_id = name.lower().replace(" ", "-") + "-1"
    today_str = datetime.date.today().isoformat()

    plant_data = {
        "id": doc_id,
        "name": name,
        "species": species,
        "location": location,
        "watering_frequency_days": watering_frequency_days,
        "last_watered": today_str,
        "health_status": "Newly Added",
        "notes": notes,
    }

    db.collection("plants").document(doc_id).set(plant_data)
    return f"Successfully added '{name}' (ID: {doc_id}) to Firestore greenhouse inventory."


def water_plant(plant_name_or_id: str) -> str:
    """Log a watering event for a plant, updating its last_watered date to today.

    Args:
        plant_name_or_id: The name or document ID of the plant to water.

    Returns:
        Confirmation message of the updated plant status.
    """
    db = _get_db()
    target_doc = None
    target_id = None

    docs = list(db.collection("plants").stream())
    for d in docs:
        p = d.to_dict()
        if (
            plant_name_or_id.lower() == d.id.lower()
            or plant_name_or_id.lower() in p.get("name", "").lower()
        ):
            target_doc = p
            target_id = d.id
            break

    if not target_id:
        return f"Could not find plant '{plant_name_or_id}' to water."

    today_str = datetime.date.today().isoformat()
    db.collection("plants").document(target_id).update(
        {
            "last_watered": today_str,
            "health_status": "Recently Watered & Hydrated",
        }
    )

    return f"Watered '{target_doc.get('name')}' (ID: {target_id}). Updated last_watered date to {today_str}."


def calculate_fertilizer_ratio(
    water_volume_liters: float,
    fertilizer_type: str = "general",
    growth_stage: str = "maintenance",
) -> str:
    """Calculates fertilizer dilution dosage and soil mix recommendation based on water volume and growth stage.

    Args:
        water_volume_liters: Volume of water to prepare in liters (e.g. 1.0, 2.5).
        fertilizer_type: Type of fertilizer ('general', 'succulent', 'blooming').
        growth_stage: Growth stage ('seedling', 'maintenance', 'active_growth').

    Returns:
        A string summarizing the recommended fertilizer dosage in mL/teaspoons and soil mix recipe.
    """
    rates = {
        "seedling": 1.0,
        "maintenance": 2.5,
        "active_growth": 5.0,
    }
    ml_per_liter = rates.get(growth_stage.lower(), 2.5)

    if fertilizer_type.lower() == "succulent":
        ml_per_liter *= 0.5
    elif fertilizer_type.lower() == "blooming":
        ml_per_liter *= 1.2

    total_ml = round(water_volume_liters * ml_per_liter, 2)
    teaspoons = round(total_ml / 4.92892, 2)

    return (
        f"Fertilizer & Soil Recipe:\n"
        f"- Target Water Volume: {water_volume_liters} L\n"
        f"- Required Dosage: {total_ml} mL (~{teaspoons} tsp) of {fertilizer_type} fertilizer\n"
        f"- Preparation: Mix {total_ml} mL into {water_volume_liters} L of room-temperature water.\n"
        f"- Recommended Soil Substrate Ratio: 60% Potting Soil, 25% Perlite, 15% Orchid Bark."
    )


def search_plant_taxonomy(plant_name: str) -> str:
    """Search botanical taxonomy and scientific classification for a plant species using public APIs.

    Reads PERENUAL_API_KEY from environment variables if present, falling back to the free GBIF Botanical API.

    Args:
        plant_name: Common or scientific plant name (e.g. 'Monstera deliciosa', 'Peace Lily', 'Ficus lyrata').

    Returns:
        A string with official scientific classification (Family, Genus, Species, Kingdom) and taxonomy data.
    """
    api_key = os.getenv("PERENUAL_API_KEY")
    if api_key:
        try:
            url = f"https://perenual.com/api/species-list?key={api_key}&q={urllib.parse.quote(plant_name)}"
            req = urllib.request.Request(url, headers={"User-Agent": "FloraCareAgent/1.0"})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                results = data.get("data", [])
                if results:
                    p = results[0]
                    return (
                        f"Perenual Plant Search Result for '{plant_name}':\n"
                        f"- Scientific Name: {', '.join(p.get('scientific_name', []))}\n"
                        f"- Common Name: {p.get('common_name')}\n"
                        f"- Sunlight: {', '.join(p.get('sunlight', []))}\n"
                        f"- Watering: {p.get('watering')}"
                    )
        except Exception:
            pass

    try:
        url = f"https://api.gbif.org/v1/species/match?name={urllib.parse.quote(plant_name)}"
        req = urllib.request.Request(url, headers={"User-Agent": "FloraCareAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data.get("matchType") != "NONE":
                return (
                    f"GBIF Botanical Taxonomy Result for '{plant_name}':\n"
                    f"- Scientific Name: {data.get('scientificName')}\n"
                    f"- Canonical Name: {data.get('canonicalName')}\n"
                    f"- Family: {data.get('family')}\n"
                    f"- Genus: {data.get('genus')}\n"
                    f"- Kingdom: {data.get('kingdom')} | Order: {data.get('order')}\n"
                    f"- Taxonomic Rank: {data.get('rank')} (Confidence: {data.get('confidence')}%)"
                )
    except Exception as e:
        return f"Error fetching botanical taxonomy for '{plant_name}': {str(e)}"

    return f"No botanical taxonomy matches found for '{plant_name}'."


def geocode_address(address: str) -> str:
    """Uses Google Geocoding API REST endpoint to convert an address string into geographic coordinates.

    Reads GOOGLE_MAPS_API_KEY from environment variables (.env). Falls back to OpenStreetMap Nominatim API if key is restricted.

    Args:
        address: The address or location string to geocode (e.g. '1600 Amphitheatre Pkwy, Mountain View, CA' or 'Seattle').

    Returns:
        A string with formatted address, latitude, and longitude.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if api_key and api_key != "PASTE_KEY_HERE":
        try:
            encoded_address = urllib.parse.quote(address)
            url = f"https://maps.googleapis.com/maps/api/geocode/json?address={encoded_address}&key={api_key}"
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                status = data.get("status")
                if status == "OK" and data.get("results"):
                    result = data["results"][0]
                    formatted_addr = result.get("formatted_address")
                    loc = result.get("geometry", {}).get("location", {})
                    lat = loc.get("lat")
                    lng = loc.get("lng")
                    return (
                        f"Geocoding Result (Google Maps) for '{address}':\n"
                        f"- Formatted Address: {formatted_addr}\n"
                        f"- Location Coordinates: Latitude {lat}, Longitude {lng}"
                    )
        except Exception:
            pass

    # OpenStreetMap Nominatim Fallback
    try:
        encoded_address = urllib.parse.quote(address)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_address}&format=json&limit=1"
        req = urllib.request.Request(url, headers={"User-Agent": "FloraCareAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            if data:
                first = data[0]
                return (
                    f"Geocoding Result for '{address}':\n"
                    f"- Formatted Address: {first.get('display_name')}\n"
                    f"- Location Coordinates: Latitude {first.get('lat')}, Longitude {first.get('lon')}"
                )
    except Exception as e:
        return f"Error geocoding address '{address}': {str(e)}"

    return f"Unable to geocode location '{address}'."


def find_nearby_places(
    latitude: float,
    longitude: float,
    place_type: str = "garden_center",
    radius_meters: float = 5000.0,
) -> str:
    """Uses Google Places API (New) searchNearby REST endpoint to find nearby places of a given type.

    Reads GOOGLE_MAPS_API_KEY from environment variables (.env) and includes required headers (X-Goog-Api-Key, X-Goog-FieldMask).
    Falls back to open places search if key is restricted.

    Args:
        latitude: Center latitude coordinate.
        longitude: Center longitude coordinate.
        place_type: Type of place to search for (e.g. 'garden_center', 'florist', 'park', 'store').
        radius_meters: Search radius in meters (default: 5000.0).

    Returns:
        A string summarizing nearby places found, including name, formatted address, and location coordinates.
    """
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if api_key and api_key != "PASTE_KEY_HERE":
        url = "https://places.googleapis.com/v1/places:searchNearby"
        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": api_key,
            "X-Goog-FieldMask": "places.displayName,places.formattedAddress,places.location",
        }
        payload = {
            "includedTypes": [place_type],
            "maxResultCount": 10,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": latitude, "longitude": longitude},
                    "radius": radius_meters,
                }
            },
        }

        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode())
                places = data.get("places", [])
                if places:
                    results_output = [
                        f"Nearby '{place_type}' Places (Google Places API):"
                    ]
                    for idx, p in enumerate(places, 1):
                        name = p.get("displayName", {}).get("text", "Unknown Name")
                        addr = p.get("formattedAddress", "No address listed")
                        loc = p.get("location", {})
                        lat = loc.get("latitude")
                        lng = loc.get("longitude")
                        results_output.append(
                            f"{idx}. {name}\n"
                            f"   Address: {addr}\n"
                            f"   Location: ({lat}, {lng})"
                        )
                    return "\n".join(results_output)
        except Exception:
            pass

    # Open Places Fallback Search
    try:
        search_query = f"{place_type.replace('_', ' ')} near {latitude},{longitude}"
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={urllib.parse.quote(search_query)}&limit=5"
        req = urllib.request.Request(url, headers={"User-Agent": "FloraCareAgent/1.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            places = json.loads(response.read().decode())
            if not places:
                search_query = f"{place_type.replace('_', ' ')} near Seattle"
                url = f"https://nominatim.openstreetmap.org/search?format=json&q={urllib.parse.quote(search_query)}&limit=5"
                req = urllib.request.Request(url, headers={"User-Agent": "FloraCareAgent/1.0"})
                with urllib.request.urlopen(req, timeout=5) as response:
                    places = json.loads(response.read().decode())

            if places:
                results_output = [
                    f"Nearby '{place_type}' Places Found ({len(places)} items):"
                ]
                for idx, p in enumerate(places, 1):
                    name = p.get("name") or p.get("display_name", "").split(",")[0]
                    addr = p.get("display_name")
                    lat = p.get("lat")
                    lng = p.get("lon")
                    results_output.append(
                        f"{idx}. {name}\n"
                        f"   Address: {addr}\n"
                        f"   Location: ({lat}, {lng})"
                    )
                return "\n".join(results_output)
    except Exception as e:
        return f"Error finding nearby '{place_type}' places: {str(e)}"

    return f"No nearby '{place_type}' places found."


def generate_plant_image(
    prompt: str,
    filename: str = "plant_preview.png",
    tool_context: ToolContext | None = None,
) -> str:
    """Generates an image of a plant, flower, leaf symptom, or greenhouse item based on a descriptive text prompt.

    Uses gemini-3.1-flash-lite-image in the global region. Saves the image as an ADK session artifact and uploads
    the image bytes directly to a public Cloud Storage bucket.

    Args:
        prompt: Detailed descriptive prompt for the image (e.g. 'A lush Monstera deliciosa in a terracotta pot', 'Yellowing peace lily leaves showing chlorosis').
        filename: Filename for the saved image artifact (default: 'plant_preview.png').
        tool_context: ADK ToolContext passed automatically by the framework to save session artifacts.

    Returns:
        A string containing the public Cloud Storage HTTPS URL (https://storage.googleapis.com/<bucket>/<object>) of the generated image.
    """
    client = genai.Client(
        vertexai=True,
        project=FIRESTORE_PROJECT,
        location="global",
    )

    response = client.models.generate_content(
        model="gemini-3.1-flash-lite-image",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["IMAGE"],
        ),
    )

    img_bytes = None
    if response and response.candidates:
        for candidate in response.candidates:
            if candidate.content and candidate.content.parts:
                for part in candidate.content.parts:
                    if part.inline_data and part.inline_data.data:
                        img_bytes = part.inline_data.data
                        break
            if img_bytes:
                break

    if not img_bytes:
        return "Error: Failed to generate image bytes from model."

    # 1. Save with tool_context.save_artifact if available
    if tool_context:
        try:
            artifact_part = types.Part.from_bytes(data=img_bytes, mime_type="image/png")
            tool_context.save_artifact(filename, artifact_part)
        except Exception:
            pass

    # 2. Upload image bytes directly to public GCS bucket
    try:
        storage_client = storage.Client(project=FIRESTORE_PROJECT)
        bucket = storage_client.bucket(MEDIA_BUCKET)

        clean_filename = filename.replace(" ", "_")
        if not clean_filename.endswith(".png") and not clean_filename.endswith(".jpg"):
            clean_filename += ".png"

        blob = bucket.blob(f"generated_images/{clean_filename}")
        blob.upload_from_string(img_bytes, content_type="image/png")

        public_url = f"https://storage.googleapis.com/{MEDIA_BUCKET}/{blob.name}"
        return public_url
    except Exception as e:
        return f"Error uploading image bytes to Cloud Storage: {str(e)}"


def generate_plant_video(
    prompt: str,
    filename: str = "plant_video.mp4",
    tool_context: ToolContext | None = None,
) -> str:
    """Generates a short video of a plant, flower, greenhouse scene, or gardening activity using Google's Omni model (gemini-omni-flash-preview) in the global region.

    Saves the generated video as an ADK session artifact (so it appears in the Playground's Artifacts panel) and
    uploads the video bytes to a public Cloud Storage bucket, returning its public HTTPS URL.

    Args:
        prompt: Detailed description of the video to generate (e.g. 'A 5-second video of a lush Monstera plant swaying in a greenhouse breeze', 'Water drops falling on fresh basil leaves').
        filename: Filename for the saved video artifact (default: 'plant_video.mp4').
        tool_context: ADK ToolContext passed automatically by the framework to save session artifacts.

    Returns:
        A string containing the public Cloud Storage HTTPS URL (https://storage.googleapis.com/<bucket>/<object>) of the generated video.
    """
    client = genai.Client(
        vertexai=True,
        project=FIRESTORE_PROJECT,
        location="global",
    )

    clean_filename = filename.replace(" ", "_")
    if not clean_filename.endswith(".mp4"):
        clean_filename += ".mp4"

    try:
        interaction = client.interactions.create(
            model="gemini-omni-flash-preview",
            input=[{"type": "text", "text": prompt}],
            response_format=[{
                "type": "video",
                "delivery": "uri",
                "gcs_uri": f"gs://{MEDIA_BUCKET}/generated_videos/"
            }]
        )
    except Exception as e:
        return f"Error triggering video generation interaction: {str(e)}"

    gcs_uri = None
    if hasattr(interaction, "output_video") and interaction.output_video and getattr(interaction.output_video, "uri", None):
        gcs_uri = interaction.output_video.uri
    elif hasattr(interaction, "steps"):
        for step in getattr(interaction, "steps", []):
            if hasattr(step, "content") and step.content:
                for item in step.content:
                    if hasattr(item, "uri") and item.uri:
                        gcs_uri = item.uri
                        break

    if not gcs_uri:
        return "Error: Video generation interaction did not return a valid Cloud Storage URI."

    # Download video bytes directly from Cloud Storage bucket (no local disk files)
    blob_name = gcs_uri.replace(f"gs://{MEDIA_BUCKET}/", "")
    try:
        storage_client = storage.Client(project=FIRESTORE_PROJECT)
        bucket = storage_client.bucket(MEDIA_BUCKET)
        blob = bucket.blob(blob_name)
        video_bytes = blob.download_as_bytes()

        # 1. Save with tool_context.save_artifact if available
        if tool_context:
            try:
                artifact_part = types.Part.from_bytes(data=video_bytes, mime_type="video/mp4")
                tool_context.save_artifact(clean_filename, artifact_part)
            except Exception:
                pass

        public_url = f"https://storage.googleapis.com/{MEDIA_BUCKET}/{blob_name}"
        return public_url
    except Exception as e:
        return f"Error downloading or processing video artifact: {str(e)}"

