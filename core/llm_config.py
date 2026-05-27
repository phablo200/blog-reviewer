import os
from enum import Enum
import logging
from typing import Callable

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from core.contants import (
    DEFAULT_GROQ_MODEL,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_TEMPERATURE,
    LLM,
    LLM_MODELS,
)

load_dotenv()
logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    GROQ = "groq"
    OPENAI = "openai"


class AgentRole(str, Enum):
    POST_WRITER = "post_writer"
    CODE_EXAMPLE = "code_example"
    REVIEWER = "reviewer"
    METADATA = "metadata"
    TRANSLATOR = "translator"


def _build_groq_chat() -> BaseChatModel:
    model_name = os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)
    temperature = float(os.getenv("GROQ_TEMPERATURE", str(DEFAULT_TEMPERATURE)))
    api_key = os.getenv("GROQ_API_KEY")
    return ChatGroq(
        model=model_name,
        temperature=temperature,
        api_key=api_key,
    )


def _build_openai_chat() -> BaseChatModel:
    model_name = os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    temperature = float(os.getenv("OPENAI_TEMPERATURE", str(DEFAULT_TEMPERATURE)))
    api_key = os.getenv("OPENAI_API_KEY")
    return ChatOpenAI(
        model=model_name,
        temperature=temperature,
        openai_api_key=api_key,
    )


MODEL_BUILDERS: dict[LLMProvider, Callable[[], BaseChatModel]] = {
    LLMProvider.GROQ: _build_groq_chat,
    LLMProvider.OPENAI: _build_openai_chat,
}


def build_chat_model(provider: LLMProvider = LLMProvider.GROQ) -> BaseChatModel:
    return MODEL_BUILDERS[provider]()


ROLE_DEFAULT_PROVIDER: dict[AgentRole, LLMProvider] = {
    AgentRole.POST_WRITER: LLMProvider.OPENAI,
    AgentRole.CODE_EXAMPLE: LLMProvider.OPENAI,
    AgentRole.REVIEWER: LLMProvider.GROQ,
    AgentRole.METADATA: LLMProvider.OPENAI,
    AgentRole.TRANSLATOR: LLMProvider.OPENAI,
}


def _provider_default_model(provider: LLMProvider) -> str:
    if provider == LLMProvider.OPENAI:
        return os.getenv("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
    return os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL)


def _provider_default_temperature(provider: LLMProvider) -> float:
    raw = (
        os.getenv("OPENAI_TEMPERATURE", str(DEFAULT_TEMPERATURE))
        if provider == LLMProvider.OPENAI
        else os.getenv("GROQ_TEMPERATURE", str(DEFAULT_TEMPERATURE))
    )
    try:
        value = float(raw)
    except (TypeError, ValueError):
        logger.warning(
            "llm_config: invalid global temperature '%s' for provider '%s'; using default=%s",
            raw,
            provider.value,
            DEFAULT_TEMPERATURE,
        )
        return DEFAULT_TEMPERATURE
    if not 0 <= value <= 1:
        logger.warning(
            "llm_config: global temperature out of range for provider '%s'; using default=%s",
            provider.value,
            DEFAULT_TEMPERATURE,
        )
        return DEFAULT_TEMPERATURE
    return value


def _resolve_provider(role: AgentRole) -> LLMProvider:
    key = f"LLM_{role.value.upper()}_PROVIDER"
    raw_provider = os.getenv(key, ROLE_DEFAULT_PROVIDER[role].value).strip().lower()
    try:
        return LLMProvider(raw_provider)
    except ValueError:
        fallback = ROLE_DEFAULT_PROVIDER[role]
        logger.warning(
            "llm_config: invalid provider '%s' for role '%s'; using '%s'",
            raw_provider,
            role.value,
            fallback.value,
        )
        return fallback


def _resolve_model(role: AgentRole, provider: LLMProvider) -> str:
    key = f"LLM_{role.value.upper()}_MODEL"
    role_model = os.getenv(key, "").strip()
    candidate = role_model or _provider_default_model(provider)
    allowed = LLM_MODELS[LLM(provider.value)]
    if candidate not in allowed:
        fallback = _provider_default_model(provider)
        logger.warning(
            "llm_config: model '%s' invalid for provider '%s' (role=%s); using '%s'",
            candidate,
            provider.value,
            role.value,
            fallback,
        )
        return fallback
    return candidate


def _resolve_temperature(role: AgentRole, provider: LLMProvider) -> float:
    key = f"LLM_{role.value.upper()}_TEMPERATURE"
    raw = os.getenv(key, "").strip()
    if not raw:
        return _provider_default_temperature(provider)
    try:
        value = float(raw)
    except ValueError:
        logger.warning(
            "llm_config: invalid temperature '%s' for role '%s'; using provider default",
            raw,
            role.value,
        )
        return _provider_default_temperature(provider)
    if not 0 <= value <= 1:
        logger.warning(
            "llm_config: temperature out of range for role '%s'; using provider default",
            role.value,
        )
        return _provider_default_temperature(provider)
    return value


def build_chat_model_for_agent(agent_role: AgentRole) -> BaseChatModel:
    provider = _resolve_provider(agent_role)
    model = _resolve_model(agent_role, provider)
    temperature = _resolve_temperature(agent_role, provider)

    if provider == LLMProvider.OPENAI:
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )
    return ChatGroq(
        model=model,
        temperature=temperature,
        api_key=os.getenv("GROQ_API_KEY"),
    )
