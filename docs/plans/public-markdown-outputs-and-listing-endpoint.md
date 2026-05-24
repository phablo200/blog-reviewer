# Implementation Plan: Public Markdown Outputs and Listing Endpoint

## Goal
Move generated markdown outputs from `blog/posts` to `public/markdowns`, and add `GET /outputs/makdown` to list available markdown files for easier download.

## Constraints
- No implementation in this phase.
- Keep requested route spelling: `/outputs/makdown`.
- Preserve existing async processing flow for `organize-notes`.
- Avoid destructive migration of existing files in `blog/posts` for initial rollout.

## Assumptions
- API clients can consume relative file paths in JSON.
- For v1, listing can be non-recursive and filename-sorted.
- Existing behavior in `POST /blog-post-writer/organize-notes` should remain unchanged except output location.

## Plan

### 1. Baseline and Design Lock
- Confirm response contract for listing endpoint:
  - `{"items": [{"filename": "...", "path": "public/markdowns/..."}], "count": N}`
- Confirm empty-directory behavior:
  - `{"items": [], "count": 0}`
- Confirm whether alias route `/outputs/markdown` is deferred (default: deferred).

Deliverable:
- Finalized API contract in spec/plan docs.

### 2. Output Directory Refactor Plan
- Update output directory constant in `blog/contants.py` to point to `public/markdowns`.
- Keep compatibility alias if needed to minimize edits in service layer.
- Ensure directory creation remains in background processing path.

Files targeted (planned):
- `blog/contants.py`
- `blog/service.py`

Deliverable:
- Planned path map showing old vs new write location.

### 3. Endpoint Addition Plan
- Add a dedicated outputs router module under `blog/`.
- Implement route `GET /outputs/makdown` with deterministic ordering and `.md` filtering.
- Register new router in `main.py`.

Files targeted (planned):
- `blog/outputs_router.py` (new)
- `main.py`

Deliverable:
- Planned endpoint behavior and response schema aligned to spec.

### 4. Testing Plan
- Add unit tests:
  - output path generation targets `public/markdowns`
  - listing logic filters `.md` and sorts filenames
- Add integration tests with FastAPI `TestClient`:
  - non-empty directory response
  - empty directory response

Files targeted (planned):
- `tests/test_service.py` (new)
- `tests/test_outputs_router.py` (new)

Deliverable:
- Test matrix mapping each acceptance criterion to at least one test.

### 5. Documentation Plan
- Update README structure and endpoint docs:
  - `blog/posts` -> `public/markdowns`
  - new `GET /outputs/makdown` example
- Add rollout note about legacy files in `blog/posts` not auto-migrated.

Files targeted (planned):
- `README.md`

Deliverable:
- Updated developer-facing usage guidance.

## Acceptance Checklist (for implementation phase)
- [ ] New outputs are saved under `public/markdowns`.
- [ ] `organize-notes` response references new output path.
- [ ] `GET /outputs/makdown` returns sorted `.md` list with `filename`, `path`, `count`.
- [ ] Endpoint works when directory does not yet exist.
- [ ] Tests cover route-level and service-level behavior.
- [ ] README reflects new path and endpoint.

## Rollout Strategy
- Phase 1: Deploy with new output directory and listing endpoint.
- Phase 2 (optional): Add alias `/outputs/markdown`.
- Phase 3 (optional): Add one-time migration utility for `blog/posts` legacy files.

## Risks
- Typo route naming may cause UX confusion.
- Existing scripts or consumers may still read from `blog/posts`.
- Path exposure may leak internals if absolute paths are returned.

Mitigations:
- Document exact route name.
- Return relative public path only.
- Keep legacy files untouched and call out transition explicitly.

## Review Questions
- Do you want me to include alias route `/outputs/markdown` in the same implementation PR? `makdown` was a mistake, implement `markdown` as your final version.
- Should we include `updated_at` in listing response now, or keep minimal payload? Yes.
- Should implementation include one-time copy/move from `blog/posts` to `public/markdowns`? No, `blog/posts` are test only, no need to migrate.
