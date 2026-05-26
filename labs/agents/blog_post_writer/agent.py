"""Blog Post Writer agent implementation."""

import logging

from langchain_core.messages import HumanMessage, SystemMessage

from labs.agents.blog_reviewer.agent import LabReviewerAgent
from labs.agents.blog_reviewer.schema import LabReviewerRequest
from core.llm_config import LLMProvider, build_chat_model

from .helper import enrich_context_with_repositories
from .prompts import LabPostWriterPrompt
from .schema import LabPostWriterRequest, LabPostWriterResponse


class LabPostWriterAgent:
    """Agent responsible for turning sketch notes into structured blog posts."""

    def __init__(self) -> None:
        """Initialize the chat model used by the agent."""
        self.logger = logging.getLogger(__name__)
        self.llm = build_chat_model(LLMProvider.OPENAI)
        self.blog_reviwer = LabReviewerAgent()

    def organize_notes(self, request: LabPostWriterRequest) -> LabPostWriterResponse:
        """Transform raw notes into a reviewed markdown blog post."""
        self.logger.info("blog_post_writer: starting organize_notes pipeline")
        enriched_context = enrich_context_with_repositories(request.context, self.logger)
        system_prompt = LabPostWriterPrompt.build_system_prompt()
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=enriched_context),
        ]

        self.logger.info("blog_post_writer: generating initial draft")
        response = self.llm.invoke(messages)
        current_markdown = str(getattr(response, "content", "")).strip()
        if not current_markdown:
            self.logger.warning(
                "blog_post_writer: initial draft empty, using fallback message"
            )
            current_markdown = "Unable to generate blog content from the provided notes."
        else:
            self.logger.info(
                "blog_post_writer: initial draft generated (chars=%s)",
                len(current_markdown),
            )

        # Run 3 full review/improvement cycles using both agents.
        for iteration in range(1, 4):
            self.logger.info("blog_post_writer: cycle %s/3 - requesting revision", iteration)
            try:
                revised = self.blog_reviwer.revise(
                    LabReviewerRequest(content=current_markdown)
                )
                self.logger.info(
                    (
                        "blog_post_writer: cycle %s/3 - revision received "
                        "(errors=%s, tips=%s, checklist=%s)"
                    ),
                    iteration,
                    len(revised.errors_found),
                    len(revised.improvement_tips),
                    len(revised.next_revision_checklist),
                )
            except Exception:
                self.logger.exception(
                    "blog_post_writer: cycle %s/3 - revision failed, stopping loop",
                    iteration,
                )
                break

            improvement_prompt = (
                "You are improving a blog post after editorial review.\n\n"
                "Apply all relevant corrections and suggestions while preserving the intent.\n\n"
                "Current post:\n"
                f"{current_markdown}\n\n"
                "Editor revised version:\n"
                f"{revised.revised_post}\n\n"
                "Errors found:\n"
                + "\n".join(f"- {item}" for item in revised.errors_found)
                + "\n\nImprovement tips:\n"
                + "\n".join(f"- {item}" for item in revised.improvement_tips)
                + "\n\nNext revision checklist:\n"
                + "\n".join(f"- {item}" for item in revised.next_revision_checklist)
                + "\n\nReturn only the final improved post in Markdown."
            )

            self.logger.info("blog_post_writer: cycle %s/3 - improving post", iteration)
            improved_response = self.llm.invoke(
                [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=improvement_prompt),
                ]
            )
            improved_markdown = str(getattr(improved_response, "content", "")).strip()
            if improved_markdown:
                current_markdown = improved_markdown
                self.logger.info(
                    "blog_post_writer: cycle %s/3 - improvement applied (chars=%s)",
                    iteration,
                    len(current_markdown),
                )
            else:
                current_markdown = revised.revised_post.strip() or current_markdown
                self.logger.warning(
                    (
                        "blog_post_writer: cycle %s/3 - empty improved response, "
                        "using revised fallback (chars=%s)"
                    ),
                    iteration,
                    len(current_markdown),
                )

        self.logger.info(
            "blog_post_writer: pipeline finished (final_chars=%s)",
            len(current_markdown),
        )
        return LabPostWriterResponse(reviewed_markdown=current_markdown)
