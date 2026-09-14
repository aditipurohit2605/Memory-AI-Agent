
import warnings
import os
import logging

warnings.filterwarnings("ignore")

os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

logging.getLogger().setLevel(logging.ERROR)

from src.llm_client import call_llm

from src.memory import (
    memory,
    search_memory,
    get_all_memories,
    delete_memory,
    delete_all_memories
)

from src.memory_extractor import (
    extract_memory,
    get_memory_category,
    get_memory_text as extract_memory_text
)

from src.tools import (
    calculator_tool,
    web_search_tool,
    execute_tool
)

from src.conversation import ConversationMemory
from src.feedback import FeedbackSystem
from src.planner import create_plan
from src.evaluator import evaluate_response

from src.profile import (
    get_user_profile,
    update_user_profile
)

from src.learning_log import (
    add_learning_record,
    get_learning_history,
    save_learning_log,
    get_learning_summary
)


MODEL = "llama3.2:3b"
USER_ID = "aditi"

MAX_IMPROVEMENT_ATTEMPTS = 1


conversation = ConversationMemory(
    max_messages=10
)

feedback_system = FeedbackSystem()

last_user_message = ""
last_ai_response = ""
last_evaluation_score = None


# =========================================================
# MEMORY RETRIEVAL
# =========================================================

def get_memory_text(user_id, user_message):
    """
    Retrieve relevant long-term memories from Mem0.
    """

    memories = search_memory(
        user_id,
        user_message
    )

    memory_text = ""

    for item in memories.get(
        "results",
        []
    ):

        stored_memory = item.get(
            "memory",
            ""
        )

        if stored_memory:
            memory_text += (
                "- "
                + stored_memory
                + "\n"
            )

    if not memory_text:

        memory_text = (
            "No relevant memories found."
        )

    return memory_text


# =========================================================
# EVALUATION SCORE
# =========================================================

def get_overall_score(evaluation):
    """
    Extract the overall score from evaluator output.
    """

    if not evaluation:
        return None

    for line in evaluation.splitlines():

        if line.lower().startswith(
            "overall:"
        ):

            try:

                score_text = (
                    line
                    .split(":", 1)[1]
                    .strip()
                )

                score_text = (
                    score_text
                    .split("/", 1)[0]
                    .strip()
                )

                score = float(score_text)
                return int(score) if score.is_integer() else score

            except Exception:

                return None

    return None


# =========================================================
# RESPONSE IMPROVEMENT
# =========================================================

