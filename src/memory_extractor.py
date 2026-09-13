from ollama import chat
import re


MODEL = "llama3.2:3b"


VALID_CATEGORIES = [
    "fact",
    "preference",
    "goal",
    "skill",
    "project",
    "learned_behavior",
    "other"
]


def extract_name_memory(user_message):
    """
    Detect explicit name statements using simple rules.
    This makes important identity information reliable.
    """

    message = user_message.strip()

    patterns = [
        r"\bmy name is\s+([A-Za-z][A-Za-z .'-]{1,40})\b",
        r"\bmy name's\s+([A-Za-z][A-Za-z .'-]{1,40})\b",
        r"\bcall me\s+([A-Za-z][A-Za-z .'-]{1,40})\b",
        r"\bi am\s+([A-Za-z][A-Za-z .'-]{1,40})\b",
        r"\bi'm\s+([A-Za-z][A-Za-z .'-]{1,40})\b"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            message,
            re.IGNORECASE
        )

        if match:

            name = match.group(1).strip()

            # Avoid treating obvious non-name phrases as names.
            invalid_names = {
                "a student",
                "a developer",
                "a student of",
                "happy",
                "fine",
                "good",
                "working",
                "learning",
                "interested"
            }

            if name.lower() in invalid_names:
                continue

            # Keep only the first sensible name words.
            name = name.rstrip(".,!?")

            return (
                "CATEGORY: fact\n"
                f"MEMORY: User's name is {name}"
            )

    return None


def extract_memory(user_message):
    """
    Extract useful long-term information from
    a user's message and classify it.
    """

    # -------------------------------------------------
    # STEP 1: Handle explicit name statements reliably
    # -------------------------------------------------

    name_memory = extract_name_memory(user_message)

    if name_memory:
        return name_memory

    # -------------------------------------------------
    # STEP 2: Use Llama for other types of memories
    # -------------------------------------------------

    prompt = f"""
You are the memory extraction module of MemoryAI.

Read the user's message and identify useful
long-term information that should be remembered.

USER MESSAGE:
{user_message}

IMPORTANT:
Personal identity facts are useful long-term memories.

For example:

"My name is Aditi"
"My name's Aditi"
"Call me Aditi"

must be remembered as:

CATEGORY: fact
MEMORY: User's name is Aditi

Useful memory categories:

1. fact
   Stable information about the user.

2. preference
   Something the user prefers or likes.

3. goal
   Something the user wants to achieve.

4. skill
   A skill or technology the user knows
   or is learning.

5. project
   A project the user is working on.

6. learned_behavior
   A response or interaction style that the
   AI should follow in future conversations.

7. other
   Useful long-term information that does not
   fit the categories above.

Examples of useful memories:

"My name is Aditi"
"I prefer Python"
"I am learning machine learning"
"My goal is to become an AI engineer"
"I am working on a RAG project"
"I prefer simple explanations"

These should be saved.

DO NOT save:

- greetings alone
- general questions
- temporary questions
- factual questions
- casual conversation
- random statements
- information about unrelated people

If there is NO useful long-term information,
return exactly:

NO_MEMORY

If useful information exists, return ONLY:

CATEGORY: <category>
MEMORY: <one concise memory statement>

The category MUST be one of:

fact
preference
goal
skill
project
learned_behavior
other

Do not explain your reasoning.
Do not use markdown.
Do not add extra text.

USER MESSAGE:
{user_message}
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

        result = (
            response["message"]["content"]
            .strip()
        )

        if result == "NO_MEMORY":
            return result

        return clean_memory(result)

    except Exception as e:

        print(
            "[Memory extraction failed:]",
            e
        )

        return "NO_MEMORY"


def clean_memory(result):
    """
    Validate and clean the extracted memory.
    """

    lines = result.splitlines()

    category = None
    memory_text = None

    for line in lines:

        if line.upper().startswith(
            "CATEGORY:"
        ):

            category = (
                line
                .split(":", 1)[1]
                .strip()
                .lower()
            )

        elif line.upper().startswith(
            "MEMORY:"
        ):

            memory_text = (
                line
                .split(":", 1)[1]
                .strip()
            )

    if (
        category not in VALID_CATEGORIES
        or not memory_text
    ):

        return "NO_MEMORY"

    return (
        f"CATEGORY: {category}\n"
        f"MEMORY: {memory_text}"
    )


def get_memory_category(memory_result):
    """
    Extract the category from a memory result.
    """

    if not memory_result:
        return None

    for line in memory_result.splitlines():

        if line.upper().startswith(
            "CATEGORY:"
        ):

            category = (
                line
                .split(":", 1)[1]
                .strip()
                .lower()
            )

            if category in VALID_CATEGORIES:
                return category

    return None


def get_memory_text(memory_result):
    """
    Extract only the memory statement.
    """

    if not memory_result:
        return None

    for line in memory_result.splitlines():

        if line.upper().startswith(
            "MEMORY:"
        ):

            return (
                line
                .split(":", 1)[1]
                .strip()
            )

    return None


if __name__ == "__main__":

    print(
        "================================"
    )

    print(
        "      MEMORY AI EXTRACTOR"
    )

    print(
        "================================"
    )

    user_message = input(
        "\nEnter a message: "
    )

    result = extract_memory(
        user_message
    )

    print(
        "\nExtracted memory:"
    )

    print(
        "-----------------"
    )

    print(result)

    print(
        "\nCategory:",
        get_memory_category(result)
    )

    print(
        "Memory:",
        get_memory_text(result)
    )