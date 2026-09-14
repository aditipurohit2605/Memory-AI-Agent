"""
ui/system_view.py

Shows the technology stack and real, best-effort connection status.
Status checks are read-only probes against the already-imported
backend (see ui/state.py) - nothing here fakes a green light.
"""

import streamlit as st

from ui import components
from ui.state import check_ollama_status, cloud_mode, get_backend


MODEL_NAME = "llama3.2:3b"

STACK = [
    ("Model", "Llama 3.2 3B"),
    ("LLM Runtime", "Ollama"),
    ("Long-Term Memory", "Mem0"),
    ("Vector Database", "Qdrant"),
    ("Embeddings", "sentence-transformers/all-MiniLM-L6-v2"),
    ("Application", "Streamlit"),
    ("Web Search", "DuckDuckGo (ddgs)"),
    ("Mode", "Local"),
]


def render() -> None:
    components.page_header(
        "⚙️ System",
        "Architecture and live status of MemoryAI's components.",
    )

    if cloud_mode():
        components.info_card("AI provider", "Gemini cloud API")
        components.info_card("Memory backend", "Lightweight cloud memory store")
        components.status_row("Gemini cloud API", ok=True)
        components.status_row("Cloud memory", ok=True)
        st.caption("Cloud mode uses Gemini for responses and a lightweight memory store for this deployment.")
        return

    agent_module, error = get_backend()

    st.markdown('<div class="mai-sidebar-section-label">Technology stack</div>', unsafe_allow_html=True)

    cols = st.columns(2)
    for index, (label, value) in enumerate(STACK):
        with cols[index % 2]:
            components.info_card(label, value)

    st.markdown('<hr class="mai-divider">', unsafe_allow_html=True)

    st.markdown('<div class="mai-sidebar-section-label">Connection status</div>', unsafe_allow_html=True)

    ollama_running, model_available = check_ollama_status(MODEL_NAME)

    components.status_row(
        "Ollama server" + (" — running" if ollama_running else " — not reachable"),
        ok=ollama_running,
    )

    if ollama_running:
        components.status_row(
            f"Model '{MODEL_NAME}'" + (" — available" if model_available else " — not found"),
            ok=bool(model_available),
        )
    else:
        components.status_row(f"Model '{MODEL_NAME}'", ok=False, unknown=True)

    components.status_row(
        "Memory backend (Mem0 + Qdrant)" + (" — connected" if agent_module else " — unavailable"),
        ok=bool(agent_module),
    )

    if not agent_module:
        st.markdown("")
        components.backend_unavailable_banner(error)

    st.markdown('<hr class="mai-divider">', unsafe_allow_html=True)

    st.markdown('<div class="mai-sidebar-section-label">Pipeline</div>', unsafe_allow_html=True)
    st.markdown(
        """
        User message → Plan (direct answer or multi-step) →
        Retrieve relevant long-term memory → Generate response
        (with calculator / web-search tools available) →
        Self-evaluate the response → Extract and save new memory →
        Update profile → Log the interaction → User feedback →
        Learn and personalize future responses.
        """
    )

    st.caption(
        "Tool usage (calculator / web search) happens inside the "
        "existing agent pipeline and isn't currently returned to the "
        "UI, so no per-message tool indicator is shown here — see "
        "README_UI_INTEGRATION.md for the smallest change that would expose it."
    )
