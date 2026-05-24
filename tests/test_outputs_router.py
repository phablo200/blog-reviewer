from pathlib import Path

from blog.helper import list_markdown_files, list_output_files
from blog.service import BlogPostService


def test_list_markdown_files_returns_sorted_markdown_files(tmp_path) -> None:
    (tmp_path / "b-file.md").write_text("b", encoding="utf-8")
    (tmp_path / "a-file.md").write_text("a", encoding="utf-8")
    (tmp_path / "notes.txt").write_text("x", encoding="utf-8")

    items = list_markdown_files(tmp_path)

    assert items == [
        {"filename": "a-file.md", "path": "public/markdowns/a-file.md"},
        {"filename": "b-file.md", "path": "public/markdowns/b-file.md"},
    ]


def test_list_markdown_files_returns_empty_for_missing_directory(tmp_path) -> None:
    items = list_markdown_files(tmp_path / "missing")
    assert items == []


def test_list_markdown_outputs_response_shape(tmp_path) -> None:
    (tmp_path / "post.md").write_text("# Post", encoding="utf-8")
    service = BlogPostService.__new__(BlogPostService)
    service.output_dir = Path(tmp_path)

    payload = service.list_markdown_outputs()

    assert payload == {
        "items": [{"filename": "post.md", "path": "public/markdowns/post.md"}],
        "count": 1,
    }


def test_list_output_files_returns_sorted_pdf_files(tmp_path) -> None:
    (tmp_path / "b-file.pdf").write_text("b", encoding="utf-8")
    (tmp_path / "a-file.pdf").write_text("a", encoding="utf-8")
    (tmp_path / "notes.md").write_text("x", encoding="utf-8")

    items = list_output_files(tmp_path, ".pdf")

    assert items == [
        {"filename": "a-file.pdf", "path": "public/markdowns/a-file.pdf"},
        {"filename": "b-file.pdf", "path": "public/markdowns/b-file.pdf"},
    ]


def test_list_pdf_outputs_response_shape(tmp_path) -> None:
    (tmp_path / "post.pdf").write_text("pdf", encoding="utf-8")
    service = BlogPostService.__new__(BlogPostService)
    service.output_dir = Path(tmp_path)

    payload = service.list_pdf_outputs()

    assert payload == {
        "items": [{"filename": "post.pdf", "path": "public/markdowns/post.pdf"}],
        "count": 1,
    }
