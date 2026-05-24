# Public Markdown Outputs and Listing Endpoint

## Objective
- Store generated markdown outputs in a public-facing directory for easier access.
- Add an API endpoint that lists all available markdown files for simple download workflows.

## Background
- Current behavior writes generated files to `blog/posts/` via `BLOG_POSTS_OUTPUT_DIR` in `blog/contants.py`.
- Existing endpoint `POST /blog-post-writer/organize-notes` returns an output file path and writes reviewed + translated files asynchronously.
- There is no dedicated endpoint to discover generated markdown files.
- `blog/posts/` currently contains generated artifacts that users may still need after migration.

## Scope
### In Scope
- Create and use `public/markdowns/` as the canonical output directory.
- Update output-directory constant/config so writer/translator artifacts are stored under `public/markdowns/`.
- Add `GET /outputs/makdown` endpoint (spelling preserved from request) returning available markdown files.
- Include file metadata sufficient for UI/download use (filename + relative public path).
- Ensure output directory is created automatically when missing.
- Add tests for new path behavior and listing endpoint.

### Out of Scope
- Changing background-task processing model.
- Implementing authentication/authorization for output discovery/download.
- Serving custom download streams from API (listing only; downloads use returned paths).
- Renaming the requested route to corrected spelling (`/outputs/markdown`) unless requested later.

## Proposed Approach
- Introduce a public output constant in `blog/contants.py`:
  - `PUBLIC_MARKDOWNS_DIR = Path(__file__).resolve().parent.parent / "public" / "markdowns"`.
  - Optionally keep backward-compatible alias `BLOG_POSTS_OUTPUT_DIR = PUBLIC_MARKDOWNS_DIR` to minimize churn.
- Keep `BlogPostService` orchestration logic intact; only switch `self.output_dir` source to public directory constant.
- Add a new router module (recommended `blog/outputs_router.py`) with:
  - `APIRouter(prefix="/outputs", tags=["Outputs"])`
  - `GET /makdown` returning JSON list of markdown files found in `public/markdowns`.
- Register new router in `main.py`.
- Listing response contract (recommended):
  - `{"items": [{"filename": "...md", "path": "public/markdowns/...md"}], "count": N}`.
  - Sort by filename ascending for deterministic responses.
- Directory scanning rules:
  - Include only files matching `*.md`.
  - Ignore nested directories for v1 (non-recursive), unless nested storage becomes a future requirement.
- Migration behavior for existing files in `blog/posts`:
  - No forced move in app startup (safe default).
  - Existing files remain where they are; new generated files go to `public/markdowns`.
  - If required later, add one-time migration script as separate task.

## Milestones
1. Output directory migration in code
- Update constants and service wiring to target `public/markdowns`.
- Ensure `mkdir(parents=True, exist_ok=True)` remains in async writer flow.

2. Output discovery API
- Implement `GET /outputs/makdown` route and response schema.
- Register router in `main.py`.

3. Verification and docs
- Add route-level and service-level tests.
- Update README project structure and endpoint docs to reflect new directory + endpoint.

## Edge Cases
- `public/markdowns` does not exist yet: endpoint should return `items: []`, `count: 0` (not 500).
- Non-markdown files present in directory: endpoint excludes them.
- Large file counts: deterministic ordering maintained; pagination deferred.
- Filenames with spaces/special chars: return exactly as stored without mutation.

## Acceptance Criteria
- [ ] New reviewed and translated markdown files are written to `public/markdowns/`.
- [ ] `POST /blog-post-writer/organize-notes` response references the new output location.
- [ ] `GET /outputs/makdown` returns all available `.md` files in `public/markdowns`.
- [ ] Listing response is deterministic (stable order) and includes filename + path + count.
- [ ] Behavior remains successful when output directory is absent at startup.

## Test Plan
- Unit:
- Verify output path generation in `BlogPostService.enqueue_markdown_organization` targets `public/markdowns`.
- Verify listing helper/function filters only `.md` and sorts deterministically.

- Integration:
- FastAPI `TestClient` test for `GET /outputs/makdown` with seeded markdown files.
- FastAPI test for empty directory response shape.

- Manual verification:
- Run API, upload sample `.md`, confirm files created in `public/markdowns`.
- Call `GET /outputs/makdown` and validate filenames/paths/count.

## Risks and Mitigations
- Risk: Typo in route (`makdown`) may cause client confusion.
  - Mitigation: Document route exactly as implemented; consider adding alias `/outputs/markdown` in follow-up.
- Risk: Existing tooling still reads `blog/posts`.
  - Mitigation: Update README and callers; keep legacy files untouched.
- Risk: Returning filesystem-like paths can leak internal structure.
  - Mitigation: Return relative public paths only (no absolute paths).

## Open Questions
- Should we add a second alias route `GET /outputs/markdown` now for forward compatibility? Actually `makdown` was a type mistakes, the realname should be `markdown` fix it in our plan.
- Should listing include timestamps (`created_at`/`updated_at`) to improve UI sorting? Yes.
- Should startup include a one-time migration from `blog/posts` to `public/markdowns`? No, It's not necessary, the files in `blog/posts` are tests only.
