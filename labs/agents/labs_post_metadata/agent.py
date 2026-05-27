"""Metadata agent implementation."""

from collections.abc import Mapping
import logging

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm_config import LLMProvider, build_chat_model

from .prompts import LabPostMetadataPrompt
from .schema import LabPostMetadataRequest, LabPostMetadataResponse


class LabPostMetadataAgent:
    """Generate frontmatter metadata from reviewed markdown content."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.llm = build_chat_model(LLMProvider.OPENAI)

    def generate(self, request: LabPostMetadataRequest) -> LabPostMetadataResponse:
        """Generate structured metadata with resilient fallback behavior."""
        messages = [
            SystemMessage(content=LabPostMetadataPrompt.build_system_prompt()),
            HumanMessage(content=request.content),
        ]

        try:
            structured_llm = self.llm.with_structured_output(LabPostMetadataResponse)
            response = structured_llm.invoke(messages)
        except Exception:
            self.logger.exception("labs_post_metadata: structured output failed")
            return LabPostMetadataResponse()

        if isinstance(response, Mapping):
            response_data = dict(response)
        else:
            response_data = {
                "title": getattr(response, "title", ""),
                "date": getattr(response, "date", ""),
                "summary": getattr(response, "summary", ""),
                "tags": getattr(response, "tags", []),
                "published": getattr(response, "published", True),
            }

        try:
            return LabPostMetadataResponse.model_validate(response_data)
        except Exception:
            self.logger.exception("labs_post_metadata: invalid structured metadata response")
            return LabPostMetadataResponse()
