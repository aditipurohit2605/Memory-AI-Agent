"""
ui/components.py

Small, reusable rendering helpers shared by every page. Nothing in
here talks to the backend - components only ever render data that
is handed to them.
"""

import html

import streamlit as st


def _safe(value) -> str:
    return html.escape(str(value if value is not None else ""))


def page_header(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div class="mai-page-header">
            <div class="mai-page-title">{_safe(title)}</div>
            <div class="mai-page-subtitle">{_safe(subtitle)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def hero_panel(eyebrow: str, title: str, body: str, stats) -> None:
    stat_markup = "".join(
        f"<div class=\"mai-hero-stat\"><strong>{_safe(value)}</strong>"
        f"<span>{_safe(label)}</span></div>"
        for value, label in stats
    )
    st.markdown(
        f"""
        <section class="mai-hero-panel">
            <div class="mai-hero-copy">
                <div class="mai-hero-eyebrow">{_safe(eyebrow)}</div>
                <div class="mai-hero-title">{_safe(title)}</div>
                <div class="mai-hero-body">{_safe(body)}</div>
            </div>
            <div class="mai-hero-stats">{stat_markup}</div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def section_label(text: str) -> None:
    st.markdown(
        f'<div class="mai-sidebar-section-label">{_safe(text)}</div>',
        unsafe_allow_html=True,
    )


def status_row(label: str, ok, unknown: bool = False) -> None:
    """
    ok=True  -> green dot
    ok=False -> red dot
    unknown  -> amber dot (status could not be determined)
    """
    if unknown:
        dot_class = "mai-dot-amber"
    elif ok:
        dot_class = "mai-dot-green"
    else:
        dot_class = "mai-dot-red"

    st.markdown(
        f"""
        <div class="mai-status-row">
            <span class="mai-dot {dot_class}"></span>
            <span>{_safe(label)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(value, label: str) -> None:
    st.markdown(
        f"""
        <div class="mai-metric">
            <div class="mai-metric-value">{_safe(value)}</div>
            <div class="mai-metric-label">{_safe(label)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def info_card(title: str, text: str, meta: str = "") -> None:
    meta_html = f'<div class="mai-card-meta">{_safe(meta)}</div>' if meta else ""
    st.markdown(
        f"""
        <div class="mai-card">
            <div class="mai-card-title">{_safe(title)}</div>
            <div class="mai-card-text">{_safe(text)}</div>
            {meta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def chip_group(items) -> None:
    if not items:
        st.markdown(
            '<span style="color: var(--mai-text-muted); font-size: 0.85rem;">'
            "Nothing here yet.</span>",
            unsafe_allow_html=True,
        )
        return

    chips_html = "".join(f'<span class="mai-chip">{_safe(item)}</span>' for item in items)
    st.markdown(f'<div>{chips_html}</div>', unsafe_allow_html=True)


def empty_state(icon: str, title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="mai-empty-state">
            <div class="mai-empty-icon">{_safe(icon)}</div>
            <div class="mai-empty-title">{_safe(title)}</div>
            <div class="mai-empty-body">{_safe(body)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def indicator_row(indicators) -> None:
    """indicators: list[str] of small text badges rendered under a chat message."""
    if not indicators:
        return
    chips_html = "".join(f'<span class="mai-indicator">{_safe(text)}</span>' for text in indicators)
    st.markdown(f'<div class="mai-indicator-row">{chips_html}</div>', unsafe_allow_html=True)


def friendly_error(message: str) -> None:
    st.error(message)


def backend_unavailable_banner(error_detail: str) -> None:
    st.markdown(
        f"""
        <div class="mai-empty-state">
            <div class="mai-empty-icon">⚠️</div>
            <div class="mai-empty-title">MemoryAI could not connect to its backend</div>
            <div class="mai-empty-body">
                Please make sure <b>Ollama</b> is running and
                <b>Llama 3.2 3B</b> is available, then reload this page.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.expander("Technical details"):
        st.code(error_detail or "No details available.", language="text")