def improve_response(
    user_request,
    current_response,
    evaluation,
    plan,
    memory_text
):
    """
    Improve the response when the evaluator
    identifies weaknesses.
    """

    prompt = f"""
You are the improvement module of MemoryAI.

USER REQUEST:
{user_request}

CURRENT RESPONSE:
{current_response}

EVALUATION:
{evaluation}

TASK PLAN:
{plan}

RELEVANT USER MEMORIES:
{memory_text}

Improve the response based on the evaluation.

Rules:

1. Answer the original request.
2. Fix the identified weakness.
3. Keep the answer clear and useful.
4. Respect relevant user preferences.
5. Do not mention the evaluator.
6. Do not mention internal memory systems.
7. Do not explain what changed.
8. Return ONLY the improved answer.
"""

    try:

        response = call_llm(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return (
            response["message"]["content"]
            .strip()
        )

    except Exception as e:

        print(
            "[Improvement failed:]",
            e
        )

        return current_response


# =========================================================
# SAVE CATEGORIZED MEMORY
# =========================================================

def save_new_memory(
    user_id,
    extracted_memory
):
    """
    Save a categorized memory to Mem0.

    The category is extracted separately,
    while only the clean memory statement
    is stored as semantic memory.
    """

    category = get_memory_category(
        extracted_memory
    )

    memory_text = extract_memory_text(
        extracted_memory
    )

    if not memory_text:

        return None, None

    memory.add(
        [
            {
                "role": "user",
                "content": memory_text
            }
        ],
        user_id=user_id
    )

    print(
        "[Memory saved]"
    )

    print(
        "[Category:",
        category,
        "]"
    )

    print(
        "[Memory:",
        memory_text,
        "]"
    )

    return category, memory_text


# =========================================================
# MAIN AGENT
# =========================================================

def run_agent(
    user_id,
    user_message
):
    """
    Run the complete MemoryAI pipeline.
    """

    global last_user_message
    global last_ai_response
    global last_evaluation_score

    print(
        "\n[Agent started]"
    )

    # -----------------------------------------------------
    # SHORT-TERM MEMORY
    # -----------------------------------------------------

    conversation.add_user_message(
        user_message
    )

    # -----------------------------------------------------
    # PLANNING
    # -----------------------------------------------------

    print(
        "\n[Planning...]"
    )

    plan = create_plan(
        user_message
    )

    print(
        "\n[Plan]"
    )

    print(plan)

    # -----------------------------------------------------
    # LONG-TERM MEMORY RETRIEVAL
    # -----------------------------------------------------

    memory_text = get_memory_text(
        user_id,
        user_message
    )

    # -----------------------------------------------------
    # SYSTEM PROMPT
    # -----------------------------------------------------

    system_prompt = f"""
You are MemoryAI, a helpful AI assistant
with short-term and long-term memory.

RELEVANT USER MEMORIES:

{memory_text}

CURRENT TASK PLAN:

{plan}

Instructions:

1. Use relevant memories to personalize
   your response.

2. Follow the task plan when one exists.

3. Pay attention to learned user behavior
   and response preferences.

4. If the user prefers a particular
   explanation style, follow it.

5. Do not mention Mem0, Qdrant, databases,
   or internal memory systems.

6. Do not invent user memories.

7. Answer clearly and naturally.

8. Use the calculator tool for mathematical
   calculations.

9. Use web_search for current, latest,
   recent, or internet-based information.

10. If no tool is needed, answer normally.

11. Use previous conversation when useful.

12. Do not show internal reasoning.
"""

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]

    messages.extend(
        conversation.get_messages()
    )

    # -----------------------------------------------------
    # FIRST AI RESPONSE
    # -----------------------------------------------------

    response = call_llm(
        model=MODEL,
        messages=messages,
        tools=[
            calculator_tool,
            web_search_tool
        ]
    )

    tool_calls = response[
        "message"
    ].get(
        "tool_calls"
    )

    # -----------------------------------------------------
    # TOOL EXECUTION
    # -----------------------------------------------------

    if tool_calls:

        print(
            "\n[Tool requested]"
        )

        messages.append(
            response["message"]
        )

        for tool_call in tool_calls:

            tool_name = (
                tool_call
                .function
                .name
            )

            arguments = (
                tool_call
                .function
                .arguments
            )

            print(
                "[Tool:",
                tool_name,
                "]"
            )

            print(
                "[Arguments:",
                arguments,
                "]"
            )

            result = execute_tool(
                tool_name,
                arguments
            )

            print(
                "[Tool result:",
                result,
                "]"
            )

            messages.append(
                {
                    "role": "tool",
                    "content": result
                }
            )

        final_response = call_llm(
            model=MODEL,
            messages=messages
        )

        answer = (
            final_response[
                "message"
            ][
                "content"
            ]
        )

    else:

        answer = (
            response[
                "message"
            ][
                "content"
            ]
        )

    # -----------------------------------------------------
    # EVALUATION
    # -----------------------------------------------------

    print(
        "\n[Evaluating response...]"
    )

    evaluation = evaluate_response(
        user_message,
        answer
    )

    print(
        "\n[Evaluation]"
    )

    print(evaluation)

    score = get_overall_score(
        evaluation
    )

    last_evaluation_score = score

    print(
        "\n[Overall score:",
        str(score) + "/5]"
    )

    # -----------------------------------------------------
    # SELF-IMPROVEMENT
    # -----------------------------------------------------

    attempts = 0

    while (
        score is not None
        and score < 4
        and attempts < MAX_IMPROVEMENT_ATTEMPTS
    ):

        attempts += 1

        print(
            "\n[Improving response...]"
        )

        answer = improve_response(
            user_message,
            answer,
            evaluation,
            plan,
            memory_text
        )

        print(
            "[Response improved]"
        )

        evaluation = evaluate_response(
            user_message,
            answer
        )

        print(
            "\n[New evaluation]"
        )

        print(evaluation)

        score = get_overall_score(
            evaluation
        )

        last_evaluation_score = score

        print(
            "\n[New overall score:",
            str(score) + "/5]"
        )

    # -----------------------------------------------------
    # MEMORY EXTRACTION
    # -----------------------------------------------------

    extracted_memory = extract_memory(
        user_message
    )

    category = None
    clean_memory = None

    if (
        extracted_memory
        and extracted_memory != "NO_MEMORY"
    ):

        category, clean_memory = (
            save_new_memory(
                user_id,
                extracted_memory
            )
        )

        if clean_memory:

            update_user_profile(
                user_id
            )

    # -----------------------------------------------------
    # PERSISTENT LEARNING LOG
    # -----------------------------------------------------

    add_learning_record(
        user_message=user_message,
        ai_response=answer,
        feedback=None,
        learning=clean_memory,
        evaluation_score=score
    )

    print(
        "[Interaction saved to learning log]"
    )

    # -----------------------------------------------------
    # SHORT-TERM MEMORY
    # -----------------------------------------------------

    conversation.add_assistant_message(
        answer
    )

    last_user_message = user_message
    last_ai_response = answer

    return answer


