from pathlib import Path
from types import SimpleNamespace

from labs.helpers.markdown_helper import MarkdownHelper
from labs.helpers import markdown_helper
from labs.helpers.pdf_helper import PDFHelper


class _WriterAgentStub:
    def organize_notes(self, request):
        return SimpleNamespace(reviewed_markdown=request.context)


class _TranslatorAgentStub:
    def translate(self, request):
        return SimpleNamespace(translated_markdown=request.content)


class _MetadataAgentStub:
    def generate(self, _request):
        return SimpleNamespace(
            title="Testando o Fluxo: Um Guia Pratico",
            date="2023-10-10",
            summary="Uma exploracao pratica dos processos de teste.",
            tags=["Carreira", "Meta"],
            published=True,
        )


class _FailingWriterAgentStub:
    def organize_notes(self, request):
        raise RuntimeError("writer failed")


def test_process_and_save_markdown_writes_reviewed_and_translated_files(tmp_path, monkeypatch) -> None:
    output_path = tmp_path / "my-post_reviewd.md"
    pdf_dir = tmp_path / "pdf"
    generated_pdfs: list[Path] = []

    def _fake_render_markdown_to_pdf(_markdown_content: str, output_pdf_path: Path) -> None:
        output_pdf_path.write_text("pdf-content", encoding="utf-8")
        generated_pdfs.append(output_pdf_path)

    monkeypatch.setattr(PDFHelper, "render_markdown_to_pdf", _fake_render_markdown_to_pdf)
    monkeypatch.setattr(markdown_helper, "PUBLIC_PDF_DIR", pdf_dir)

    MarkdownHelper.process_and_save_markdown(
        context="# Title",
        output_path=output_path,
        writer_agent=_WriterAgentStub(),
        translator_agent=_TranslatorAgentStub(),
        metadata_agent=_MetadataAgentStub(),
    )

    assert output_path.exists()
    assert output_path.with_name("my-post_reviewd_pt_br.md").exists()
    assert (pdf_dir / "my-post_reviewd.pdf").exists()
    assert (pdf_dir / "my-post_reviewd_pt_br.pdf").exists()
    assert generated_pdfs == [
        pdf_dir / "my-post_reviewd.pdf",
        pdf_dir / "my-post_reviewd_pt_br.pdf",
    ]


def test_process_and_save_markdown_writes_error_file_on_failure(tmp_path) -> None:
    output_path = tmp_path / "my-post_reviewd.md"

    MarkdownHelper.process_and_save_markdown(
        context="# Title",
        output_path=output_path,
        writer_agent=_FailingWriterAgentStub(),
        translator_agent=_TranslatorAgentStub(),
        metadata_agent=_MetadataAgentStub(),
    )

    content = output_path.read_text(encoding="utf-8")
    assert "Failed to process markdown notes." in content
    assert "writer failed" in content


def test_process_and_save_markdown_preserves_markdown_when_pdf_generation_fails(
    tmp_path, monkeypatch
) -> None:
    output_path = tmp_path / "my-post_reviewd.md"
    pdf_dir = tmp_path / "pdf"

    def _failing_render_markdown_to_pdf(_markdown_content: str, _output_pdf_path: Path) -> None:
        raise AttributeError("'super' object has no attribute 'transform'")

    monkeypatch.setattr(PDFHelper, "render_markdown_to_pdf", _failing_render_markdown_to_pdf)
    monkeypatch.setattr(markdown_helper, "PUBLIC_PDF_DIR", pdf_dir)

    MarkdownHelper.process_and_save_markdown(
        context="# Title",
        output_path=output_path,
        writer_agent=_WriterAgentStub(),
        translator_agent=_TranslatorAgentStub(),
        metadata_agent=_MetadataAgentStub(),
    )

    content = output_path.read_text(encoding="utf-8")
    assert "Failed to process markdown notes." not in content
    assert "title:" in content
    assert output_path.with_name("my-post_reviewd_pt_br.md").exists()
