# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
import json
from pathlib import Path
from zoneinfo import ZoneInfo

from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.manager import A2uiSchemaManager
from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.code_executors import AgentEngineSandboxCodeExecutor
from google.adk.memory.vertex_ai_memory_bank_service import VertexAiMemoryBankService
from google.adk.models import Gemini
from google.adk.tools.preload_memory_tool import PreloadMemoryTool
from google.genai import types

from app.a2ui_utils import a2ui_callback
from app.tools import (
    add_plant,
    calculate_fertilizer_ratio,
    find_nearby_places,
    generate_plant_image,
    generate_plant_video,
    geocode_address,
    get_plant_details,
    list_plants,
    search_plant_taxonomy,
    water_plant,
)

# Load remote_agent_runtime_id / Memory Bank ID from deployment_metadata.json
deployment_metadata_file = (
    Path(__file__).parent.parent / "deployment_metadata.json"
)
remote_agent_runtime_id = None
if deployment_metadata_file.exists():
    try:
        with open(deployment_metadata_file, "r") as f:
            metadata = json.load(f)
            remote_agent_runtime_id = metadata.get("remote_agent_runtime_id")
    except Exception:
        pass

if not remote_agent_runtime_id:
    remote_agent_runtime_id = (
        "projects/1016486577645/locations/us-east1/reasoningEngines/6974367181727334400"
    )

memory_bank_id = remote_agent_runtime_id.split("/")[-1]

code_executor = AgentEngineSandboxCodeExecutor(
    agent_engine_resource_name=remote_agent_runtime_id
)


def get_memory_service():
    """Builds VertexAiMemoryBankService for Cloud Run / Agent Runtime deployments."""
    return VertexAiMemoryBankService(
        project="qwiklabs-gcp-02-23618b5bca3a",
        location="us-east1",
        agent_engine_id=memory_bank_id,
    )


# WRITE: after each turn, send the session to Memory Bank for extraction.
async def generate_memories_callback(callback_context: CallbackContext):
    await callback_context.add_session_to_memory()
    return None


def get_weather(query: str) -> str:
    """Simulates weather info for greenhouse temperature and humidity planning.

    Args:
        query: A string containing the location to get weather information for.

    Returns:
        A string with weather information for the queried location.
    """
    if "sf" in query.lower() or "san francisco" in query.lower():
        return "It's 60 degrees and foggy."
    return "It's 90 degrees and sunny."


# Build A2UI 0.8 system prompt
schema_manager = A2uiSchemaManager(
    version="0.8",
    catalogs=[BasicCatalog.get_config("0.8")],
)

instruction = schema_manager.generate_system_prompt(
    role_description=(
        "You are FloraCare, an expert plant care & greenhouse assistant. "
        "You help users manage indoor plants, greenhouse inventory, watering schedules, fertilizer recipes, local plant nursery searches, plant image generation, short plant video generation, and custom calculations via Python code execution. "
        "IMPORTANT MEMORY INSTRUCTION: You MUST remember and track all user allergies, sensitivities, health conditions, or pet toxicities mentioned across sessions. "
        "Always tailor your advice, plant recommendations, fertilizer selections, and care tips to respect the user's recorded allergies and safety preferences."
    ),
    workflow_description="Analyze the request and return structured UI when appropriate.",
    ui_description=(
        "Keep every surface tiny and flat: ONE Card > ONE Column > a few Text rows. "
        "Never nest a Card inside a Card. "
        "Use ONLY these components: Card, Column, Row, Text, and Image. Do not use "
        "Table or Heading (unsupported), or Buttons, actions, or forms (they do "
        "nothing in adk web). "
        "You may include one Image component, but only when you have a public https "
        "URL for the image (for example the URL an image tool returns after uploading "
        "to a public bucket). Set the Image url to that exact https link, for example "
        '{"Image": {"url": {"literalString": "https://..."}}}. Never point an '
        "Image at a bare filename, an artifact name, or a non-http(s) path. If you do "
        "not have a public URL, add a short Text line noting the image instead. "
        "No markdown in text; use the usageHint property ('h1', 'h2', 'body') for "
        "headings and emphasis. "
        "Output ONLY the raw A2UI JSON array — no prose, and never wrap it in "
        "<a2a_datapart_json> tags or 'kind'/'data'/'metadata' objects."
    ),
    include_schema=True,
    include_examples=True,
)


root_agent = Agent(
    name="root_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    code_executor=code_executor,
    instruction=instruction,
    tools=[
        PreloadMemoryTool(),
        list_plants,
        get_plant_details,
        add_plant,
        water_plant,
        calculate_fertilizer_ratio,
        search_plant_taxonomy,
        geocode_address,
        find_nearby_places,
        generate_plant_image,
        generate_plant_video,
        get_weather,
    ],

    after_agent_callback=generate_memories_callback,
    after_model_callback=a2ui_callback,
)

app = App(
    root_agent=root_agent,
    name="app",
)
