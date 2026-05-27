import core.llm_config as llm_config
from core.llm_config import AgentRole, LLMProvider


class _ModelStub:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def test_build_chat_model_for_agent_uses_role_specific_values(monkeypatch) -> None:
    monkeypatch.setattr(llm_config, "ChatOpenAI", _ModelStub)
    monkeypatch.setattr(llm_config, "ChatGroq", _ModelStub)

    monkeypatch.setenv("LLM_POST_WRITER_PROVIDER", "openai")
    monkeypatch.setenv("LLM_POST_WRITER_MODEL", "gpt-4o")
    monkeypatch.setenv("LLM_POST_WRITER_TEMPERATURE", "0.42")

    model = llm_config.build_chat_model_for_agent(AgentRole.POST_WRITER)

    assert model.kwargs["model"] == "gpt-4o"
    assert model.kwargs["temperature"] == 0.42


def test_build_chat_model_for_agent_falls_back_to_global_model(monkeypatch) -> None:
    monkeypatch.setattr(llm_config, "ChatOpenAI", _ModelStub)
    monkeypatch.setattr(llm_config, "ChatGroq", _ModelStub)

    monkeypatch.delenv("LLM_METADATA_MODEL", raising=False)
    monkeypatch.setenv("LLM_METADATA_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-4o-mini")

    model = llm_config.build_chat_model_for_agent(AgentRole.METADATA)
    assert model.kwargs["model"] == "gpt-4o-mini"


def test_resolve_model_invalid_role_model_fallback(monkeypatch) -> None:
    monkeypatch.setenv("LLM_REVIEWER_PROVIDER", "groq")
    monkeypatch.setenv("LLM_REVIEWER_MODEL", "gpt-4o")
    monkeypatch.setenv("GROQ_MODEL", "llama-3.1-8b-instant")

    resolved = llm_config._resolve_model(AgentRole.REVIEWER, LLMProvider.GROQ)
    assert resolved == "llama-3.1-8b-instant"
