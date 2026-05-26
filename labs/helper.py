"""Helper functions for blog processing workflows."""

from pathlib import Path
import logging

from markdown import markdown
from weasyprint import HTML

from labs.agents.blog_post_translator.schema import LabPostTranslatorRequest
from labs.agents.blog_post_writer.schema import LabPostWriterRequest
from labs.contants import PUBLIC_PDF_DIR
from labs.frontmatter import ensure_required_frontmatter

logger = logging.getLogger(__name__)


def render_markdown_to_pdf(markdown_content: str, output_pdf_path: Path) -> None:
    """Render markdown content as a PDF file."""
    html = markdown(markdown_content, extensions=["fenced_code", "tables"])
    HTML(string=html).write_pdf(str(output_pdf_path))


def process_and_save_markdown(
    context: str,
    output_path: Path,
    writer_agent,
    translator_agent,
) -> None:
    """Generate reviewed + translated markdown and persist both files."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    PUBLIC_PDF_DIR.mkdir(parents=True, exist_ok=True)
    reviewed_markdown_written = False
    try:
        response = writer_agent.organize_notes(LabPostWriterRequest(context=context))
        normalized_reviewed_markdown = ensure_required_frontmatter(response.reviewed_markdown)
        output_path.write_text(normalized_reviewed_markdown, encoding="utf-8")
        reviewed_markdown_written = True

        translated_response = translator_agent.translate(
            LabPostTranslatorRequest(content=normalized_reviewed_markdown)
        )
        pt_br_output_path = output_path.with_name(f"{output_path.stem}_pt_br{output_path.suffix}")
        normalized_translated_markdown = ensure_required_frontmatter(
            translated_response.translated_markdown
        )
        pt_br_output_path.write_text(
            normalized_translated_markdown,
            encoding="utf-8",
        )
        reviewed_pdf_path = PUBLIC_PDF_DIR / f"{output_path.stem}.pdf"
        pt_br_pdf_path = PUBLIC_PDF_DIR / f"{pt_br_output_path.stem}.pdf"
        try:
            render_markdown_to_pdf(normalized_reviewed_markdown, reviewed_pdf_path)
            render_markdown_to_pdf(normalized_translated_markdown, pt_br_pdf_path)
        except Exception:
            logger.exception("PDF generation failed, markdown files were kept")
    except Exception as exc:
        if not reviewed_markdown_written:
            output_path.write_text(
                f"Failed to process markdown notes.\n\nError: {exc}",
                encoding="utf-8",
            )
        else:
            logger.exception("Processing failed after markdown write; preserving markdown file")


def list_output_files(base_dir: Path, extension: str, public_subdir: str) -> list[dict[str, str]]:
    """List output files with the requested extension in deterministic order."""
    if not base_dir.exists():
        return []

    normalized_extension = extension if extension.startswith(".") else f".{extension}"
    items: list[dict[str, str]] = []
    for path in sorted(base_dir.glob(f"*{normalized_extension}"), key=lambda p: p.name.lower()):
        if path.is_file():
            items.append(
                {
                    "filename": path.name,
                    "path": str(Path("public") / public_subdir / path.name),
                }
            )
    return items


def list_markdown_files(base_dir: Path) -> list[dict[str, str]]:
    """List markdown files in the output directory in deterministic order."""
    return list_output_files(base_dir, ".md", "markdown")
