"""Shared constants for core module."""

from enum import Enum

DEFAULT_GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.0


class LLM(str, Enum):
    OPENAI = "openai"
    GROQ = "groq"


class OpenAIModel(str, Enum):
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4O = "gpt-4o"


class GroqModel(str, Enum):
    LLAMA_4_SCOUT_17B = "meta-llama/llama-4-scout-17b-16e-instruct"
    LLAMA_3_1_8B_INSTANT = "llama-3.1-8b-instant"



LLM_MODELS: dict[LLM, set[str]] = {
    LLM.OPENAI: {model.value for model in OpenAIModel},
    LLM.GROQ: {model.value for model in GroqModel},
}
