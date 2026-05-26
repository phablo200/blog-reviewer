"""Service layer for blog post writing and revision workflows."""

from typing import Any

from fastapi import BackgroundTasks, HTTPException

from labs.agents.blog_post_writer.agent import LabPostWriterAgent
from labs.agents.blog_post_translator.agent import LabPostTranslatorAgent
from labs.agents.blog_reviewer.agent import LabReviewerAgent
from labs.agents.blog_reviewer.schema import LabReviewerRequest, LabReviewerResponse
from labs.contants import PUBLIC_MARKDOWN_DIR, PUBLIC_PDF_DIR
from labs.helper import list_markdown_files, list_output_files, process_and_save_markdown
from pathlib import Path


class LabPostService:
    """Orchestrates blog post generation/revision and file output."""

    def __init__(self) -> None:
        self.writer_agent = LabPostWriterAgent()
        self.translator_agent = LabPostTranslatorAgent()
        self.reviewer_agent = LabReviewerAgent()
        self.markdown_output_dir = PUBLIC_MARKDOWN_DIR
        self.pdf_output_dir = PUBLIC_PDF_DIR

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
        output_path = self.markdown_output_dir / output_name
        background_tasks.add_task(
            process_and_save_markdown,
            context,
            output_path,
            self.writer_agent,
            self.translator_agent,
        )

        return {
            "message": "Processing started.",
            "output_file": str(output_path),
        }

    def revise_blog_post(self, request: LabReviewerRequest) -> LabReviewerResponse:
        """Revise blog content through the revisor agent."""
        return self.reviewer_agent.revise(request)

    def list_markdown_outputs(self) -> dict[str, Any]:
        """List generated markdown outputs available in the public output folder."""
        items = list_markdown_files(self.markdown_output_dir)
        return {"items": items, "count": len(items)}

    def list_pdf_outputs(self) -> dict[str, Any]:
        """List generated PDF outputs available in the public output folder."""
        items = list_output_files(self.pdf_output_dir, ".pdf", "pdf")
        return {"items": items, "count": len(items)}
