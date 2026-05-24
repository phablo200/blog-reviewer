from pathlib import Path
from types import SimpleNamespace

import blog.helper as helper


class _WriterAgentStub:
    def organize_notes(self, request):
        return SimpleNamespace(reviewed_markdown=request.context)


class _TranslatorAgentStub:
    def translate(self, request):
        return SimpleNamespace(translated_markdown=request.content)


class _FailingWriterAgentStub:
    def organize_notes(self, request):
        raise RuntimeError("writer failed")


def test_process_and_save_markdown_writes_reviewed_and_translated_files(tmp_path, monkeypatch) -> None:
    output_path = tmp_path / "my-post_reviewd.md"
    generated_pdfs: list[Path] = []

    def _fake_render_markdown_to_pdf(_markdown_content: str, output_pdf_path: Path) -> None:
        output_pdf_path.write_text("pdf-content", encoding="utf-8")
        generated_pdfs.append(output_pdf_path)

    monkeypatch.setattr(helper, "render_markdown_to_pdf", _fake_render_markdown_to_pdf)

    helper.process_and_save_markdown(
        context="# Title",
        output_path=output_path,
        writer_agent=_WriterAgentStub(),
        translator_agent=_TranslatorAgentStub(),
    )

    assert output_path.exists()
    assert output_path.with_name("my-post_reviewd_pt_br.md").exists()
    assert output_path.with_suffix(".pdf").exists()
    assert output_path.with_name("my-post_reviewd_pt_br.pdf").exists()
    assert generated_pdfs == [
        output_path.with_suffix(".pdf"),
        output_path.with_name("my-post_reviewd_pt_br.pdf"),
    ]


def test_process_and_save_markdown_writes_error_file_on_failure(tmp_path) -> None:
    output_path = tmp_path / "my-post_reviewd.md"

    helper.process_and_save_markdown(
        context="# Title",
        output_path=output_path,
        writer_agent=_FailingWriterAgentStub(),
        translator_agent=_TranslatorAgentStub(),
    )

    content = output_path.read_text(encoding="utf-8")
    assert "Failed to process markdown notes." in content
    assert "writer failed" in content
