
import os

from dotenv import load_dotenv
from mem0 import Memory


# --------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------

load_dotenv()


def build_memory_config():
    """Return the correct Mem0 configuration for local or cloud deployments."""
    google_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    qdrant_url = os.getenv("QDRANT_URL")
    qdrant_api_key = os.getenv("QDRANT_API_KEY")
    provider = (os.getenv("MEMORYAI_LLM_PROVIDER") or "").strip().lower()

    is_cloud = bool(
        os.getenv("RENDER")
        or google_key
        or qdrant_url
        or qdrant_api_key
        or provider in {"gemini", "google", "google-genai", "cloud"}
    )

    if is_cloud and google_key:
        llm_provider = "gemini"
        llm_config = {
            "model": os.getenv("GEMINI_MODEL", "gemini-3.6-flash"),
            "temperature": 0.2,
            "max_tokens": 1000,
            "api_key": google_key,
        }
    else:
        llm_provider = "ollama"
        llm_config = {
            "model": os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
            "temperature": 0.2,
            "max_tokens": 1000,
            "ollama_base_url": os.getenv("OLLAMA_HOST") or os.getenv("OLLAMA_BASE_URL"),
        }

    vector_cfg = {
        "collection_name": os.getenv("MEM0_COLLECTION", "memory-ai-agent"),
        "embedding_model_dims": 384,
    }
    if qdrant_url and qdrant_api_key:
        vector_cfg.update({
            "url": qdrant_url,
            "api_key": qdrant_api_key,
            "https": str(qdrant_url).startswith("https://"),
        })
    else:
        vector_cfg["path"] = os.getenv("QDRANT_PATH", "./qdrant_data")

    return {
        "llm": {
            "provider": llm_provider,
            "config": llm_config,
        },
        "embedder": {
            "provider": "huggingface",
            "config": {
                "model": os.getenv("EMBEDDER_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
            },
        },
        "vector_store": {
            "provider": "qdrant",
            "config": vector_cfg,
        },
    }


# --------------------------------
# START MEMORY SYSTEM
# --------------------------------

print("Starting Memory AI Agent...")


# --------------------------------
# MEM0 CONFIGURATION
# --------------------------------

config = build_memory_config()


# --------------------------------
# CREATE MEM0 MEMORY
# --------------------------------

memory = Memory.from_config(
    config
)


# --------------------------------
# ADD MEMORY
# --------------------------------

def add_memory(
    user_id,
    messages
):

    result = memory.add(
        messages,
        user_id=user_id
    )

    return result


# --------------------------------
# SEARCH MEMORY
# --------------------------------

def search_memory(
    user_id,
    query
):

    result = memory.search(
        query,
        filters={
            "user_id": user_id
        }
    )

    return result


# --------------------------------
# GET ALL USER MEMORIES
# --------------------------------

def get_all_memories(
    user_id
):

    result = memory.get_all(
        filters={
            "user_id": user_id
        }
    )

    return result


# --------------------------------
# GET ONE MEMORY
# --------------------------------

def get_memory(
    memory_id
):

    result = memory.get(
        memory_id
    )

    return result


# --------------------------------
# DELETE ONE MEMORY
# --------------------------------

def delete_memory(
    memory_id
):

    result = memory.delete(
        memory_id
    )

    return result


# --------------------------------
# DELETE ALL USER MEMORIES
# --------------------------------

def delete_all_memories(
    user_id
):

    result = memory.delete_all(
        user_id=user_id
    )

    return result


# --------------------------------
# MEMORY HISTORY
# --------------------------------

def get_memory_history(
    memory_id
):

    result = memory.history(
        memory_id
    )

    return result


# ==============================================
# TEST MEMORY SYSTEM
# ==============================================

if __name__ == "__main__":

    user_id = "aditi"


    messages = [

        {
            "role": "user",
            "content": (
                "I prefer Python for AI "
                "and machine learning projects."
            )
        },

        {
            "role": "assistant",
            "content": (
                "I will remember that preference."
            )
        }

    ]


    print(
        "\nAdding memory..."
    )


    result = add_memory(
        user_id,
        messages
    )


    print(
        "\nMemory added:"
    )

    print(
        result
    )


    print(
        "\nSearching memory..."
    )


    search_result = search_memory(
        user_id,
        "What programming language "
        "does the user prefer?"
    )


    print(
        "\nMemory search result:"
    )

    print(
        search_result
    )