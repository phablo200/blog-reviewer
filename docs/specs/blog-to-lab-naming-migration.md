# Title
Blog to Lab Naming Migration

## Objective
- Complete the post-folder-rename migration by replacing remaining `blog`-named class/module references with `lab`-named references, without changing runtime behavior of existing endpoints.

## Background
- The feature directory has already been renamed from `blog/` to `labs/`, but runtime code still imports from `blog.*` in multiple modules (`main.py`, `labs/router.py`, `labs/service.py`, `labs/helper.py`, and tests).
- Core service/router classes still use `Blog*` names (e.g., `BlogPostService`, `BlogReviewerRequest`), which is inconsistent with the new domain naming.
- Existing docs/tests also still mention legacy paths and naming, increasing maintenance cost and risk of regressions.

## Scope
### In Scope
- Rename Python imports from `blog.*` to `labs.*` wherever they reference migrated modules.
- Rename public/internal classes that still encode legacy naming, including service and schema-facing class names.
- Update call sites in routers, services, helpers, agents, and tests to match new class names.
- Update module docstrings/comments where they incorrectly describe the feature as `blog` when referring to code ownership/domain naming.
- Preserve existing HTTP paths (`/blog-post-writer/*`) for backward compatibility in this change.

### Out of Scope
- Changing API route prefixes/tags from `blog-post-writer` to `lab-post-writer`.
- Renaming agent folder names (`blog_post_writer`, `blog_reviewer`, `blog_post_translator`) unless explicitly requested in a follow-up migration.
- Rewriting generated markdown content under `public/markdowns/`.
- Functional changes to prompt behavior, output formatting, or model wiring.

## Proposed Approach
- Apply the migration in two passes to reduce breakage:
1. Import-path alignment:
- Update all imports that still point to `blog.*` so app startup/tests resolve modules correctly from `labs.*`.
- Expected file targets: `main.py`, `labs/router.py`, `labs/service.py`, `labs/helper.py`, `labs/agents/blog_post_writer/agent.py`, `tests/test_*.py`, and any remaining Python modules surfaced by `rg -n "from blog|import blog"`.

2. Class/type naming alignment:
- Rename class identifiers from `Blog*` to `Lab*` in service and schema layers.
- Primary renames (recommended baseline):
  - `BlogPostService` -> `LabPostService`
  - `BlogPostWriterAgent` -> `LabPostWriterAgent`
  - `BlogPostWriterRequest` -> `LabPostWriterRequest`
  - `BlogPostWriterResponse` -> `LabPostWriterResponse`
  - `BlogReviewerAgent` -> `LabReviewerAgent`
  - `BlogReviewerRequest` -> `LabReviewerRequest`
  - `BlogReviewerResponse` -> `LabReviewerResponse`
  - `BlogReviewerStructuredResponse` -> `LabReviewerStructuredResponse`
  - `BlogPostTranslatorAgent` -> `LabPostTranslatorAgent`
  - `BlogPostTranslatorRequest` -> `LabPostTranslatorRequest`
  - `BlogPostTranslatorResponse` -> `LabPostTranslatorResponse`
- Keep temporary backwards-compatible aliases inside schema/agent modules for one migration cycle if cross-module churn is high (optional but recommended):
  - Example: `BlogReviewerRequest = LabReviewerRequest`
- Do not rename route function names unless necessary for readability.

3. Documentation and test alignment:
- Update README and AGENTS references to `labs/` paths where they currently claim `blog/`.
- Update test imports and stubs to new class names.
- Keep existing endpoint assertions unchanged unless route contracts intentionally change.

- Compatibility decision:
- Preserve old external API endpoint paths and response shapes in this migration, so clients are unaffected.

## Milestones
1. Discovery and mapping
- Produce a concrete rename map and reference list using `rg` across `main.py`, `labs/`, `tests/`, and docs.

2. Code migration
- Update imports and class names in Python runtime modules first (`labs/`, `main.py`), then update tests.
- Add optional compatibility aliases where required to keep incremental rollout safe.

3. Validation and cleanup
- Run syntax and test checks.
- Update docs and ensure no unresolved `from blog`/`import blog` statements remain.

## Edge Cases
- Typos and legacy names already present (e.g., `contants.py`, `_reviewd`) must not be changed unless directly required for class/module reference migration.
- Some text mentions of “blog” are content/domain semantics (e.g., prompt copy, generated markdown) and should remain unchanged unless they refer to code/module naming.
- Partial renames can create circular import/runtime errors; migration should be committed in a coherent batch.

## Acceptance Criteria
- [ ] `rg -n "from blog|import blog"` returns no results in executable Python files.
- [ ] `main.py` imports router from `labs` and app boots successfully.
- [ ] Service/router/helper/agent modules compile with renamed class/type references and no NameError/import errors.
- [ ] Existing endpoint behavior remains unchanged for:
  - `POST /blog-post-writer/organize-notes`
  - `POST /blog-post-writer/revise`
  - `GET /outputs/makdown`
  - `GET /outputs/pdf`
- [ ] Test suite passes for updated imports and class names.

## Test Plan
- Unit:
- Run `python -m compileall main.py labs core tests`.
- Run `pytest tests/test_service.py tests/test_helper.py tests/test_outputs_router.py tests/test_outputs_pdf_endpoint.py`.

- Integration:
- Start API with `uvicorn main:app --reload --host 0.0.0.0 --port 3015` and verify startup without import errors.

- Manual verification:
- Upload a UTF-8 markdown file to `POST /blog-post-writer/organize-notes` and verify accepted response.
- Call outputs endpoints and confirm response schema (`items`, `count`) unchanged.

## Risks and Mitigations
- Risk: Incomplete class rename leaves mismatched imports/usages across modules.
  - Mitigation: Use an explicit rename map and validate with `rg -n "Blog|blog" labs tests main.py` before/after.

- Risk: Over-renaming user-facing text that should remain domain-specific (“blog post”).
  - Mitigation: Restrict required renames to code symbols/import paths; review prompt/content files separately.

- Risk: Breaking downstream code if external imports rely on old class names.
  - Mitigation: Provide temporary alias exports for one release cycle and deprecate with follow-up cleanup.

## Open Questions
- Should this migration include endpoint/tag renaming (`/blog-post-writer` -> `/lab-post-writer`) or remain code-only for now?
- Should agent directory names (`blog_post_*`) also be renamed in the same PR, or staged later to minimize churn?
