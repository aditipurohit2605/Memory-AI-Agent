"""
ui/chat.py

The Chat page. Every response the user sees comes from
src.agent.run_agent() - this file only orchestrates calls to the
existing backend and renders the result. It does not re-implement
memory retrieval, evaluation, or learning.

Integration notes (see README_UI_INTEGRATION.md for the full list):

- run_agent() returns only the final answer string. To show a
  "memories used" indicator, this page makes its own read-only call
  to the backend's existing search_memory() with the same query -
  the same function run_agent() itself calls internally - so the
  count shown is real, not invented.

- Whether a new memory was saved, and the evaluation score for the
  turn, are read back from get_learning_history()[-1] immediately
  after run_agent() finishes, since add_learning_record() already
  stores both of those values for every turn.

- Tool usage (calculator / web search) is decided and executed
  entirely inside run_agent() and is not returned or exposed
  anywhere. There is no reliable, non-fabricated way to show a
  "tool used" badge without changing src/agent.py, so this page
  intentionally does not show one. See the integration notes doc
  for the smallest possible backend change that would expose it.
"""

import streamlit as st

from ui import components
from ui.state import get_backend


def _run_turn(agent_module, user_message: str) -> dict:
    """
    Calls the existing backend and reads back what it already
    computed and persisted for this turn. No backend logic is
    duplicated here.
    """

    # Same read-only call run_agent() makes internally - lets us show
    # a real "memories used" count without changing the backend.
    try:
        retrieved = agent_module.search_memory(agent_module.USER_ID, user_message)
        results = retrieved.get("results", []) if isinstance(retrieved, dict) else []
        memories_used = len([item for item in results if item.get("memory")])
    except Exception:
        memories_used = None

    answer = agent_module.run_agent(agent_module.USER_ID, user_message)

    eval_score = None
    new_memory = None
    try:
        history = agent_module.get_learning_history()
        if history:
            last_record = history[-1]
            eval_score = last_record.get("evaluation_score")
            new_memory = last_record.get("learning")
    except Exception:
        pass

    return {
        "answer": answer,
        "memories_used": memories_used,
        "eval_score": eval_score,
        "new_memory": new_memory,
    }


def _submit_feedback(agent_module, feedback_value: str):
    """
    Mirrors the existing CLI's /feedback flow in src/agent.py
    (add_feedback -> analyze_feedback -> save as learned_behavior
    memory -> update profile -> update learning log) using only
    existing backend functions.

    Returns (ok: bool, message: str).
    """

    if not agent_module.feedback_system.add_feedback(feedback_value):
        return False, "Invalid feedback value."

    user_msg = agent_module.last_user_message
    ai_msg = agent_module.last_ai_response

    if not (user_msg and ai_msg):
        return False, "No previous response is available for feedback."

    learning_statement = agent_module.feedback_system.analyze_feedback(
        user_msg, ai_msg, feedback_value
    )

    if not learning_statement:
        return True, "Feedback saved. No specific learning was extracted this time."

    categorized_learning = f"CATEGORY: learned_behavior\nMEMORY: {learning_statement}"

    _category, clean_learning = agent_module.save_new_memory(
        agent_module.USER_ID, categorized_learning
    )

    if clean_learning:
        agent_module.update_user_profile(agent_module.USER_ID)

    try:
        history = agent_module.get_learning_history()
        if history:
            history[-1]["feedback"] = feedback_value
            history[-1]["learning"] = clean_learning
            history[-1]["evaluation_score"] = agent_module.last_evaluation_score
            agent_module.save_learning_log(history)
    except Exception:
        pass

    return True, learning_statement or "Feedback saved."


