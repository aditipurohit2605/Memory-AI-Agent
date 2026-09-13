
from ollama import chat


MODEL = "llama3.2:3b"


# ========================================
# CREATE PLAN
# ========================================

def create_plan(user_request):
    """
    Decide whether the request needs a plan.

    Simple requests return:
    DIRECT_ANSWER

    Complex requests return:
    a short numbered plan.
    """

    prompt = f"""
You are the planning module of MemoryAI.

Analyze this user request:

{user_request}

Your ONLY job is to decide whether the request
needs multiple steps.

IMPORTANT:

If the user is:

- stating a preference
- sharing information
- saying something about themselves
- asking a simple question
- asking for a simple calculation
- asking for a definition
- asking for a short explanation
- asking for a simple direct answer

return EXACTLY:

DIRECT_ANSWER

Do NOT create a plan for these requests.

Only create a numbered plan when the task genuinely
requires multiple steps, research, analysis, coding,
comparison, or a multi-stage process.

If a plan is required:

1. Keep it short.
2. Use 2 to 5 steps.
3. Do not answer the user's question.
4. Do not include explanations.
5. Do not write an introduction.

Example 1:

User:
I prefer simple explanations.

Output:
DIRECT_ANSWER

Example 2:

User:
What is Python?

Output:
DIRECT_ANSWER

Example 3:

User:
What is 25 * 48?

Output:
DIRECT_ANSWER

Example 4:

User:
I am interested in computer vision.

Output:
DIRECT_ANSWER

Example 5:

User:
Build a Python Flask API that accepts an image
and returns a classification result.

Output:
1. Create the Flask API structure.
2. Add image upload handling.
3. Load the classification model.
4. Implement prediction and response handling.
5. Test the API.

Return ONLY the final decision or numbered plan.
"""


    try:

        response = chat(
            model=MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        plan = (
            response[
                "message"
            ][
                "content"
            ]
            .strip()
        )

        # --------------------------------
        # Clean accidental formatting
        # --------------------------------

        plan_upper = plan.upper()

        # If model includes DIRECT_ANSWER
        # anywhere, treat it as direct.
        if "DIRECT_ANSWER" in plan_upper:

            return "DIRECT_ANSWER"

        return plan

    except Exception as e:

        print(
            "[Planning failed:]",
            e
        )

        return "DIRECT_ANSWER"


# ========================================
# TEST
# ========================================

if __name__ == "__main__":

    print(
        "================================"
    )

    print(
        "       MEMORY AI PLANNER"
    )

    print(
        "================================"
    )

    user_request = input(
        "\nEnter a task: "
    )

    plan = create_plan(
        user_request
    )

    print(
        "\nGenerated Plan:"
    )

    print(
        "----------------"
    )

    print(
        plan
    )
