# FloraCare 🌱

An intelligent, conversational AI assistant for plant enthusiasts and greenhouse managers, powered by Google's Agent Development Kit (ADK) and Gemini 2.5.

![FloraCare Agent Demo](./demo.gif)

---

## 🌟 Overview

**FloraCare** helps users manage indoor plants, track greenhouse inventory, log watering schedules, calculate fertilizer dilution recipes, search local plant nurseries, look up scientific botanical classifications, and generate AI plant previews and videos.

---

## 🛠️ Integrated Google Cloud Services & Capabilities

The codebase connects directly to the following Google Cloud Platform services and tools:

- **Vertex AI Memory Bank Service**: Stores long-term user preferences, plant care history, and allergy/toxicity safety guidelines across sessions.
- **Google Cloud Firestore**: Persists greenhouse plant records, locations, last-watered dates, and care notes.
- **Google Cloud Storage**: Public bucket storage for generated plant images and video assets.
- **Vertex AI Imagen 3 (`gemini-3.1-flash-lite-image`)**: Generates realistic preview images of mature plants, leaf conditions, and planter arrangements.
- **Vertex AI Omni (`gemini-omni-flash-preview`)**: Generates short videos of plants and greenhouse scenes.
- **Agent Engine Sandbox Code Executor**: Runs Python code to calculate precise fertilizer dilution ratios (mL/L and teaspoons) and soil substrate percentages.
- **Google Geocoding & Google Places API**: Converts address locations and searches nearby garden centers, florists, and plant nurseries.
- **A2UI 0.8 Protocol**: Renders structured UI cards (inventory lists, care schedules, image previews) inside the chat interface.
- **Botanical Taxonomy APIs**: Looks up scientific classifications, family, genus, and sunlight requirements via the Perenual API and GBIF (Global Biodiversity Information Facility) API.

---

## 📋 Implemented Agent Tools

| Tool Function | Description | Connected Service |
| :--- | :--- | :--- |
| `list_plants` | Retrieves all greenhouse plant records and status | Google Cloud Firestore |
| `get_plant_details` | Gets detailed care notes for a specific plant | Google Cloud Firestore |
| `add_plant` | Adds a new plant to the greenhouse inventory | Google Cloud Firestore |
| `water_plant` | Logs a watering event and updates last watered timestamp | Google Cloud Firestore |
| `calculate_fertilizer_ratio` | Calculates fertilizer dosage and soil substrate mix | Python Code Execution Sandbox |
| `generate_plant_image` | Generates a high-quality plant preview image | Vertex AI Imagen 3 & Cloud Storage |
| `generate_plant_video` | Generates a short video clip of a plant scene | Vertex AI Omni & Cloud Storage |
| `geocode_address` | Converts address strings into latitude/longitude coordinates | Google Geocoding API |
| `find_nearby_places` | Finds nearby garden centers and plant nurseries | Google Places API (New) |
| `search_plant_taxonomy` | Queries scientific botanical taxonomy and plant data | Perenual & GBIF APIs |
| `get_weather` | Retrieves location weather for watering adjustments | Weather Utility |

---

## 🚧 Planned / Not Yet Implemented

The following features were discussed during initial project planning but are not currently implemented in the codebase:

- **IoT Hardware Sensor Integration**: Live soil moisture sensor readings and automated drip irrigation valve triggers (planned for future hardware expansion).
- **Automated Push Notifications**: Scheduled SMS / Email watering reminders via Cloud Tasks (planned for future release).

---

## 🚀 Local Setup & Execution Instructions

### Prerequisites
- Python 3.10+
- Google Cloud SDK (`gcloud` CLI authenticated to your GCP project)
- Active Google Cloud Project with Firestore, Vertex AI, and Cloud Storage enabled

### 1. Clone & Install Dependencies

```bash
git clone <your-repository-url>
cd floracare
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the project root:

```ini
FIRESTORE_PROJECT=your-gcp-project-id
MEDIA_BUCKET=your-gcs-bucket-name
GOOGLE_MAPS_API_KEY=your-google-maps-api-key
PERENUAL_API_KEY=your-perenual-api-key
```

### 3. Seed Firestore Database

Initialize sample greenhouse plant data in Firestore:

```bash
python seed_db.py
```

### 4. Run the Agent Locally

Start the local Agent Development Kit (ADK) Web interface:

```bash
adk web --app app
```

Or run the FastAPI chat proxy and frontend server:

```bash
cd frontend
python main.py
```

---

## 📂 Project Structure

```
floracare/
├── app/
│   ├── agent.py          # Root agent definition, Memory Bank, and A2UI callbacks
│   ├── tools.py          # Implemented tools (Firestore, Imagen, Omni, Maps, Taxonomy)
│   └── a2ui_utils.py     # A2UI 0.8 card layout callback handler
├── frontend/
│   ├── main.py           # FastAPI backend proxy talking A2A protocol
│   └── static/
│       └── index.html    # Chat UI frontend
├── seed_db.py            # Firestore database seeder
├── demo.gif              # Inline demonstration walkthrough
├── agents-cli-manifest.yaml
└── pyproject.toml
```
