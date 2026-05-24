"""Helper functions for blog processing workflows."""

from pathlib import Path

from blog.agents.blog_post_translator.schema import BlogPostTranslatorRequest
from blog.agents.blog_post_writer.schema import BlogPostWriterRequest
from blog.frontmatter import ensure_required_frontmatter


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
    except Exception as exc:
        output_path.write_text(
            f"Failed to process markdown notes.\n\nError: {exc}",
            encoding="utf-8",
        )


def list_markdown_files(base_dir: Path) -> list[dict[str, str]]:
    """List markdown files in the output directory in deterministic order."""
    if not base_dir.exists():
        return []

    items: list[dict[str, str]] = []
    for path in sorted(base_dir.glob("*.md"), key=lambda p: p.name.lower()):
        if path.is_file():
            items.append(
                {
                    "filename": path.name,
                    "path": str(Path("public") / "markdowns" / path.name),
                }
            )
    return items
