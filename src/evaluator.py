from ollama import chat


MODEL = "llama3.2:3b"


def evaluate_response(
    user_request,
    ai_response
):
    """
    Evaluate an AI response based on
    relevance, correctness, clarity,
    completeness, and task completion.
    """

    prompt = f"""
You are the evaluation module of an AI agent.

Evaluate the AI response given below.

USER REQUEST:
{user_request}

AI RESPONSE:
{ai_response}

Evaluate the response using these criteria:

1. Relevance
   Does the response directly address
   the user's request?

2. Correctness
   Is the information reasonable and
   factually correct?

3. Clarity
   Is the response easy to understand?

4. Completeness
   Does it cover the important parts
   of the request?

5. Task Completion
   Did the AI actually complete the
   requested task?

Give each criterion a score from 1 to 5.

Then calculate an overall score from 1 to 5.

Finally give one short improvement suggestion.

Return ONLY in this format:

Relevance: X/5
Correctness: X/5
Clarity: X/5
Completeness: X/5
Task Completion: X/5
Overall: X/5
Improvement: <short suggestion>

Do not explain your reasoning.
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

        evaluation = (
            response["message"]["content"]
            .strip()
        )

        return evaluation

    except Exception as e:

        print(
            "[Evaluation failed:]",
            e
        )

        return None


if __name__ == "__main__":

    print(
        "================================"
    )

    print(
        "      MEMORY AI EVALUATOR"
    )

    print(
        "================================"
    )

    user_request = input(
        "\nUser request: "
    )

    ai_response = input(
        "\nAI response: "
    )

    print(
        "\nEvaluating response..."
    )

    evaluation = evaluate_response(
        user_request,
        ai_response
    )

    print(
        "\nEvaluation:"
    )

    print(
        "----------------"
    )

    print(
        evaluation
    )