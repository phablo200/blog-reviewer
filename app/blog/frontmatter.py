"""Utilities to enforce required YAML frontmatter for blog posts."""

from datetime import date

REQUIRED_FRONTMATTER_TEMPLATE = """---
title: "{title}"
date: "{date}"
summary: "{summary}"
tags: ["Carreira", "Meta"]
published: true
---
"""


def _extract_frontmatter(markdown: str) -> tuple[str | None, str]:
    text = markdown.lstrip()
    if not text.startswith("---\n"):
        return None, markdown

    end_marker = "\n---\n"
    end_idx = text.find(end_marker, 4)
    if end_idx == -1:
        return None, markdown

    frontmatter = text[: end_idx + len("\n---")]
    body = text[end_idx + len(end_marker) :]
    return frontmatter, body


def ensure_required_frontmatter(markdown: str) -> str:
    """Guarantee required metadata keys are present in post frontmatter."""
    frontmatter, body = _extract_frontmatter(markdown)
    body = body.lstrip("\n") if frontmatter is not None else markdown.lstrip("\n")

    default_title = "Olá, mundo: por que comecei este blog"
    default_date = date.today().isoformat()
    default_summary = (
        "Depois de 9+ anos construindo software, decidi escrever sobre o que "
        "aprendo no caminho. Aqui está o porquê — e o que esperar."
    )

    if frontmatter is None:
        template = REQUIRED_FRONTMATTER_TEMPLATE.format(
            title=default_title,
            date=default_date,
            summary=default_summary,
        )
        return f"{template}\n{body}".rstrip() + "\n"

    required_lines = {
        "title:": f'title: "{default_title}"',
        "date:": f'date: "{default_date}"',
        "summary:": f'summary: "{default_summary}"',
        "tags:": 'tags: ["Carreira", "Meta"]',
        "published:": "published: true",
    }

    lines = frontmatter.splitlines()
    if lines and lines[0] == "---" and lines[-1] == "---":
        inner = lines[1:-1]
    else:
        inner = lines

    for key, line in required_lines.items():
        if not any(item.strip().startswith(key) for item in inner):
            inner.append(line)

    normalized_frontmatter = "---\n" + "\n".join(inner) + "\n---\n"
    return f"{normalized_frontmatter}\n{body}".rstrip() + "\n"
