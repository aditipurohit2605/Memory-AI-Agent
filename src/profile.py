
import json
import re

from src.llm_client import call_llm

from src.memory import get_all_memories


MODEL = "llama3.2:3b"


# ========================================
# DEFAULT PROFILE
# ========================================

DEFAULT_PROFILE = {
    "skills": [],
    "interests": [],
    "goals": [],
    "preferences": [],
    "projects": [],
    "other": []
}


# ========================================
# CLEAN JSON RESPONSE
# ========================================

def clean_json_response(text):
    """
    Extract and parse JSON from an LLM response.

    Handles:
    - normal JSON
    - ```json ... ```
    - ``` ... ```
    - extra text surrounding JSON
    """

    if not text:
        return None

    text = text.strip()

    # --------------------------------
    # Remove markdown code fences
    # --------------------------------

    text = re.sub(
        r"```json\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(
        r"```\s*",
        "",
        text
    )

    text = text.strip()

    # --------------------------------
    # Try direct JSON parsing
    # --------------------------------

    try:

        profile = json.loads(text)

        if isinstance(profile, dict):
            return normalize_profile(profile)

    except json.JSONDecodeError:
        pass

    # --------------------------------
    # Find JSON object inside response
    # --------------------------------

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:

        json_text = text[
            start:end + 1
        ]

        try:

            profile = json.loads(
                json_text
            )

            if isinstance(profile, dict):
                return normalize_profile(profile)

        except json.JSONDecodeError:

            pass

    print(
        "[Profile JSON parsing failed]"
    )

    return None


# ========================================
# NORMALIZE PROFILE
# ========================================

def normalize_profile(profile):
    """
    Make sure the profile always contains
    the expected categories.
    """

    normalized = {}

    for category in DEFAULT_PROFILE:

        value = profile.get(
            category,
            []
        )

        if isinstance(value, list):

            cleaned_items = []

            for item in value:

                if item is not None:

                    item = str(
                        item
                    ).strip()

                    if item:
                        cleaned_items.append(
                            item
                        )

            normalized[
                category
            ] = cleaned_items

        else:

            normalized[
                category
            ] = []

    return normalized


# ========================================
# GET USER PROFILE
# ========================================

def get_user_profile(user_id):
    """
    Generate a structured user profile
    from long-term memories.
    """

    memories_data = get_all_memories(
        user_id
    )

    memories = memories_data.get(
        "results",
        []
    )

    # --------------------------------
    # No memories
    # --------------------------------

    if not memories:

        return DEFAULT_PROFILE.copy()

    # --------------------------------
    # Prepare memory text
    # --------------------------------

    memory_text = ""

    for item in memories:

        memory = item.get(
            "memory",
            ""
        )

        if memory:

            memory_text += (
                "- "
                + memory
                + "\n"
            )

    # --------------------------------
    # Profile generation prompt
    # --------------------------------

    prompt = f"""
You are the user profile module of MemoryAI.

Create a structured profile using ONLY
the user's long-term memories below.

USER MEMORIES:

{memory_text}

Organize the information into exactly
these categories:

skills
interests
goals
preferences
projects
other

Rules:

1. Only use information present in the memories.
2. Do not invent information.
3. Remove duplicate information.
4. Keep each item short.
5. If a category has no information,
   return an empty list.
6. Do not add extra categories.
7. Return ONLY valid JSON.
8. Do NOT use markdown.
9. Do NOT write explanations.

Return exactly this structure:

{{
    "skills": [],
    "interests": [],
    "goals": [],
    "preferences": [],
    "projects": [],
    "other": []
}}
"""

    # --------------------------------
    # Ask Ollama
    # --------------------------------

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

        profile_text = (
            response[
                "message"
            ][
                "content"
            ]
            .strip()
        )

        profile = clean_json_response(
            profile_text
        )

        if profile:

            return profile

        return DEFAULT_PROFILE.copy()

    except Exception as e:

        print(
            "[Profile generation failed:]",
            e
        )

        return DEFAULT_PROFILE.copy()


# ========================================
# UPDATE USER PROFILE
# ========================================

def update_user_profile(user_id):
    """
    Regenerate the user's profile after
    new long-term memory has been added.
    """

    profile = get_user_profile(
        user_id
    )

    print(
        "[User profile automatically updated]"
    )

    return profile


# ========================================
# DISPLAY PROFILE
# ========================================

def display_profile(user_id):

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

    print(
        json.dumps(
            profile,
            indent=4
        )
    )

    print(
        "================================"
    )


# ========================================
# TEST
# ========================================

if __name__ == "__main__":

    print(
        "================================"
    )

    print(
        "       MEMORY AI PROFILE"
    )

    print(
        "================================"
    )

    user_id = input(
        "\nEnter user ID: "
    ).strip()

    display_profile(
        user_id
    )

