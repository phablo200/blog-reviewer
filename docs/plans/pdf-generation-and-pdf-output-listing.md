# Plan: PDF Generation and PDF Output Listing Endpoint

## Goal
Implement PDF generation for both EN and PT-BR markdown outputs in the existing review flow, and expose `GET /outputs/pdf` to list downloadable PDFs.

## Assumptions
- Existing markdown output flow and filenames remain unchanged.
- PDF files will be generated in the same directory as markdown outputs: `public/markdowns`.
- Existing endpoint `GET /outputs/makdown` remains unchanged in this task.

## Milestone 1: Dependency and Runtime Preparation
1. Update Python dependencies in `requirements.txt`:
- Add `markdown`.
- Add `weasyprint`.
2. Verify runtime requirements for WeasyPrint in local/dev container:
- Confirm imports succeed.
- If container/runtime is missing native libs, document and patch `Dockerfile`.

Deliverables:
- Dependency changes committed in `requirements.txt`.
- Runtime note (and Dockerfile update only if required).

## Milestone 2: PDF Generation in Background Workflow
1. Extend `blog/helper.py` with markdown-to-PDF conversion utility:
- Convert markdown to HTML with extensions: `fenced_code`, `tables`.
- Render HTML to PDF via WeasyPrint.
2. Wire PDF generation into `process_and_save_markdown`:
- Generate EN PDF after writing `<name>_reviewd.md`.
- Generate PT-BR PDF after writing `<name>_reviewd_pt_br.md`.
3. Keep current error contract stable:
- Preserve existing top-level exception handling behavior.

Deliverables:
- Helper function(s) for PDF rendering.
- Updated processing flow generating 4 artifacts per request (`2x .md`, `2x .pdf`).

## Milestone 3: PDF Listing Endpoint
1. Add reusable file-listing support for extension-based discovery (or dedicated PDF listing helper).
2. Add `list_pdf_outputs` in `blog/service.py` returning:
- `{"items": [{"filename": "...", "path": "public/markdowns/..."}], "count": N}`
3. Add route in `blog/router.py`:
- `GET /outputs/pdf` mapped to `service.list_pdf_outputs()`.

Deliverables:
- Service method and route for PDF listing.
- Deterministic sorting by filename.

## Milestone 4: Test Coverage
1. Unit tests:
- PDF file listing filters only `.pdf` and sorts deterministically.
- `BlogPostService.list_pdf_outputs()` response shape and count.
- Background flow test ensuring both EN and PT-BR PDF targets are triggered.
2. Integration tests:
- `GET /outputs/pdf` returns seeded PDF files and excludes non-PDF files.
- Empty-directory response returns `items: []`, `count: 0`.

Deliverables:
- New/updated tests under `tests/`.
- Passing local test commands for touched scope.

## Milestone 5: Verification and Documentation
1. Manual validation:
- Upload a sample markdown via `POST /blog-post-writer/organize-notes`.
- Confirm generated artifacts:
  - `*_reviewd.md`
  - `*_reviewd_pt_br.md`
  - `*_reviewd.pdf`
  - `*_reviewd_pt_br.pdf`
- Call `GET /outputs/pdf` and verify payload.
2. Update docs if needed:
- Endpoint inventory and output artifacts expectations.

Deliverables:
- Verified behavior evidence.
- Doc adjustments where relevant.

## Execution Order
1. Milestone 1
2. Milestone 2
3. Milestone 3
4. Milestone 4
5. Milestone 5

## Risks
- WeasyPrint native dependency issues in Docker/runtime.
- Longer background task processing time due to PDF rendering.
- Rendering differences from plain markdown to styled PDF.

## Rollback Strategy
- Feature rollback can be done by:
1. Removing PDF-generation calls from `process_and_save_markdown`.
2. Removing `GET /outputs/pdf` route and service method.
3. Reverting added dependencies if no longer needed.

## Definition of Done
- EN and PT-BR PDFs are generated for each successful markdown run.
- `GET /outputs/pdf` lists only `.pdf` files with deterministic order.
- Tests for helper/service/router pass.
- No regression in existing markdown output and listing behavior.
