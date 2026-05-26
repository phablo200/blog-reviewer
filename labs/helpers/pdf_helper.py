"""PDF-related helper methods."""

from pathlib import Path

from markdown import markdown
from weasyprint import HTML


class PDFHelper:
    """Encapsulates markdown-to-PDF rendering and PDF file listing."""

    @staticmethod
    def render_markdown_to_pdf(markdown_content: str, output_pdf_path: Path) -> None:
        """Render markdown content as a PDF file."""
        html = markdown(markdown_content, extensions=["fenced_code", "tables"])
        HTML(string=html).write_pdf(str(output_pdf_path))

    @staticmethod
    def list_output_files(
        base_dir: Path, extension: str, public_subdir: str
    ) -> list[dict[str, str]]:
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
