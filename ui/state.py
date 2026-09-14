"""
ui/state.py

Owns two things only:

1. A cached, safe connection to the EXISTING backend (src/agent.py
   and everything it imports: Mem0, Qdrant, Ollama). This module
   never re-implements backend behaviour - it only imports it.

2. Streamlit session_state initialisation for UI-only state
   (which page is selected, the on-screen chat transcript, etc).

Why a cached loader:
Streamlit re-runs this whole script on every interaction. The
backend's import chain (Mem0 + Qdrant + sentence-transformers)
is expensive, so it must only run once per process. st.cache_resource
guarantees that: the module is imported the first time get_backend()
succeeds, and the same object is reused after that. If the import
fails (e.g. Ollama isn't running yet), the failure is NOT cached,
so the user can fix the issue and retry without restarting Streamlit.
"""

import os
import json
from pathlib import Path
from datetime import datetime

import streamlit as st


CLOUD_MEMORY_FILE = Path(__file__).resolve().parent.parent / "data" / "cloud_memories.json"


def cloud_mode() -> bool:
    return bool(os.getenv("RENDER"))


def get_cloud_memories(user_id: str) -> list[dict]:
    try:
        with CLOUD_MEMORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
        return data.get(user_id, []) if isinstance(data, dict) else []
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_cloud_memory(user_id: str, text: str) -> None:
    CLOUD_MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with CLOUD_MEMORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    records = data.setdefault(user_id, [])
    if any(item.get("memory", "").lower() == text.lower() for item in records):
        return
    records.append({"id": f"cloud-{len(records) + 1}", "memory": text, "created_at": datetime.now().isoformat(timespec="seconds")})
    with CLOUD_MEMORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def delete_cloud_memory(user_id: str, memory_id: str) -> None:
    records = [item for item in get_cloud_memories(user_id) if item.get("id") != memory_id]
    CLOUD_MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with CLOUD_MEMORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data[user_id] = records
    with CLOUD_MEMORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def clear_cloud_memories(user_id: str) -> None:
    CLOUD_MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with CLOUD_MEMORY_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    data[user_id] = []
    with CLOUD_MEMORY_FILE.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def cloud_ai_error() -> str | None:
    """Return a fast configuration error for cloud deployments."""
    if os.getenv("RENDER") and not (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")):
        return (
            "Cloud AI is not configured on Render. Add GEMINI_API_KEY or "
            "GOOGLE_API_KEY in the Render environment variables, then redeploy."
        )
    return None


@st.cache_resource(show_spinner=False)
def _load_backend():
    """
    Import the existing MemoryAI backend exactly once.
    Returns the src.agent module, which already exposes everything
    the UI needs (run_agent, USER_ID, conversation, feedback_system,
    memory helpers, profile helpers, learning-log helpers, ...).
    """
    import src.agent as agent_module
    return agent_module


def get_backend():
    """
    Returns (agent_module, error_message).

    On success: (module, None)
    On failure: (None, "human readable error")

    Never raises - callers can always render a friendly message
    instead of crashing the app.
    """
    try:
        return _load_backend(), None
    except Exception as exc:  # noqa: BLE001 - intentionally broad, see docstring
        return None, str(exc)


def check_ollama_status(model_name: str):
    """
    Lightweight, read-only probe of the local Ollama server.
    Returns (is_running: bool, model_available: bool | None).

    model_available is None if Ollama itself could not be reached,
    since we can't know whether the model is pulled in that case.
    """
    try:
        import ollama

        response = ollama.list()
        models = response.get("models", []) if isinstance(response, dict) else getattr(response, "models", [])

        available_names = []
        for item in models:
            if isinstance(item, dict):
                available_names.extend(
                    name for name in [item.get("name"), item.get("model")] if name
                )
            else:
                for attr in ("name", "model"):
                    name = getattr(item, attr, None)
                    if name:
                        available_names.append(name)

        normalized_target = model_name.strip().lower()
        model_available = any(normalized_target == name.strip().lower() or normalized_target in name.strip().lower() for name in available_names)
        return True, model_available

    except Exception:
        return False, None


def init_session_state() -> None:
    """Initialise UI-only session state. Safe to call on every rerun."""

    defaults = {
        "page": "💬 Chat",
        "chat_history": [],          # list[dict]: role, content, + optional indicators
        "last_feedback_turn": -1,     # index of the turn feedback was last given for
        "feedback_message": None,     # (kind, text) shown once after a feedback action
        "pending_prompt": None,       # prompt selected from the chat starter missions
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