def render() -> None:
    components.page_header(
        "💬 Chat",
        "Ask MemoryAI anything. It remembers what matters and learns from your feedback.",
    )

    agent_module = None
    error = None
    if st.session_state.chat_history or st.session_state.pending_prompt:
        agent_module, error = get_backend()

    try:
        history = agent_module.get_learning_history() if agent_module else []
        memories = agent_module.get_all_memories(agent_module.USER_ID) if agent_module else {}
        memory_count = len(memories.get("results", [])) if isinstance(memories, dict) else 0
    except Exception:
        history = []
        memory_count = 0

    components.hero_panel(
        "PERSONAL INTELLIGENCE / LOCAL FIRST",
        "An assistant that gets more useful over time.",
        "MemoryAI connects conversation, long-term memory, feedback, and self-evaluation into one private workspace.",
        [
            (memory_count, "memories"),
            (len(history), "learning signals"),
            ("READY", "chat mode"),
        ],
    )

    components.section_label("Starter missions")
    prompt_cols = st.columns(3)
    starter_prompts = [
        ("Plan a build", "Help me plan a personal AI project in 5 clear steps."),
        ("Use my context", "What do you remember about my goals and preferences?"),
        ("Try a tool", "Calculate 144 * 27 and explain the result simply."),
    ]
    for column, (label, prompt) in zip(prompt_cols, starter_prompts):
        with column:
            if st.button(label, key=f"starter_{label}", use_container_width=True):
                st.session_state.pending_prompt = prompt
                st.rerun()

    st.markdown('<div class="mai-divider"></div>', unsafe_allow_html=True)

    header_col, clear_col = st.columns([5, 1])
    with clear_col:
        if st.button("Clear conversation", use_container_width=True):
            agent_module.conversation.clear()
            st.session_state.chat_history = []
            st.session_state.last_feedback_turn = -1
            st.session_state.feedback_message = None
            st.rerun()

    if not st.session_state.chat_history:
        components.empty_state(
            "🧠",
            "Start a conversation",
            "Ask a question below. MemoryAI will use relevant long-term "
            "memories to personalize its answer, and remember anything "
            "useful for next time.",
        )

    for turn_index, turn in enumerate(st.session_state.chat_history):
        with st.chat_message(turn["role"]):
            st.markdown(turn["content"])

            if turn["role"] == "assistant":
                indicators = []
                if turn.get("memories_used") is not None:
                    count = turn["memories_used"]
                    if count > 0:
                        indicators.append(f"🧠 {count} relevant memor{'y' if count == 1 else 'ies'} used")
                    else:
                        indicators.append("🧠 No relevant memories found")
                if turn.get("new_memory"):
                    indicators.append("✨ New memory saved")
                if turn.get("eval_score") is not None:
                    indicators.append(f"📊 Quality score: {turn['eval_score']}/5")
                components.indicator_row(indicators)

                is_latest_assistant_turn = turn_index == len(st.session_state.chat_history) - 1
                if is_latest_assistant_turn:
                    already_rated = st.session_state.last_feedback_turn == turn_index
                    fcol1, fcol2, _ = st.columns([1, 1, 4])
                    with fcol1:
                        if st.button("👍 Helpful", key=f"good_{turn_index}", disabled=already_rated):
                            ok, message = _submit_feedback(agent_module, "good")
                            st.session_state.last_feedback_turn = turn_index
                            st.session_state.feedback_message = ("success" if ok else "error", message)
                            st.rerun()
                    with fcol2:
                        if st.button("👎 Not helpful", key=f"bad_{turn_index}", disabled=already_rated):
                            ok, message = _submit_feedback(agent_module, "bad")
                            st.session_state.last_feedback_turn = turn_index
                            st.session_state.feedback_message = ("success" if ok else "error", message)
                            st.rerun()

                    if already_rated and st.session_state.feedback_message:
                        kind, message = st.session_state.feedback_message
                        if kind == "success":
                            st.caption(f"✓ Learned: {message}")
                        else:
                            st.caption(f"⚠️ {message}")

    user_message = st.chat_input("Ask MemoryAI anything...")
    if st.session_state.pending_prompt:
        user_message = st.session_state.pending_prompt
        st.session_state.pending_prompt = None

    if user_message:
        if not agent_module:
            agent_module, error = get_backend()
        if not agent_module:
            st.session_state.chat_history.append(
                {
                    "role": "assistant",
                    "content": f"MemoryAI is still starting. {error or 'Please try again in a moment.'}",
                }
            )
            st.rerun()

        st.session_state.chat_history.append({"role": "user", "content": user_message})
        st.session_state.last_feedback_turn = -1
        st.session_state.feedback_message = None

        with st.spinner("MemoryAI is thinking..."):
            try:
                result = _run_turn(agent_module, user_message)
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": result["answer"],
                        "memories_used": result["memories_used"],
                        "new_memory": result["new_memory"],
                        "eval_score": result["eval_score"],
                    }
                )
            except Exception as exc:  # noqa: BLE001
                import traceback

                traceback.print_exc()
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": (
                            "⚠️ MemoryAI ran into a problem generating a response. "
                            "Please make sure Ollama is running and Llama 3.2 3B is "
                            "available, then try again."
                        ),
                    }
                )

        st.rerun()
