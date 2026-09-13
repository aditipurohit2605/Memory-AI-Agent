
from ollama import chat


MODEL = "llama3.2:3b"


class FeedbackSystem:
    """
    Handles user feedback and analyzes
    previous interactions to extract
    useful learning.
    """

    def __init__(self):

        self.feedback_history = []


    # --------------------------------
    # ADD FEEDBACK
    # --------------------------------

    def add_feedback(self, feedback):

        feedback = feedback.lower().strip()

        if feedback not in ["good", "bad"]:

            return False

        self.feedback_history.append(
            feedback
        )

        return True


    # --------------------------------
    # GET LAST FEEDBACK
    # --------------------------------

    def get_last_feedback(self):

        if not self.feedback_history:

            return None

        return self.feedback_history[-1]


    # --------------------------------
    # FEEDBACK SUMMARY
    # --------------------------------

    def get_summary(self):

        good = self.feedback_history.count(
            "good"
        )

        bad = self.feedback_history.count(
            "bad"
        )

        return {
            "good": good,
            "bad": bad,
            "total": len(
                self.feedback_history
            )
        }


    # --------------------------------
    # ANALYZE FEEDBACK
    # --------------------------------

    def analyze_feedback(
        self,
        user_message,
        ai_response,
        feedback
    ):

        prompt = f"""
You are analyzing feedback for an AI assistant.

User question:
{user_message}

AI response:
{ai_response}

User feedback:
{feedback}

Your task is to identify what the AI assistant
should learn from this interaction.

If the feedback is GOOD:
Identify what response characteristics
were useful and should be continued.

If the feedback is BAD:
Identify what could be improved in future
responses.

Focus on useful long-term preferences such as:

- explanation style
- response length
- technical difficulty
- clarity
- examples
- formatting
- level of detail
- communication style

Do NOT create temporary or irrelevant memories.

Return ONLY one concise learning statement.

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

            learning = (
                response["message"]["content"]
                .strip()
            )

            return learning

        except Exception as e:

            print(
                "[Feedback analysis failed:",
                e,
                "]"
            )

            return None
