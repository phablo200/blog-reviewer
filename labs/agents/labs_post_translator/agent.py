"""Blog Post Translator agent implementation."""

import logging

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from core.llm_config import AgentRole, LLMConfig

from .prompts import LabPostTranslatorPrompt
from .schema import LabPostTranslatorRequest, LabPostTranslatorResponse


class LabPostTranslatorAgent:
    """Agent responsible for translating reviewed posts to pt-BR."""

    def __init__(self, llm: BaseChatModel | None = None) -> None:
        self.logger = logging.getLogger(__name__)
        self.agent_name = AgentRole.TRANSLATOR
        self.llm = llm or LLMConfig.build_chat_model_for_agent(AgentRole.TRANSLATOR)

    def translate(self, request: LabPostTranslatorRequest) -> LabPostTranslatorResponse:
        """Translate reviewed English markdown into Brazilian Portuguese."""
        self.logger.info("agent=%s | starting translation", self.agent_name)
        system_prompt = LabPostTranslatorPrompt.build_system_prompt()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=request.content),
        ]

        response = self.llm.invoke(messages)
        translated_markdown = str(getattr(response, "content", "")).strip()

        if not translated_markdown:
            self.logger.warning(
                "agent=%s | empty translation, using source markdown fallback",
                self.agent_name,
            )
            translated_markdown = request.content
        else:
            self.logger.info(
                "agent=%s | translation generated (chars=%s)",
                self.agent_name,
                len(translated_markdown),
            )

        return LabPostTranslatorResponse(translated_markdown=translated_markdown)
