
import os
import streamlit as st


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="MemoryAI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# RUNTIME CONFIGURATION
# =========================================================

def configure_runtime():
    """
    Configure optional runtime settings.

    On Streamlit Cloud, secrets may exist.
    Locally, secrets.toml may not exist, so
    st.secrets must be handled safely.
    """

    try:
        ollama_host = st.secrets.get("OLLAMA_HOST")
    except Exception:
        ollama_host = None

    if ollama_host:
        os.environ["OLLAMA_HOST"] = ollama_host


# =========================================================
# BACKEND IMPORTS
# =========================================================

def load_backend():
    """
    Import backend modules after runtime configuration.
    """

    from src.agent import run_agent
    from src.memory import (
        search_memory,
        get_all_memories,
        delete_memory,
        delete_all_memories
    )

    from src.profile import get_user_profile

    from src.learning_log import (
        get_learning_history,
        get_learning_summary
    )

    return {
        "run_agent": run_agent,
        "search_memory": search_memory,
        "get_all_memories": get_all_memories,
        "delete_memory": delete_memory,
        "delete_all_memories": delete_all_memories,
        "get_user_profile": get_user_profile,
        "get_learning_history": get_learning_history,
        "get_learning_summary": get_learning_summary,
    }


# =========================================================
# INITIALIZE RUNTIME
# =========================================================

configure_runtime()


# =========================================================
# SESSION STATE
# =========================================================

if "backend" not in st.session_state:
    try:
        st.session_state.backend = load_backend()
    except Exception as e:
        st.session_state.backend_error = str(e)
        st.session_state.backend = None


if "user_id" not in st.session_state:
    st.session_state.user_id = "aditi"


if "page" not in st.session_state:
    st.session_state.page = "Chat"


if "messages" not in st.session_state:
    st.session_state.messages = []


# =========================================================
# BACKEND ERROR
# =========================================================

if st.session_state.backend is None:

    st.title("🧠 MemoryAI")

    st.error(
        "MemoryAI backend could not be loaded."
    )

    with st.expander("Show error details"):
        st.code(
            st.session_state.get(
                "backend_error",
                "Unknown backend error."
            )
        )

    st.info(
        "Check your Python environment, dependencies, "
        "Ollama configuration, Mem0, and Qdrant setup."
    )

    st.stop()


