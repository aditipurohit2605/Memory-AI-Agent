"""
ui/styles.py

Custom CSS injected on top of Streamlit's built-in dark theme
(see .streamlit/config.toml). Everything here is pure styling -
no backend logic lives in this file.
"""

import streamlit as st


CUSTOM_CSS = """
<style>

:root {
    --mai-bg: #0B1115;
    --mai-surface: rgba(20, 31, 35, 0.88);
    --mai-surface-2: #17262A;
    --mai-border: rgba(151, 189, 181, 0.18);
    --mai-text: #EDF4EF;
    --mai-text-muted: #9AADA7;
    --mai-accent: #72D6BF;
    --mai-accent-soft: rgba(114, 214, 191, 0.12);
    --mai-green: #74DB9A;
    --mai-red: #FF7D7D;
    --mai-amber: #F2C879;
    --mai-radius: 12px;
}

/* Tighten default Streamlit padding for a denser dashboard feel */
.block-container {
    padding-top: 2.5rem;
    padding-bottom: 3rem;
    max-width: 1180px;
}

.stApp {
    background:
        radial-gradient(circle at 85% 0%, rgba(114, 214, 191, 0.11), transparent 28rem),
        radial-gradient(circle at 0% 100%, rgba(255, 154, 118, 0.07), transparent 24rem),
        var(--mai-bg);
    color: var(--mai-text);
    font-family: "Avenir Next", "Segoe UI", sans-serif;
}

.stApp::before {
    content: "";
    display: block;
    height: 3px;
    background: linear-gradient(90deg, var(--mai-accent), #FF9A76);
    position: fixed;
    inset: 0 0 auto 0;
    z-index: 999;
}

section[data-testid="stSidebar"] {
    background: rgba(9, 18, 21, 0.96);
    border-right: 1px solid var(--mai-border);
}

/* Hide the default Streamlit chrome we don't want */
#MainMenu, footer { visibility: hidden; }

/* ---------------------------------------------------------- */
/* Sidebar branding                                            */
/* ---------------------------------------------------------- */

.mai-brand {
    display: flex;
    flex-direction: column;
    gap: 2px;
    padding: 0.25rem 0 1rem 0;
    border-bottom: 1px solid var(--mai-border);
    margin-bottom: 1rem;
}

.mai-brand-title {
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--mai-text);
    letter-spacing: -0.01em;
}

.mai-brand-subtitle {
    font-size: 0.8rem;
    color: var(--mai-text-muted);
}

.mai-sidebar-section-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    color: var(--mai-text-muted);
    text-transform: uppercase;
    margin: 1rem 0 0.5rem 0;
}

/* ---------------------------------------------------------- */
/* Status badges (used in sidebar + System page)               */
/* ---------------------------------------------------------- */

.mai-status-row {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    color: var(--mai-text);
    padding: 3px 0;
}

.mai-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    flex-shrink: 0;
}

.mai-dot-green { background: var(--mai-green); box-shadow: 0 0 6px rgba(61,220,132,0.6); }
.mai-dot-red { background: var(--mai-red); box-shadow: 0 0 6px rgba(255,107,107,0.6); }
.mai-dot-amber { background: var(--mai-amber); box-shadow: 0 0 6px rgba(245,184,65,0.6); }

/* ---------------------------------------------------------- */
/* Page header                                                  */
/* ---------------------------------------------------------- */

.mai-page-header {
    margin-bottom: 1.75rem;
    padding: 0.25rem 0 1.1rem;
    border-bottom: 1px solid var(--mai-border);
}

.mai-page-title {
    font-size: clamp(1.6rem, 3vw, 2.35rem);
    font-weight: 700;
    color: var(--mai-text);
    margin-bottom: 0.35rem;
}

.mai-page-subtitle {
    font-size: 0.92rem;
    color: var(--mai-text-muted);
}

.mai-hero-panel {
    display: flex;
    justify-content: space-between;
    gap: 2rem;
    padding: 1.6rem 1.7rem;
    margin-bottom: 1.5rem;
    border: 1px solid rgba(114, 214, 191, 0.28);
    border-radius: 16px;
    background:
        linear-gradient(115deg, rgba(30, 71, 68, 0.9), rgba(20, 31, 35, 0.9) 62%),
        var(--mai-surface);
    box-shadow: 0 20px 44px rgba(0, 0, 0, 0.18);
}

.mai-hero-copy { max-width: 630px; }
.mai-hero-eyebrow {
    color: var(--mai-accent);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    margin-bottom: 0.7rem;
}
.mai-hero-title {
    color: var(--mai-text);
    font-size: clamp(1.45rem, 3vw, 2.35rem);
    font-weight: 700;
    line-height: 1.1;
    margin-bottom: 0.7rem;
}
.mai-hero-body { color: var(--mai-text-muted); line-height: 1.55; max-width: 560px; }
.mai-hero-stats { display: flex; align-items: flex-end; gap: 1.4rem; }
.mai-hero-stat { display: flex; flex-direction: column; gap: 0.25rem; min-width: 72px; }
.mai-hero-stat strong { color: var(--mai-text); font-size: 1.35rem; }
.mai-hero-stat span { color: var(--mai-text-muted); font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; }

/* ---------------------------------------------------------- */
/* Cards                                                        */
/* ---------------------------------------------------------- */

.mai-card {
    background: var(--mai-surface);
    border: 1px solid var(--mai-border);
    border-radius: var(--mai-radius);
    padding: 1rem 1.15rem;
    margin-bottom: 0.75rem;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.12);
    transition: border-color 160ms ease, transform 160ms ease;
}

.mai-card:hover {
    border-color: rgba(114, 214, 191, 0.42);
    transform: translateY(-1px);
}

.mai-card-title {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--mai-accent);
    margin-bottom: 6px;
}

.mai-card-text {
    font-size: 0.95rem;
    color: var(--mai-text);
    line-height: 1.5;
}

.mai-card-meta {
    font-size: 0.75rem;
    color: var(--mai-text-muted);
    margin-top: 8px;
}

/* ---------------------------------------------------------- */
/* Metrics grid                                                 */
/* ---------------------------------------------------------- */

.mai-metric {
    background: var(--mai-surface);
    border: 1px solid var(--mai-border);
    border-radius: var(--mai-radius);
    padding: 1.1rem 1rem;
    text-align: left;
}

.mai-metric-value {
    font-size: 1.9rem;
    font-weight: 700;
    color: var(--mai-text);
    line-height: 1.1;
}

.mai-metric-label {
    font-size: 0.78rem;
    color: var(--mai-text-muted);
    margin-top: 4px;
}

/* ---------------------------------------------------------- */
/* Tag / chip                                                    */
/* ---------------------------------------------------------- */

.mai-chip {
    display: inline-block;
    background: var(--mai-accent-soft);
    color: var(--mai-accent);
    border: 1px solid rgba(114,214,191,0.35);
    border-radius: 7px;
    padding: 4px 12px;
    font-size: 0.82rem;
    margin: 0 6px 6px 0;
}

/* ---------------------------------------------------------- */
/* Empty states                                                  */
/* ---------------------------------------------------------- */

.mai-empty-state {
    text-align: center;
    padding: 3rem 1.5rem;
    color: var(--mai-text-muted);
    background: linear-gradient(145deg, rgba(20, 31, 35, 0.94), rgba(14, 25, 28, 0.78));
    border: 1px dashed var(--mai-border);
    border-radius: var(--mai-radius);
}

.mai-empty-icon {
    font-size: 2.2rem;
    margin-bottom: 0.5rem;
}

.mai-empty-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--mai-text);
    margin-bottom: 4px;
}

.mai-empty-body {
    font-size: 0.88rem;
    max-width: 380px;
    margin: 0 auto;
}

/* ---------------------------------------------------------- */
/* Inline indicator row under chat responses                    */
/* ---------------------------------------------------------- */

.mai-indicator-row {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-top: 6px;
    margin-bottom: 4px;
}

.mai-indicator {
    font-size: 0.76rem;
    color: var(--mai-text-muted);
    background: var(--mai-surface-2);
    border: 1px solid var(--mai-border);
    border-radius: 8px;
    padding: 3px 9px;
}

/* ---------------------------------------------------------- */
/* Section divider                                               */
/* ---------------------------------------------------------- */

.mai-divider {
    border: none;
    border-top: 1px solid var(--mai-border);
    margin: 1.25rem 0;
}

div[data-testid="stChatMessage"] {
    border: 1px solid transparent;
    border-radius: var(--mai-radius);
    padding: 0.6rem 0.8rem;
    transition: background 160ms ease, border-color 160ms ease;
}

div[data-testid="stChatMessage"]:hover {
    background: rgba(114, 214, 191, 0.035);
    border-color: var(--mai-border);
}

div[data-testid="stChatInput"] {
    border-color: rgba(114, 214, 191, 0.4);
}

@media (max-width: 700px) {
    .block-container { padding: 1.4rem 1rem 2rem; }
    .mai-page-title { font-size: 1.7rem; }
    .mai-metric { padding: 0.85rem 0.75rem; }
    .mai-metric-value { font-size: 1.45rem; }
    .mai-hero-panel { flex-direction: column; gap: 1.25rem; padding: 1.25rem; }
    .mai-hero-stats { gap: 1rem; flex-wrap: wrap; }
}

</style>
"""


def apply_custom_css() -> None:
    """Inject MemoryAI's custom CSS once per render."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
