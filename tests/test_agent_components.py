from types import SimpleNamespace

from src.llm_client import call_llm
from src.tools import calculator
from src.conversation import ConversationMemory
from src.feedback import FeedbackSystem
from src.planner import create_plan
from src.evaluator import evaluate_response
from src.memory import build_memory_config
from ui.state import check_ollama_status


# ========================================
# TEST OLLAMA MODEL DETECTION
# ========================================

def test_ollama_status_supports_name_and_model_fields(monkeypatch):
    class FakeOllama:
        @staticmethod
        def list():
            return {
                "models": [
                    {"name": "llama3.2:3b"},
                    {"model": "mistral:7b"},
                ]
            }

    monkeypatch.setitem(__import__("sys").modules, "ollama", SimpleNamespace(list=FakeOllama.list))

    running, available = check_ollama_status("llama3.2:3b")

    assert running is True
    assert available is True


# ========================================
# TEST CALCULATOR
# ========================================

def test_calculator():

    result = calculator("25 * 4")

    assert result == "100"


def test_calculator_addition():

    result = calculator("10 + 20")

    assert result == "30"


def test_calculator_invalid_input():

    result = calculator(
        "import os"
    )

    assert result == (
        "Invalid mathematical expression."
    )


# ========================================
# TEST SHORT-TERM MEMORY
# ========================================

def test_conversation_memory():

    conversation = ConversationMemory(
        max_messages=3
    )

    conversation.add_user_message(
        "Hello"
    )

    conversation.add_assistant_message(
        "Hi!"
    )

    conversation.add_user_message(
        "How are you?"
    )

    messages = (
        conversation.get_messages()
    )

    assert len(messages) == 3


def test_conversation_memory_limit():

    conversation = ConversationMemory(
        max_messages=2
    )

    conversation.add_user_message(
        "Message 1"
    )

    conversation.add_assistant_message(
        "Message 2"
    )

    conversation.add_user_message(
        "Message 3"
    )

    messages = (
        conversation.get_messages()
    )

    assert len(messages) == 2

    assert messages[0]["content"] == (
        "Message 2"
    )


# ========================================
# TEST FEEDBACK SYSTEM
# ========================================

def test_feedback_good():

    feedback = FeedbackSystem()

    result = feedback.add_feedback(
        "good"
    )

    assert result is True

    assert (
        feedback.get_last_feedback()
        == "good"
    )


def test_feedback_bad():

    feedback = FeedbackSystem()

    result = feedback.add_feedback(
        "bad"
    )

    assert result is True

    assert (
        feedback.get_last_feedback()
        == "bad"
    )


def test_feedback_invalid():

    feedback = FeedbackSystem()

    result = feedback.add_feedback(
        "average"
    )

    assert result is False


def test_feedback_summary():

    feedback = FeedbackSystem()

    feedback.add_feedback("good")
    feedback.add_feedback("good")
    feedback.add_feedback("bad")

    summary = (
        feedback.get_summary()
    )

    assert summary["good"] == 2
    assert summary["bad"] == 1
    assert summary["total"] == 3


# ========================================
# TEST PLANNER
# ========================================

def test_planner():

    plan = create_plan(
        "What is Python?"
    )

    assert plan is not None

    assert len(plan) > 0


# ========================================
# TEST EVALUATOR
# ========================================

def test_evaluator():

    evaluation = evaluate_response(
        "Explain Python simply.",
        "Python is a programming language "
        "used to build software and AI systems."
    )

    assert evaluation is not None

    assert len(evaluation) > 0


def test_build_memory_config_uses_gemini_for_cloud(monkeypatch):
    monkeypatch.setenv("GOOGLE_API_KEY", "cloud-key")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OLLAMA_HOST", raising=False)

    config = build_memory_config()

    assert config["llm"]["provider"] == "gemini"
    assert config["llm"]["config"]["model"] == "gemini-3.6-flash"
    assert config["llm"]["config"]["api_key"] == "cloud-key"


def test_build_memory_config_defaults_to_local_ollama(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("QDRANT_URL", raising=False)
    monkeypatch.delenv("QDRANT_API_KEY", raising=False)

    config = build_memory_config()

    assert config["llm"]["provider"] == "ollama"
    assert config["vector_store"]["provider"] == "qdrant"
    assert config["vector_store"]["config"]["path"] == "./qdrant_data"


def test_call_llm_uses_local_ollama_when_render_has_no_cloud_key(monkeypatch):
    monkeypatch.setenv("RENDER", "true")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("MEMORYAI_LLM_PROVIDER", raising=False)

    observed = {}

    def fake_ollama_call(model, messages, tools=None, **kwargs):
        observed["used"] = "ollama"
        return {"message": {"content": "fallback response"}}

    monkeypatch.setattr("src.llm_client._ollama_call", fake_ollama_call)

    result = call_llm("llama3.2:3b", [{"role": "user", "content": "Hi"}])

    assert observed["used"] == "ollama"
    assert result["message"]["content"] == "fallback response"


def test_call_llm_falls_back_to_ollama_on_gemini_503(monkeypatch):
    monkeypatch.setenv("MEMORYAI_LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    observed = {"gemini_calls": 0, "ollama_calls": 0}

    def fake_gemini_call(model, messages, tools=None, **kwargs):
        observed["gemini_calls"] += 1
        raise RuntimeError("503 UNAVAILABLE: This model is currently experiencing high demand.")

    def fake_ollama_call(model, messages, tools=None, **kwargs):
        observed["ollama_calls"] += 1
        return {"message": {"content": "local fallback"}}

    monkeypatch.setattr("src.llm_client._gemini_call", fake_gemini_call)
    monkeypatch.setattr("src.llm_client._ollama_call", fake_ollama_call)

    result = call_llm("gemini-3.6-flash", [{"role": "user", "content": "Hi"}])

    assert observed["gemini_calls"] >= 1
    assert observed["ollama_calls"] >= 1
    assert result["message"]["content"] == "local fallback"


def test_call_llm_returns_fallback_when_all_backends_fail(monkeypatch):
    monkeypatch.setenv("MEMORYAI_LLM_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    def fake_gemini_call(model, messages, tools=None, **kwargs):
        raise RuntimeError("503 UNAVAILABLE")

    def fake_ollama_call(model, messages, tools=None, **kwargs):
        raise RuntimeError("Ollama not reachable")

    monkeypatch.setattr("src.llm_client._gemini_call", fake_gemini_call)
    monkeypatch.setattr("src.llm_client._ollama_call", fake_ollama_call)

    result = call_llm("gemini-3.6-flash", [{"role": "user", "content": "What is 2+2?"}])

    assert "temporarily unable to answer" in result["message"]["content"].lower()
    assert "2+2" in result["message"]["content"]


# ========================================
# TEST SUITE MESSAGE
# ========================================

print(
    "\nMemoryAI component tests loaded."
)