"""Helper functions for blog processing workflows."""

from pathlib import Path

from markdown import markdown
from weasyprint import HTML

from blog.agents.blog_post_translator.schema import BlogPostTranslatorRequest
from blog.agents.blog_post_writer.schema import BlogPostWriterRequest
from blog.frontmatter import ensure_required_frontmatter


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
    try:
        response = writer_agent.organize_notes(BlogPostWriterRequest(context=context))
        normalized_reviewed_markdown = ensure_required_frontmatter(response.reviewed_markdown)
        output_path.write_text(normalized_reviewed_markdown, encoding="utf-8")
        render_markdown_to_pdf(normalized_reviewed_markdown, output_path.with_suffix(".pdf"))

        translated_response = translator_agent.translate(
            BlogPostTranslatorRequest(content=normalized_reviewed_markdown)
        )
        pt_br_output_path = output_path.with_name(f"{output_path.stem}_pt_br{output_path.suffix}")
        normalized_translated_markdown = ensure_required_frontmatter(
            translated_response.translated_markdown
        )
        pt_br_output_path.write_text(
            normalized_translated_markdown,
            encoding="utf-8",
        )
        render_markdown_to_pdf(
            normalized_translated_markdown,
            pt_br_output_path.with_suffix(".pdf"),
        )
    except Exception as exc:
        output_path.write_text(
            f"Failed to process markdown notes.\n\nError: {exc}",
            encoding="utf-8",
        )


def list_output_files(base_dir: Path, extension: str) -> list[dict[str, str]]:
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
                    "path": str(Path("public") / "markdowns" / path.name),
                }
            )
    return items


def list_markdown_files(base_dir: Path) -> list[dict[str, str]]:
    """List markdown files in the output directory in deterministic order."""
    return list_output_files(base_dir, ".md")
