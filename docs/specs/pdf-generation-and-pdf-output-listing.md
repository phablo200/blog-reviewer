# PDF Generation and PDF Output Listing Endpoint

## Objective
- Generate PDF artifacts from both reviewed English markdown and translated Portuguese markdown during the existing background processing flow.
- Expose a new API endpoint (`GET /outputs/pdf`) to list available PDFs for download/discovery.

## Background
- `POST /blog-post-writer/organize-notes` enqueues `process_and_save_markdown` in `blog/helper.py`.
- Current flow writes two markdown files into `public/markdowns`: `<name>_reviewd.md` (EN) and `<name>_reviewd_pt_br.md` (PT-BR).
- Existing outputs API only lists markdown files via `GET /outputs/makdown` in `blog/router.py`.
- No PDF generation exists, and there is no listing endpoint for PDF outputs.

## Scope
### In Scope
- Generate one PDF for each produced markdown file (EN + PT-BR) in the same output directory (`public/markdowns`).
- Add helper utilities to convert markdown content into PDF using `markdown` + `weasyprint`.
- Add a PDF outputs listing endpoint at `GET /outputs/pdf`.
- Add/adjust tests for PDF listing and markdown-to-PDF orchestration behavior.
- Add required dependencies to `requirements.txt`.

### Out of Scope
- Visual template/theme customization for generated PDFs.
- Authentication/authorization for output listing or file download.
- Changing async model (keep FastAPI `BackgroundTasks` flow).
- Deprecation/migration of existing markdown endpoint naming (`/outputs/makdown`) in this task.

## Proposed Approach
- Keep orchestration entrypoint unchanged (`BlogPostService.enqueue_markdown_organization`).
- Extend `blog/helper.py`:
  - Add a pure helper, e.g. `render_markdown_to_pdf(markdown_text: str, output_pdf_path: Path) -> None`.
  - Convert markdown to HTML with `markdown(markdown_text, extensions=["fenced_code", "tables"])`.
  - Render PDF via `weasyprint.HTML(string=html).write_pdf(str(output_pdf_path))`.
  - Call this helper after writing EN markdown and after writing PT-BR markdown:
    - `<name>_reviewd.pdf`
    - `<name>_reviewd_pt_br.pdf`
- Add a generic file-list helper for PDFs (recommended in `blog/helper.py`):
  - `list_output_files(base_dir: Path, extension: str) -> list[dict[str, str]]`
  - Build deterministic ascending filename list and return paths rooted at `public/markdowns`.
- Extend service layer in `blog/service.py`:
  - Add `list_pdf_outputs(self) -> dict[str, Any]` returning `{"items": [...], "count": N}`.
- Extend outputs router in `blog/router.py`:
  - Add `@outputs_router.get("/pdf")` route returning `service.list_pdf_outputs()`.
- Dependency updates:
  - Add `markdown` and `weasyprint` to `requirements.txt`.
  - Note: WeasyPrint requires native system libs in container/runtime; update Dockerfile only if build/runtime fails in verification.

## Milestones
1. PDF generation in background workflow
- Update `blog/helper.py` to render PDFs immediately after each markdown output is written.
- Ensure failure behavior remains predictable (existing top-level exception handler still writes failure text to EN markdown).

2. PDF discovery endpoint
- Add service method and router endpoint for `GET /outputs/pdf`.
- Reuse deterministic listing behavior and response shape.

3. Validation and dependency wiring
- Add tests for helper/service/route behavior.
- Add dependencies to `requirements.txt` and confirm import/runtime viability.

## Edge Cases
- Output directory missing: list endpoint returns empty list and zero count.
- Non-PDF files present: `/outputs/pdf` excludes them.
- Markdown contains code blocks/tables: conversion supports these extensions.
- PDF rendering failure for one language:
  - Recommended behavior: fail current task and keep existing error handling contract, so issue is visible in generated failure file.

## Acceptance Criteria
- [ ] For each `organize-notes` request, EN markdown and PT-BR markdown are still generated as before.
- [ ] For each generated markdown file, a sibling PDF with matching stem is created in `public/markdowns`.
- [ ] `GET /outputs/pdf` returns only `.pdf` files from `public/markdowns` with deterministic ordering.
- [ ] PDF listing response shape is `{"items": [{"filename": "...", "path": "public/markdowns/..."}], "count": N}`.
- [ ] Existing markdown listing behavior remains unchanged.

## Test Plan
- Unit:
- Add/extend helper tests to verify `.pdf` filtering and stable sorting.
- Add service test for `list_pdf_outputs` response shape/count.
- Add helper test that invokes `process_and_save_markdown` with mocked writer/translator and mocked PDF renderer to verify EN and PT-BR PDF targets are requested.

- Integration:
- Add FastAPI route test for `GET /outputs/pdf` with seeded `.pdf` and non-`.pdf` files.
- Preserve existing route tests for markdown listing.

- Manual verification:
- Start API, upload a markdown file to `POST /blog-post-writer/organize-notes`.
- Confirm 4 artifacts appear in `public/markdowns`: `*_reviewd.md`, `*_reviewd_pt_br.md`, `*_reviewd.pdf`, `*_reviewd_pt_br.pdf`.
- Call `GET /outputs/pdf` and validate list/count.

## Risks and Mitigations
- Risk: `weasyprint` may fail in Docker/minimal environments due to missing native dependencies.
  - Mitigation: document/verify required OS packages and update Dockerfile if needed.
- Risk: Rendering arbitrary markdown HTML directly may produce inconsistent styling.
  - Mitigation: accept default rendering for v1; introduce CSS template in follow-up if needed.
- Risk: Increased background-task processing time.
  - Mitigation: keep generation in same async task and monitor latency; defer queueing redesign unless required.

## Open Questions
- Should `/outputs/makdown` also gain a corrected alias `/outputs/markdown` in this same change?
- Should PDF listing include timestamps (`created_at` / `updated_at`) for UI sorting/filtering?
- If EN PDF generation succeeds but PT-BR PDF generation fails, should partial outputs be retained or rolled back?
