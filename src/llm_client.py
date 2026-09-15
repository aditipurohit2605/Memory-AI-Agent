import os
from typing import Any, Dict, List, Optional

try:
    from google import genai
    from google.genai import types
except Exception:  # pragma: no cover - handled gracefully at runtime
    genai = None
    types = None

try:
    from ollama import chat as ollama_chat
except Exception:  # pragma: no cover - handled gracefully at runtime
    ollama_chat = None


def _is_cloud_mode() -> bool:
    provider = (os.getenv("MEMORYAI_LLM_PROVIDER") or "").strip().lower()
    explicit_cloud = provider in {"gemini", "google", "google-genai", "cloud"}
    return explicit_cloud or bool(
        os.getenv("GOOGLE_API_KEY")
        or os.getenv("GEMINI_API_KEY")
        or os.getenv("QDRANT_URL")
        or os.getenv("QDRANT_API_KEY")
    )


def _get_gemini_api_key() -> Optional[str]:
    return os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")


def _normalize_tool_call(tool_call: Any) -> Dict[str, Any]:
    if isinstance(tool_call, dict):
        function = tool_call.get("function") or {}
        if isinstance(function, dict):
            return {
                "function": {
                    "name": function.get("name"),
                    "arguments": function.get("arguments") or {},
                }
            }
        return {
            "function": {
                "name": tool_call.get("name"),
                "arguments": tool_call.get("arguments") or {},
            }
        }

    function = getattr(tool_call, "function", None)
    if function is not None:
        return {
            "function": {
                "name": getattr(function, "name", None),
                "arguments": getattr(function, "arguments", {}) or {},
            }
        }

    return {
        "function": {
            "name": getattr(tool_call, "name", None),
            "arguments": getattr(tool_call, "arguments", {}) or {},
        }
    }


def _gemini_call(model: str, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None, **kwargs: Any) -> Dict[str, Any]:
    if genai is None or types is None:
        raise RuntimeError("Google GenAI SDK is not installed. Install google-genai for cloud mode.")

    api_key = _get_gemini_api_key()
    if not api_key:
        raise RuntimeError("Missing GOOGLE_API_KEY or GEMINI_API_KEY for cloud mode.")

    client = genai.Client(api_key=api_key)
    system_instruction = None
    contents = []

    for message in messages:
        role = message.get("role", "user")
        content = message.get("content") or ""
        if role == "system":
            system_instruction = content
        else:
            contents.append(
                types.Content(
                    parts=[types.Part(text=content)],
                    role=role,
                )
            )

    config_kwargs: Dict[str, Any] = {}
    if "temperature" in kwargs:
        config_kwargs["temperature"] = kwargs["temperature"]
    if "max_tokens" in kwargs:
        config_kwargs["max_output_tokens"] = kwargs["max_tokens"]
    if "top_p" in kwargs:
        config_kwargs["top_p"] = kwargs["top_p"]
    if system_instruction:
        config_kwargs["system_instruction"] = system_instruction

    if tools:
        function_declarations = []
        for tool in tools:
            function = tool.get("function") or {}
            parameters = function.get("parameters") or {"type": "object", "properties": {}}
            declaration = types.FunctionDeclaration(
                name=function.get("name", ""),
                description=function.get("description", ""),
                parameters=parameters,
            )
            function_declarations.append(declaration)
        config_kwargs["tools"] = [types.Tool(function_declarations=function_declarations)]

    generation_config = types.GenerateContentConfig(**config_kwargs)
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generation_config,
    )

    candidate = response.candidates[0] if getattr(response, "candidates", None) else None
    parts = candidate.content.parts if candidate and getattr(candidate, "content", None) else []

    content_text = ""
    tool_calls = []

    for part in parts:
        if hasattr(part, "text") and getattr(part, "text"):
            content_text += getattr(part, "text")
        if hasattr(part, "function_call") and getattr(part, "function_call"):
            fn = part.function_call
            tool_calls.append(
                {
                    "function": {
                        "name": getattr(fn, "name", None),
                        "arguments": dict(fn.args) if getattr(fn, "args", None) else {},
                    }
                }
            )

    return {"message": {"content": content_text.strip(), "tool_calls": tool_calls}}


def _ollama_call(model: str, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None, **kwargs: Any) -> Dict[str, Any]:
    if ollama_chat is None:
        raise RuntimeError("Ollama Python client is not installed.")
    payload = {"model": model, "messages": messages}
    if tools:
        payload["tools"] = tools
    payload.update({key: value for key, value in kwargs.items() if value is not None})
    return ollama_chat(**payload)


def call_llm(model: str, messages: List[Dict[str, str]], tools: Optional[List[Dict[str, Any]]] = None, **kwargs: Any) -> Dict[str, Any]:
    """Route to Gemini when configured, otherwise safely fall back to local Ollama."""
    provider = (os.getenv("MEMORYAI_LLM_PROVIDER") or "").strip().lower()
    cloud_requested = provider in {"gemini", "google", "google-genai", "cloud"}
    cloud_available = bool(_get_gemini_api_key())

    if cloud_requested and not cloud_available:
        return _ollama_call(model, messages, tools=tools, **kwargs)

    if provider in {"", "local", "ollama"} and not _is_cloud_mode():
        return _ollama_call(model, messages, tools=tools, **kwargs)

    if cloud_available and (cloud_requested or _is_cloud_mode()):
        return _gemini_call(model, messages, tools=tools, **kwargs)

    return _ollama_call(model, messages, tools=tools, **kwargs)
