import os
from enum import Enum
from typing import Callable

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI

from core.contants import (
    DEFAULT_GROQ_MODEL,
    DEFAULT_OPENAI_MODEL,
    DEFAULT_TEMPERATURE,
)

load_dotenv()


class LLMProvider(str, Enum):
    GROQ = "groq"
    OPENAI = "openai"


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
