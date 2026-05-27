from pathlib import Path

from fastapi import BackgroundTasks

from labs.service import LabPostService


def test_enqueue_markdown_organization_uses_public_markdowns_path() -> None:
    service = LabPostService.__new__(LabPostService)
    service.markdown_output_dir = Path("public/markdown")
    service.pdf_output_dir = Path("public/pdf")
    service.writer_agent = object()
    service.translator_agent = object()
    service.metadata_agent = object()

    result = service.enqueue_markdown_organization(
        background_tasks=BackgroundTasks(),
        filename="example.md",
        context="# Notes",
    )

    assert "public/markdown/example_reviewd.md" in result["output_file"]
