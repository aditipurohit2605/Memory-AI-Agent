"""
ui/profile_view.py

Renders the structured profile produced by src.profile's existing
get_user_profile(). No profile fields are invented here - if a
category is empty, it is shown as empty.
"""

import os

import streamlit as st

from ui import components
from ui.state import get_backend


SECTIONS = [
    ("skills", "Skills"),
    ("interests", "Interests"),
    ("goals", "Goals"),
    ("preferences", "Preferences"),
    ("projects", "Projects"),
    ("other", "Other"),
]


def render() -> None:
    components.page_header(
        "👤 User Profile",
        "A structured profile MemoryAI builds from your long-term memories.",
    )

    if os.getenv("RENDER"):
        components.empty_state(
            "👤",
            "Profile is unavailable in cloud mode.",
            "Connect a hosted memory store to build and view a persistent profile on Render.",
        )
        return

    agent_module, error = get_backend()

    if not agent_module:
        components.backend_unavailable_banner(error)
        return

    header_col, action_col = st.columns([5, 1.4])
    with action_col:
        regenerate = st.button("↻ Regenerate", use_container_width=True)

    try:
        with st.spinner("Generating profile from memories..."):
            profile = agent_module.get_user_profile(agent_module.USER_ID)
    except Exception as exc:  # noqa: BLE001
        components.friendly_error("MemoryAI could not generate your profile.")
        with st.expander("Technical details"):
            st.code(str(exc), language="text")
        return

    has_any_data = any(profile.get(key) for key, _ in SECTIONS)

    if not has_any_data:
        components.empty_state(
            "👤",
            "Your profile is still being built.",
            "Continue chatting with MemoryAI - your profile fills in "
            "automatically as it learns about your skills, goals, and preferences.",
        )
        return

    for key, label in SECTIONS:
        items = profile.get(key, [])
        st.markdown(f'<div class="mai-sidebar-section-label">{label}</div>', unsafe_allow_html=True)
        components.chip_group(items)
        st.write("")
