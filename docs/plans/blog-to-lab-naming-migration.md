# Plan: Blog to Lab Naming Migration

## Goal
Finalize the naming migration by replacing legacy `blog` module/class references with `lab` naming in runtime code, tests, and docs, while keeping API behavior stable.

## Constraints
- No API contract changes in this task.
- Keep existing endpoint paths and tags unchanged (`/blog-post-writer/*`, `/outputs/*`).
- Do not rename agent folder paths (`labs/agents/blog_*`) in this phase.

## Assumptions
- The folder migration (`blog/` -> `labs/`) is already complete.
- Class renames are allowed as long as call sites are updated in the same change.
- Temporary compatibility aliases are acceptable for one release cycle if needed.

## Plan

### 1. Baseline and Rename Map Lock
- Generate baseline inventories:
  - Import usage: `rg -n "from blog|import blog" main.py labs tests`
  - Symbol usage: `rg -n "\bBlog[A-Za-z0-9_]*\b" labs tests main.py`
- Freeze the authoritative rename map from spec before edits begin.

Planned deliverable:
- Validated rename list and affected-file checklist.

### 2. Runtime Import-Path Migration
- Update all runtime imports from `blog.*` to `labs.*`.
- Prioritize startup-critical files first:
  - `main.py`
  - `labs/router.py`
  - `labs/service.py`
  - `labs/helper.py`
  - `labs/agents/blog_post_writer/agent.py`

Planned deliverable:
- App imports resolve exclusively through `labs.*` in runtime modules.

### 3. Class and Schema Naming Migration
- Rename core service/agent/schema class names from `Blog*` to `Lab*` and update all local call sites.
- Planned baseline renames:
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
- If needed for incremental safety, add compatibility aliases inside renamed modules.

Planned deliverable:
- Consistent `Lab*` naming across runtime type definitions and call sites.

### 4. Test and Documentation Alignment
- Update test imports/usages to new module paths and class names:
  - `tests/test_service.py`
  - `tests/test_helper.py`
  - `tests/test_outputs_router.py`
  - `tests/test_outputs_pdf_endpoint.py`
- Update documentation references that still claim `blog/` module paths:
  - `README.md`
  - `AGENTS.md` (if this repo keeps it as source-of-truth)

Planned deliverable:
- Tests and docs aligned with migrated module/class naming.

### 5. Validation and Cleanup
- Syntax validation:
  - `python -m compileall main.py labs core tests`
- Targeted tests:
  - `pytest tests/test_service.py tests/test_helper.py tests/test_outputs_router.py tests/test_outputs_pdf_endpoint.py`
- Post-migration verification scans:
  - `rg -n "from blog|import blog" main.py labs tests`
  - `rg -n "\bBlog[A-Za-z0-9_]*\b" labs tests main.py`
- Manual smoke test:
  - Run app and check routes still respond at unchanged paths.

Planned deliverable:
- Passing checks and zero unresolved legacy import references.

## Execution Order
1. Milestone 1
2. Milestone 2
3. Milestone 3
4. Milestone 4
5. Milestone 5

## Acceptance Checklist (for implementation phase)
- [ ] No executable Python file imports `blog.*`.
- [ ] `main.py` includes routers from `labs` and app starts.
- [ ] Core classes/types are renamed to `Lab*` and references compile.
- [ ] Existing API endpoints behave unchanged.
- [ ] Targeted tests pass.
- [ ] Docs no longer describe runtime structure as `blog/` where it now is `labs/`.

## Risks
- Incomplete symbol rename causing runtime NameError/import errors.
- Over-renaming semantic “blog post” text that should remain domain language.
- External/internal consumers importing old class names directly.

Mitigations:
- Use explicit rename map with pre/post `rg` validation.
- Limit edits to code symbols/imports unless path docs are inaccurate.
- Add temporary aliases for compatibility where necessary.

## Rollback Strategy
- Revert migration commit as one logical unit if import/runtime regressions appear.
- If partial rollback is needed:
1. Restore previous class exports via compatibility aliases.
2. Revert only class renames while keeping stable `labs.*` import-path fixes.
3. Re-run compile/tests before redeploy.

## Definition of Done
- Runtime code, tests, and docs are internally consistent with `labs` module naming.
- Class/type naming is standardized to `Lab*` for migrated components.
- Verification commands and tests complete without migration-related failures.
