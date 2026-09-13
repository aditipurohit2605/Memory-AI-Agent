from ollama import chat

from src.tools import calculator


tools = [
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Calculate a mathematical expression.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "The mathematical expression to calculate."
                    }
                },
                "required": ["expression"]
            }
        }
    }
]


if __name__ == "__main__":
    response = chat(
        model="llama3.2:3b",
        messages=[
            {
                "role": "user",
                "content": "Calculate 25 * 4"
            }
        ],
        tools=tools
    )
    print(response)