# =========================================================
# COMMAND LINE INTERFACE
# =========================================================

if __name__ == "__main__":

    user_id = USER_ID

    print(
        "\n================================"
    )

    print(
        "         MEMORY AI AGENT"
    )

    print(
        "================================"
    )

    print(
        "Model:",
        MODEL
    )

    print(
        "Long-Term Memory: Mem0 + Qdrant"
    )

    print(
        "Short-Term Memory: Enabled"
    )

    print(
        "Native Tool Calling: Enabled"
    )

    print(
        "Tools: Calculator + Web Search"
    )

    print(
        "Feedback Learning: Enabled"
    )

    print(
        "Memory Management: Enabled"
    )

    print(
        "Agent Planning: Enabled"
    )

    print(
        "Self-Evaluation: Enabled"
    )

    print(
        "User Profile: Enabled"
    )

    print(
        "Automatic Profile Update: Enabled"
    )

    print(
        "Persistent Learning Log: Enabled"
    )

    print(
        "Categorized Memory: Enabled"
    )

    print(
        "\nCommands:"
    )

    print("/memory")
    print("/memories")
    print("/profile")

    print("/learning")
    print("/learning-summary")

    print("/forget <memory-id>")
    print("/forget-all")

    print("/clear")

    print("/feedback good")
    print("/feedback bad")
    print("/feedback-summary")

    print("exit")

    print(
        "\nType your message below.\n"
    )

    while True:

        user_message = input(
            "You: "
        ).strip()

        # =================================================
        # EXIT
        # =================================================

        if (
            user_message.lower()
            == "exit"
        ):

            print(
                "\nGoodbye!"
            )

            break

        if not user_message:
            continue

        # =================================================
        # PROFILE
        # =================================================

        if (
            user_message.lower()
            == "/profile"
        ):

            print(
                "\n[Generating user profile...]"
            )

            profile = get_user_profile(
                user_id
            )

            print(
                "\n================================"
            )

            print(
                "          MEMORYAI PROFILE"
            )

            print(
                "================================"
            )

            print(profile)

            print(
                "================================"
            )

            continue

        # =================================================
        # LEARNING HISTORY
        # =================================================

        if (
            user_message.lower()
            == "/learning"
        ):

            print(
                "\n================================"
            )

            print(
                "       LEARNING HISTORY"
            )

            print(
                "================================"
            )

            history = (
                get_learning_history()
            )

            if not history:

                print(
                    "No learning records found."
                )

            else:

                for index, record in enumerate(
                    history,
                    start=1
                ):

                    print(
                        f"\n{index}. "
                        f"{record.get('timestamp')}"
                    )

                    print(
                        "   User:",
                        record.get(
                            "user_message"
                        )
                    )

                    print(
                        "   AI:",
                        record.get(
                            "ai_response"
                        )
                    )

                    print(
                        "   Feedback:",
                        record.get(
                            "feedback"
                        )
                    )

                    print(
                        "   Learning:",
                        record.get(
                            "learning"
                        )
                    )

                    print(
                        "   Evaluation:",
                        record.get(
                            "evaluation_score"
                        )
                    )

            print(
                "\n================================"
            )

            continue

        # =================================================
        # LEARNING SUMMARY
        # =================================================

        if (
            user_message.lower()
            == "/learning-summary"
        ):

            summary = (
                get_learning_summary()
            )

            print(
                "\n================================"
            )

            print(
                "       LEARNING SUMMARY"
            )

            print(
                "================================"
            )

            print(
                "Total interactions:",
                summary[
                    "total_interactions"
                ]
            )

            print(
                "Positive feedback:",
                summary[
                    "positive_feedback"
                ]
            )

            print(
                "Negative feedback:",
                summary[
                    "negative_feedback"
                ]
            )

            average = summary[
                "average_evaluation_score"
            ]

            if average is not None:

                print(
                    "Average evaluation:",
                    round(
                        average,
                        2
                    ),
                    "/5"
                )

            else:

                print(
                    "Average evaluation: N/A"
                )

            print(
                "================================"
            )

            continue

        # =================================================
        # FEEDBACK
        # =================================================

        if (
            user_message.lower()
            .startswith("/feedback")
        ):

            parts = (
                user_message.split()
            )

            if len(parts) != 2:

                print(
                    "\nUsage:"
                )

                print(
                    "/feedback good"
                )

                print(
                    "/feedback bad"
                )

                continue

            feedback = parts[
                1
            ].lower()

            if feedback_system.add_feedback(
                feedback
            ):

                print(
                    "\nFeedback saved:",
                    feedback
                )

                if (
                    last_user_message
                    and last_ai_response
                ):

                    print(
                        "[Analyzing feedback...]"
                    )

                    learning_memory = (
                        feedback_system
                        .analyze_feedback(
                            last_user_message,
                            last_ai_response,
                            feedback
                        )
                    )

                    if learning_memory:

                        categorized_learning = (
                            "CATEGORY: learned_behavior\n"
                            "MEMORY: "
                            + learning_memory
                        )

                        (
                            category,
                            clean_learning
                        ) = save_new_memory(
                            user_id,
                            categorized_learning
                        )

                        print(
                            "[Learning extracted:]"
                        )

                        print(
                            learning_memory
                        )

                        print(
                            "[Learning saved "
                            "to long-term memory]"
                        )

                        update_user_profile(
                            user_id
                        )

                        # ---------------------------------
                        # UPDATE LEARNING LOG
                        # ---------------------------------

                        history = (
                            get_learning_history()
                        )

                        if history:

                            history[-1][
                                "feedback"
                            ] = feedback

                            history[-1][
                                "learning"
                            ] = clean_learning

                            history[-1][
                                "evaluation_score"
                            ] = (
                                last_evaluation_score
                            )

                            save_learning_log(
                                history
                            )

                            print(
                                "[Learning log updated]"
                            )

                    else:

                        print(
                            "[No useful learning "
                            "was extracted]"
                        )

                else:

                    print(
                        "[No previous response "
                        "available for feedback]"
                    )

            else:

                print(
                    "\nInvalid feedback."
                )

                print(
                    "Use /feedback good"
                )

                print(
                    "or /feedback bad"
                )

            continue

        # =================================================
        # FEEDBACK SUMMARY
        # =================================================

        if (
            user_message.lower()
            == "/feedback-summary"
        ):

            summary = (
                feedback_system
                .get_summary()
            )

            print(
                "\nFeedback Summary"
            )

            print(
                "----------------"
            )

            print(
                "Good:",
                summary["good"]
            )

            print(
                "Bad:",
                summary["bad"]
            )

            print(
                "Total:",
                summary["total"]
            )

            continue

        # =================================================
        # RELEVANT MEMORY
        # =================================================

        if (
            user_message.lower()
            == "/memory"
        ):

            print(
                "\nRelevant memories:"
            )

            memories = search_memory(
                user_id,
                "user preferences goals skills "
                "projects feedback learning "
                "response style"
            )

            results = memories.get(
                "results",
                []
            )

            if not results:

                print(
                    "No memories found."
                )

            else:

                for item in results:

                    print(
                        "-",
                        item["memory"]
                    )

            continue

        # =================================================
        # ALL MEMORIES
        # =================================================

        if (
            user_message.lower()
            == "/memories"
        ):

            print(
                "\nAll stored memories:"
            )

            print(
                "===================="
            )

            memories = get_all_memories(
                user_id
            )

            results = memories.get(
                "results",
                []
            )

            if not results:

                print(
                    "No memories found."
                )

            else:

                for index, item in enumerate(
                    results,
                    start=1
                ):

                    memory_id = item.get(
                        "id",
                        "Unknown ID"
                    )

                    memory_text = item.get(
                        "memory",
                        "No memory text"
                    )

                    print(
                        f"\n{index}. "
                        f"{memory_text}"
                    )

                    print(
                        "   ID:",
                        memory_id
                    )

            continue

        # =================================================
        # FORGET ONE MEMORY
        # =================================================

        if (
            user_message.lower()
            .startswith("/forget ")
        ):

            parts = (
                user_message.split(
                    maxsplit=1
                )
            )

            if len(parts) != 2:

                print(
                    "\nUsage:"
                )

                print(
                    "/forget <memory-id>"
                )

                continue

            memory_id = parts[
                1
            ].strip()

            try:

                delete_memory(
                    memory_id
                )

                print(
                    "\nMemory deleted successfully."
                )

                print(
                    "Memory ID:",
                    memory_id
                )

            except Exception as e:

                print(
                    "\nCould not delete memory."
                )

                print(
                    "Error:",
                    e
                )

            continue

        # =================================================
        # FORGET ALL
        # =================================================

        if (
            user_message.lower()
            == "/forget-all"
        ):

            confirmation = input(
                "\nThis will delete ALL long-term "
                "memories for this user.\n"
                "Type YES to continue: "
            ).strip()

            if confirmation == "YES":

                try:

                    delete_all_memories(
                        user_id
                    )

                    print(
                        "\nAll long-term memories deleted."
                    )

                except Exception as e:

                    print(
                        "\nCould not delete memories."
                    )

                    print(
                        "Error:",
                        e
                    )

            else:

                print(
                    "\nOperation cancelled."
                )

            continue

        # =================================================
        # CLEAR SHORT-TERM MEMORY
        # =================================================

        if (
            user_message.lower()
            == "/clear"
        ):

            conversation.clear()

            print(
                "\nShort-term conversation memory cleared."
            )

            continue

        # =================================================
        # RUN AGENT
        # =================================================

        answer = run_agent(
            user_id,
            user_message
        )

        print(
            "\nAI:",
            answer
        )

        print()