backend = st.session_state.backend


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        # 🧠 MemoryAI

        **Self-Learning AI Agent**

        Persistent memory • Planning •
        Evaluation • Feedback
        """
    )

    st.divider()

    st.markdown("### Navigation")

    pages = [
        "Chat",
        "Memory",
        "Profile",
        "Learning",
        "System"
    ]

    selected_page = st.radio(
        "Go to",
        pages,
        index=pages.index(
            st.session_state.page
        ),
        label_visibility="collapsed"
    )

    st.session_state.page = selected_page

    st.divider()

    st.markdown("### User")

    st.caption(
        "User ID: " +
        st.session_state.user_id
    )

    st.divider()

    st.caption(
        "MemoryAI • Local AI Agent"
    )


# =========================================================
# CHAT PAGE
# =========================================================

def show_chat():

    st.title("💬 Chat with MemoryAI")

    st.markdown(
        """
        Ask questions, give instructions, or tell MemoryAI
        something about yourself.
        """
    )

    st.divider()

    # -----------------------------------------------------
    # Display previous messages
    # -----------------------------------------------------

    for message in st.session_state.messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )

    # -----------------------------------------------------
    # Chat input
    # -----------------------------------------------------

    user_message = st.chat_input(
        "Message MemoryAI..."
    )

    if user_message:

        # Add user message
        st.session_state.messages.append(
            {
                "role": "user",
                "content": user_message
            }
        )

        with st.chat_message("user"):
            st.markdown(user_message)

        # Generate response
        with st.chat_message("assistant"):

            with st.spinner(
                "MemoryAI is thinking..."
            ):

                try:

                    response = backend[
                        "run_agent"
                    ](
                        st.session_state.user_id,
                        user_message
                    )

                except Exception as e:

                    response = (
                        "Sorry, an error occurred while "
                        "running the agent.\n\n"
                        + str(e)
                    )

            st.markdown(response)

        # Save assistant response
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )

        st.rerun()


# =========================================================
# MEMORY PAGE
# =========================================================

def show_memory():

    st.title("🧠 Long-Term Memory")

    st.markdown(
        """
        These are the persistent memories stored for the
        current user.
        """
    )

    st.divider()

    user_id = st.session_state.user_id

    try:

        memories_data = backend[
            "get_all_memories"
        ](user_id)

        if isinstance(
            memories_data,
            dict
        ):
            memories = memories_data.get(
                "results",
                []
            )
        else:
            memories = memories_data or []

    except Exception as e:

        st.error(
            "Could not load memories."
        )

        st.code(str(e))

        return

    if not memories:

        st.info(
            "No long-term memories found yet."
        )

        return

    st.success(
        f"{len(memories)} memories found."
    )

    # -----------------------------------------------------
    # Memory search
    # -----------------------------------------------------

    search_text = st.text_input(
        "🔎 Search memories",
        placeholder="Search your memories..."
    )

    if search_text:

        filtered_memories = []

        for item in memories:

            memory_text = item.get(
                "memory",
                ""
            )

            if search_text.lower() in memory_text.lower():

                filtered_memories.append(
                    item
                )

        memories = filtered_memories

    # -----------------------------------------------------
    # Display memories
    # -----------------------------------------------------

    for index, item in enumerate(
        memories,
        start=1
    ):

        memory_text = item.get(
            "memory",
            ""
        )

        memory_id = item.get(
            "id",
            ""
        )

        with st.container(
            border=True
        ):

            col1, col2 = st.columns(
                [5, 1]
            )

            with col1:

                st.markdown(
                    f"**Memory {index}**"
                )

                st.write(
                    memory_text
                )

                if memory_id:

                    st.caption(
                        "ID: " +
                        str(memory_id)
                    )

            with col2:

                if memory_id:

                    if st.button(
                        "🗑️ Delete",
                        key=f"delete_{memory_id}"
                    ):

                        try:

                            backend[
                                "delete_memory"
                            ](
                                memory_id
                            )

                            st.success(
                                "Memory deleted."
                            )

                            st.rerun()

                        except Exception as e:

                            st.error(
                                str(e)
                            )

    # -----------------------------------------------------
    # Delete all
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "Memory Management"
    )

    if st.button(
        "🗑️ Delete All Memories",
        type="secondary"
    ):

        try:

            backend[
                "delete_all_memories"
            ](
                user_id
            )

            st.success(
                "All memories deleted."
            )

            st.rerun()

        except Exception as e:

            st.error(
                "Could not delete memories."
            )

            st.code(str(e))


# =========================================================
# PROFILE PAGE
# =========================================================

def show_profile():

    st.title("👤 User Profile")

    st.markdown(
        """
        MemoryAI builds your profile from information
        learned through your conversations.
        """
    )

    st.divider()

    user_id = st.session_state.user_id

    try:

        profile = backend[
            "get_user_profile"
        ](
            user_id
        )

    except Exception as e:

        st.error(
            "Could not generate profile."
        )

        st.code(str(e))

        return

    if isinstance(
        profile,
        dict
    ):

        for key, value in profile.items():

            st.markdown(
                f"### {str(key).replace('_', ' ').title()}"
            )

            st.write(
                value
            )

    else:

        st.markdown(
            "### Profile"
        )

        st.write(
            profile
        )


# =========================================================
# LEARNING PAGE
# =========================================================

def show_learning():

    st.title("📚 Learning & Improvement")

    st.markdown(
        """
        MemoryAI tracks interactions, feedback,
        learned information, and evaluation scores.
        """
    )

    st.divider()

    try:

        summary = backend[
            "get_learning_summary"
        ]()

    except Exception as e:

        st.error(
            "Could not load learning summary."
        )

        st.code(str(e))

        return

    # -----------------------------------------------------
    # Metrics
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Interactions",
            summary.get(
                "total_interactions",
                0
            )
        )

    with col2:

        st.metric(
            "Positive Feedback",
            summary.get(
                "positive_feedback",
                0
            )
        )

    with col3:

        st.metric(
            "Negative Feedback",
            summary.get(
                "negative_feedback",
                0
            )
        )

    with col4:

        average = summary.get(
            "average_evaluation_score"
        )

        if average is None:

            average_display = "N/A"

        else:

            average_display = (
                f"{average:.2f}/5"
            )

        st.metric(
            "Average Score",
            average_display
        )

    st.divider()

    # -----------------------------------------------------
    # Learning history
    # -----------------------------------------------------

    try:

        history = backend[
            "get_learning_history"
        ]()

    except Exception as e:

        st.error(
            "Could not load learning history."
        )

        st.code(str(e))

        return

    if not history:

        st.info(
            "No learning records found yet."
        )

        return

    # -----------------------------------------------------
    # Feedback table
    # -----------------------------------------------------

    import pandas as pd

    feedback_rows = []

    for record in history:

        feedback_rows.append(
            {
                "Feedback": record.get(
                    "feedback"
                ),
                "Evaluation Score": record.get(
                    "evaluation_score"
                )
            }
        )

    feedback_df = pd.DataFrame(
        feedback_rows
    )

    st.subheader(
        "Feedback History"
    )

    st.dataframe(
        feedback_df,
        use_container_width=True,
        hide_index=True
    )

    # -----------------------------------------------------
    # Evaluation scores
    # -----------------------------------------------------

    scores = []

    for record in history:

        score = record.get(
            "evaluation_score"
        )

        if isinstance(
            score,
            (int, float)
        ):

            scores.append(
                score
            )

    st.subheader(
        "Evaluation Scores"
    )

    if scores:

        scores_df = pd.DataFrame(
            {
                "Evaluation Score": scores
            }
        )

        st.dataframe(
            scores_df,
            use_container_width=True,
            hide_index=True
        )

    else:

        st.info(
            "No evaluation scores available."
        )

    # -----------------------------------------------------
    # Recent learning
    # -----------------------------------------------------

    st.subheader(
        "Recent Learning"
    )

    recent_records = history[-10:]

    for record in reversed(
        recent_records
    ):

        learning = record.get(
            "learning"
        )

        if not learning:

            continue

        with st.container(
            border=True
        ):

            st.write(
                learning
            )

            score = record.get(
                "evaluation_score"
            )

            if score is not None:

                st.caption(
                    f"Evaluation score: {score}/5"
                )

    # -----------------------------------------------------
    # Full learning log
    # -----------------------------------------------------

    st.divider()

    st.subheader(
        "Full Learning Log"
    )

    for index, record in enumerate(
        reversed(history),
        start=1
    ):

        with st.expander(
            f"Interaction {len(history) - index + 1}"
        ):

            st.markdown(
                "**User:**"
            )

            st.write(
                record.get(
                    "user_message",
                    ""
                )
            )

            st.markdown(
                "**AI:**"
            )

            st.write(
                record.get(
                    "ai_response",
                    ""
                )
            )

            st.markdown(
                "**Feedback:**"
            )

            st.write(
                record.get(
                    "feedback",
                    "None"
                )
            )

            st.markdown(
                "**Learning:**"
            )

            st.write(
                record.get(
                    "learning",
                    "None"
                )
            )

            st.markdown(
                "**Evaluation:**"
            )

            st.write(
                record.get(
                    "evaluation_score",
                    "N/A"
                )
            )


# =========================================================
# SYSTEM PAGE
# =========================================================

def show_system():

    st.title("⚙️ System")

    st.markdown(
        """
        Current MemoryAI runtime and model information.
        """
    )

    st.divider()

    # -----------------------------------------------------
    # Model
    # -----------------------------------------------------

    st.subheader(
        "AI Model"
    )

    st.write(
        "Model: `llama3.2:3b`"
    )

    # -----------------------------------------------------
    # Ollama
    # -----------------------------------------------------

    st.subheader(
        "Ollama Status"
    )

    try:

        import ollama

        models_response = ollama.list()

        model_names = []

        if hasattr(
            models_response,
            "models"
        ):

            for model in models_response.models:

                if hasattr(
                    model,
                    "model"
                ):

                    model_names.append(
                        model.model
                    )

                elif isinstance(
                    model,
                    dict
                ):

                    model_names.append(
                        model.get(
                            "model",
                            ""
                        )
                    )

        elif isinstance(
            models_response,
            dict
        ):

            for model in models_response.get(
                "models",
                []
            ):

                if isinstance(
                    model,
                    dict
                ):

                    model_names.append(
                        model.get(
                            "name",
                            model.get(
                                "model",
                                ""
                            )
                        )
                    )

        if "llama3.2:3b" in model_names:

            st.success(
                "Ollama is running and llama3.2:3b is available."
            )

        elif model_names:

            st.warning(
                "Ollama is running, but llama3.2:3b "
                "was not found."
            )

            st.write(
                "Available models:"
            )

            st.code(
                "\n".join(model_names)
            )

        else:

            st.warning(
                "Ollama is running, but no models were found."
            )

    except Exception as e:

        st.error(
            "Ollama is not available."
        )

        st.code(
            str(e)
        )

    # -----------------------------------------------------
    # Memory
    # -----------------------------------------------------

    st.subheader(
        "Long-Term Memory"
    )

    st.success(
        "Mem0 + Qdrant"
    )

    # -----------------------------------------------------
    # Architecture
    # -----------------------------------------------------

    st.subheader(
        "Architecture"
    )

    architecture = {
        "LLM": "Ollama + Llama 3.2 3B",
        "Memory": "Mem0",
        "Vector Database": "Qdrant",
        "Embeddings": "all-MiniLM-L6-v2",
        "Agent Framework": "Custom Python Agent",
        "UI": "Streamlit",
        "Tools": "Calculator + Web Search",
        "Learning": "Feedback + Evaluation",
    }

    import pandas as pd

    architecture_df = pd.DataFrame(
        list(
            architecture.items()
        ),
        columns=[
            "Component",
            "Technology"
        ]
    )

    st.dataframe(
        architecture_df,
        use_container_width=True,
        hide_index=True
    )


# =========================================================
# PAGE ROUTER
# =========================================================

if st.session_state.page == "Chat":

    show_chat()

elif st.session_state.page == "Memory":

    show_memory()

elif st.session_state.page == "Profile":

    show_profile()

elif st.session_state.page == "Learning":

    show_learning()

elif st.session_state.page == "System":

    show_system()