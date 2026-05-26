"""Blog Reviewer agent implementation."""

from collections.abc import Mapping
import logging
import re

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm_config import LLMProvider, build_chat_model

from .prompts import LabReviewerPrompt
from .schema import (
    LabReviewerRequest,
    LabReviewerResponse,
    LabReviewerStructuredResponse,
)


class LabReviewerAgent:
    """Agent responsible for revising blog posts in Markdown."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.llm = build_chat_model(LLMProvider.GROQ)

    @staticmethod
    def _normalize_list_field(value: object) -> list[str]:
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        if isinstance(value, str):
            lines = [line.strip() for line in value.splitlines() if line.strip()]
            normalized: list[str] = []
            for line in lines:
                cleaned = re.sub(r"^[-*]\s*", "", line).strip()
                if cleaned:
                    normalized.append(cleaned)
            return normalized
        return []

    def revise(self, request: LabReviewerRequest) -> LabReviewerResponse:
        system_prompt = LabReviewerPrompt.build_system_prompt()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=request.content),
        ]

        try:
            structured_llm = self.llm.with_structured_output(LabReviewerStructuredResponse)
            response = structured_llm.invoke(messages)
        except Exception:
            self.logger.exception(
                "blog_reviewer: structured output failed, falling back to raw generation"
            )
            raw_response = self.llm.invoke(messages)
            raw_text = str(getattr(raw_response, "content", "")).strip()
            return LabReviewerResponse(
                revised_post=raw_text or request.content,
                errors_found=[],
                improvement_tips=[],
                next_revision_checklist=[],
            )

        if isinstance(response, Mapping):
            response_data = dict(response)
        else:
            response_data = {
                "revised_post": getattr(response, "revised_post", ""),
                "errors_found": getattr(response, "errors_found", []),
                "improvement_tips": getattr(response, "improvement_tips", []),
                "next_revision_checklist": getattr(
                    response, "next_revision_checklist", []
                ),
            }

        response_data["errors_found"] = self._normalize_list_field(
            response_data.get("errors_found")
        )
        response_data["improvement_tips"] = self._normalize_list_field(
            response_data.get("improvement_tips")
        )
        response_data["next_revision_checklist"] = self._normalize_list_field(
            response_data.get("next_revision_checklist")
        )

        structured = LabReviewerStructuredResponse.model_validate(response_data)
        return LabReviewerResponse(
            revised_post=structured.revised_post,
            errors_found=structured.errors_found,
            improvement_tips=structured.improvement_tips,
            next_revision_checklist=structured.next_revision_checklist,
        )
