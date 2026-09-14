"""
ui/memory_view.py

Displays the user's real long-term memories from Mem0 and allows
deletion, using only src.memory's existing functions.

Integration note: memories are stored via memory.add() in
src/agent.py's save_new_memory() with only the plain memory
statement - the category classified by src/memory_extractor.py is
used once (to decide the profile update) and is never persisted
alongside the memory in Mem0. Because of that, per-memory category
labels genuinely don't exist in stored data, and this page does not
invent them. See README_UI_INTEGRATION.md for the smallest backend
change that would make categories persist and displayable.
"""

import streamlit as st

from ui import components
from ui.state import get_backend


def render() -> None:
    components.page_header(
        "🧠 Long-Term Memory",
        "Everything MemoryAI currently remembers about you.",
    )

    agent_module, error = get_backend()

    if not agent_module:
        components.backend_unavailable_banner(error)
        return

    try:
        with st.spinner("Loading memories..."):
            data = agent_module.get_all_memories(agent_module.USER_ID)
        results = data.get("results", []) if isinstance(data, dict) else []
    except Exception as exc:  # noqa: BLE001
        components.friendly_error(
            "MemoryAI could not reach its memory store (Mem0 / Qdrant). "
            "Please make sure the backend is running and try again."
        )
        with st.expander("Technical details"):
            st.code(str(exc), language="text")
        return

    if not results:
        components.empty_state(
            "🧠",
            "No memories yet.",
            "As you interact with MemoryAI, useful information will "
            "automatically be remembered here.",
        )
        return

    search_query = st.text_input(
        "Filter memories",
        placeholder="Type to filter by keyword...",
        label_visibility="collapsed",
    )

    filtered = [
        item for item in results
        if not search_query or search_query.lower() in (item.get("memory") or "").lower()
    ]

    st.caption(
        f"{len(filtered)} of {len(results)} memories"
        if search_query else f"{len(results)} memories stored"
    )

    for item in filtered:
        memory_id = item.get("id", "unknown")
        memory_text = item.get("memory", "")

        card_col, action_col = st.columns([6, 1])
        with card_col:
            components.info_card(
                "Memory",
                memory_text,
                meta=f"ID: {memory_id}",
            )
        with action_col:
            if st.button("🗑️", key=f"delete_{memory_id}", help="Delete this memory"):
                try:
                    agent_module.delete_memory(memory_id)
                    st.toast("Memory deleted.")
                    st.rerun()
                except Exception as exc:  # noqa: BLE001
                    components.friendly_error("Could not delete this memory.")
                    with st.expander("Technical details"):
                        st.code(str(exc), language="text")

    st.markdown('<hr class="mai-divider">', unsafe_allow_html=True)

    with st.expander("Danger zone"):
        st.caption("Permanently delete all long-term memories for this user.")
        confirm = st.checkbox("I understand this cannot be undone.")
        if st.button("Delete all memories", disabled=not confirm, type="primary"):
            try:
                agent_module.delete_all_memories(agent_module.USER_ID)
                st.toast("All memories deleted.")
                st.rerun()
            except Exception as exc:  # noqa: BLE001
                components.friendly_error("Could not delete all memories.")
                with st.expander("Technical details"):
                    st.code(str(exc), language="text")
