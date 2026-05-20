"""Service layer for blog post writing and revision workflows."""

from pathlib import Path

from fastapi import BackgroundTasks, HTTPException

from blog.agents.blog_post_translator.agent import BlogPostTranslatorAgent
from blog.agents.blog_post_translator.schema import BlogPostTranslatorRequest
from blog.agents.blog_post_writer.agent import BlogPostWriterAgent
from blog.agents.blog_post_writer.schema import BlogPostWriterRequest
from blog.agents.blog_reviewer.agent import BlogReviewerAgent
from blog.agents.blog_reviewer.schema import BlogReviewerRequest, BlogReviewerResponse
from blog.contants import BLOG_POSTS_OUTPUT_DIR
from blog.frontmatter import ensure_required_frontmatter


class BlogPostService:
    """Orchestrates blog post generation/revision and file output."""

    def __init__(self) -> None:
        self.writer_agent = BlogPostWriterAgent()
        self.translator_agent = BlogPostTranslatorAgent()
        self.reviewer_agent = BlogReviewerAgent()
        self.output_dir = BLOG_POSTS_OUTPUT_DIR

    def enqueue_markdown_organization(
        self, background_tasks: BackgroundTasks, filename: str, context: str
    ) -> dict[str, str]:
        """Validate file metadata and enqueue async processing for markdown generation."""
        original_name = Path(filename or "")
        safe_name = original_name.name
        if not safe_name:
            raise HTTPException(status_code=400, detail="A filename is required.")

        filename = safe_name
        if not filename.lower().endswith(".md"):
            raise HTTPException(status_code=400, detail="Only .md files are supported.")

        output_name = f"{original_name.stem}_reviewd{original_name.suffix or '.md'}"
        output_path = self.output_dir / output_name
        background_tasks.add_task(self._process_and_save_markdown, context, output_path)

        return {
            "message": "Processing started.",
            "output_file": str(output_path),
        }

    def revise_blog_post(self, request: BlogReviewerRequest) -> BlogReviewerResponse:
        """Revise blog content through the revisor agent."""
        return self.reviewer_agent.revise(request)

    def _process_and_save_markdown(self, context: str, output_path: Path) -> None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            response = self.writer_agent.organize_notes(BlogPostWriterRequest(context=context))
            normalized_reviewed_markdown = ensure_required_frontmatter(response.reviewed_markdown)
            output_path.write_text(normalized_reviewed_markdown, encoding="utf-8")

            translated_response = self.translator_agent.translate(
                BlogPostTranslatorRequest(content=normalized_reviewed_markdown)
            )
            pt_br_output_path = output_path.with_name(
                f"{output_path.stem}_pt_br{output_path.suffix}"
            )
            normalized_translated_markdown = ensure_required_frontmatter(
                translated_response.translated_markdown
            )
            pt_br_output_path.write_text(
                normalized_translated_markdown,
                encoding="utf-8",
            )
        except Exception as exc:
            output_path.write_text(
                f"Failed to process markdown notes.\n\nError: {exc}",
                encoding="utf-8",
            )
