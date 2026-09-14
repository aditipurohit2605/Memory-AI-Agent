"""
app.py

MemoryAI - Streamlit UI entry point.

This file, and everything under ui/, is the ONLY new code added to
the project. Nothing under src/ is imported except through the
public functions src/agent.py already exposes (see ui/state.py).
"""

import os

import streamlit as st

from ui import chat, components, learning_view, memory_view, profile_view, system_view
from ui.state import check_ollama_status, get_backend, init_session_state
from ui.styles import apply_custom_css


PAGES = {
    "💬 Chat": chat,
    "🧠 Memory": memory_view,
    "👤 Profile": profile_view,
    "📈 Learning": learning_view,
    "⚙️ System": system_view,
}

MODEL_NAME = "llama3.2:3b"


def configure_runtime() -> None:
    """Load deployment-only connection settings before backend imports.

    Streamlit raises StreamlitSecretNotFoundError when no secrets.toml exists,
    which is normal in Render when environment variables are used instead.
    """
    os.environ.setdefault("PORT", "8501")

    ollama_host = os.getenv("OLLAMA_HOST")

    try:
        secret_host = st.secrets.get("OLLAMA_HOST")
    except Exception:
        secret_host = None

    if secret_host:
        ollama_host = str(secret_host).rstrip("/")

    if ollama_host:
        os.environ["OLLAMA_HOST"] = str(ollama_host).rstrip("/")

    if os.getenv("RENDER"):
        os.environ.setdefault("MEMORYAI_LLM_PROVIDER", "gemini")
        os.environ.setdefault("GEMINI_MODEL", "gemini-3.6-flash")


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div class="mai-brand">
                <div class="mai-brand-title">🧠 MemoryAI</div>
                <div class="mai-brand-subtitle">Self-Learning AI Agent</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        selected = st.radio(
            "Navigation",
            list(PAGES.keys()),
            index=list(PAGES.keys()).index(st.session_state.page)
            if st.session_state.page in PAGES else 0,
            label_visibility="collapsed",
        )
        st.session_state.page = selected

        st.markdown('<div class="mai-sidebar-section-label">System</div>', unsafe_allow_html=True)

        components.status_row(
            "Memory backend (loads when needed)",
            ok=False,
            unknown=True,
        )
        ollama_running, model_available = check_ollama_status(MODEL_NAME)

        components.status_row(
            "Local AI (Ollama)",
            ok=bool(ollama_running and model_available),
            unknown=not ollama_running,
        )


def main() -> None:
    configure_runtime()

    st.set_page_config(
        page_title="MemoryAI",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    apply_custom_css()
    init_session_state()
    render_sidebar()

    page_module = PAGES.get(st.session_state.page, chat)
    page_module.render()


if __name__ == "__main__":
    main()
