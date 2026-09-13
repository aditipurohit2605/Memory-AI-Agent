"""
ui/learning_view.py

Learning / analytics dashboard, built entirely from
src.learning_log's existing get_learning_summary() and
get_learning_history(). All numbers shown come directly from
data/learning_log.json - nothing here is simulated.
"""

import pandas as pd
import streamlit as st

from ui import components
from ui.state import get_backend


def render() -> None:
    agent_module, error = get_backend()

    components.page_header(
        "📈 Learning Analytics",
        "How MemoryAI is improving from real feedback and self-evaluation.",
    )

    if not agent_module:
        components.backend_unavailable_banner(error)
        return

    try:
        summary = agent_module.get_learning_summary()
        history = agent_module.get_learning_history()
    except Exception as exc:  # noqa: BLE001
        components.friendly_error("MemoryAI could not load the learning log.")
        with st.expander("Technical details"):
            st.code(str(exc), language="text")
        return

    if not history:
        components.empty_state(
            "📈",
            "No learning data yet.",
            "Chat with MemoryAI and give feedback to start building "
            "your learning history.",
        )
        return

    # ---------------------------------------------------------------
    # Metrics
    # ---------------------------------------------------------------

    average = summary.get("average_evaluation_score")
    average_display = f"{round(average, 2)}/5" if average is not None else "N/A"

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        components.metric_card(summary.get("total_interactions", 0), "Total Interactions")
    with m2:
        components.metric_card(summary.get("positive_feedback", 0), "👍 Positive")
    with m3:
        components.metric_card(summary.get("negative_feedback", 0), "👎 Negative")
    with m4:
        components.metric_card(average_display, "Avg. Evaluation Score")

    st.markdown('<hr class="mai-divider">', unsafe_allow_html=True)

    # ---------------------------------------------------------------
    # Charts (only rendered when there's real data to support them)
    # ---------------------------------------------------------------

    good = summary.get("positive_feedback", 0)
    bad = summary.get("negative_feedback", 0)

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown('<div class="mai-sidebar-section-label">Feedback distribution</div>', unsafe_allow_html=True)
        if good or bad:
            feedback_df = pd.DataFrame({"Count": [good, bad]}, index=["Positive", "Negative"])
            st.dataframe(feedback_df, use_container_width=True)
        else:
            st.caption("No feedback recorded yet.")

    with chart_col2:
        st.markdown('<div class="mai-sidebar-section-label">Evaluation score over time</div>', unsafe_allow_html=True)
        scores = [
            record.get("evaluation_score")
            for record in history
            if isinstance(record.get("evaluation_score"), (int, float))
        ]
        if scores:
            st.line_chart(scores)
        else:
            st.caption("No evaluation scores recorded yet.")

    st.markdown('<hr class="mai-divider">', unsafe_allow_html=True)

    # ---------------------------------------------------------------
    # Recent learning
    # ---------------------------------------------------------------

    st.markdown('<div class="mai-sidebar-section-label">Recent learning</div>', unsafe_allow_html=True)

    learned_records = [record for record in reversed(history) if record.get("learning")]

    if not learned_records:
        st.caption("No learning has been extracted yet. Give feedback to help MemoryAI learn.")
    else:
        for record in learned_records[:10]:
            st.markdown(f"✓ {record['learning']}")

    st.markdown('<hr class="mai-divider">', unsafe_allow_html=True)

    # ---------------------------------------------------------------
    # Full log (detail view)
    # ---------------------------------------------------------------

    with st.expander(f"Full interaction log ({len(history)} records)"):
        for record in reversed(history):
            components.info_card(
                record.get("timestamp", ""),
                record.get("user_message", ""),
                meta=(
                    f"Feedback: {record.get('feedback') or '—'} · "
                    f"Score: {record.get('evaluation_score', '—')}/5"
                ),
            )
