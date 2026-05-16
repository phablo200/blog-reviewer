"""Blog Post Translator agent implementation."""

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from core.llm_config import LLMProvider, build_chat_model

from .prompts import BlogPostTranslatorPrompt
from .schema import BlogPostTranslatorRequest, BlogPostTranslatorResponse


class BlogPostTranslatorAgent:
    """Agent responsible for translating reviewed posts to pt-BR."""

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.llm = build_chat_model(LLMProvider.OPENAI)

    def translate(self, request: BlogPostTranslatorRequest) -> BlogPostTranslatorResponse:
        """Translate reviewed English markdown into Brazilian Portuguese."""
        self.logger.info("blog_post_translator: starting translation")
        system_prompt = BlogPostTranslatorPrompt.build_system_prompt()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=request.content),
        ]

        response = self.llm.invoke(messages)
        translated_markdown = str(getattr(response, "content", "")).strip()

        if not translated_markdown:
            self.logger.warning(
                "blog_post_translator: empty translation, using source markdown fallback"
            )
            translated_markdown = request.content
        else:
            self.logger.info(
                "blog_post_translator: translation generated (chars=%s)",
                len(translated_markdown),
            )

        return BlogPostTranslatorResponse(translated_markdown=translated_markdown)
