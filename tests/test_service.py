from pathlib import Path

from fastapi import BackgroundTasks

from blog.service import BlogPostService


def test_enqueue_markdown_organization_uses_public_markdowns_path() -> None:
    service = BlogPostService.__new__(BlogPostService)
    service.output_dir = Path("public/markdowns")
    service.writer_agent = object()
    service.translator_agent = object()

    result = service.enqueue_markdown_organization(
        background_tasks=BackgroundTasks(),
        filename="example.md",
        context="# Notes",
    )

    assert "public/markdowns/example_reviewd.md" in result["output_file"]
