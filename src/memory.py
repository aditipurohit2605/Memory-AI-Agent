
from dotenv import load_dotenv
from mem0 import Memory


# --------------------------------
# LOAD ENVIRONMENT VARIABLES
# --------------------------------

load_dotenv()


# --------------------------------
# START MEMORY SYSTEM
# --------------------------------

print("Starting Memory AI Agent...")


# --------------------------------
# MEM0 CONFIGURATION
# --------------------------------

config = {

    "llm": {
        "provider": "ollama",
        "config": {
            "model": "llama3.2:3b",
            "temperature": 0.2,
            "max_tokens": 1000
        }
    },

    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "sentence-transformers/all-MiniLM-L6-v2"
        }
    },

    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "memory-ai-agent",
            "embedding_model_dims": 384,
            "path": "./qdrant_data"
        }
    }
}


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