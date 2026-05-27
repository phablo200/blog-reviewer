# Plan: Labs Code Example Agent Integration

## Goal
Implement and integrate `labs_code_example` so GitHub-based code examples are extracted from sketch notes context and injected into the writer/reviewer pipeline to improve final lab post quality.

## Confirmed Decisions
- Repository discovery source: parse both frontmatter metadata and markdown body links, then deduplicate.
- Integration point: inject structured examples into `LabPostWriterAgent.organize_notes(...)` before initial draft generation.
- Failure behavior: example extraction is best-effort and must never break markdown generation.
- Reviewer collaboration: revision cycles must explicitly validate and improve technical explanation of included code examples.

## Assumptions
- Existing HTTP contracts stay unchanged (`POST /labs/review`, `GET /outputs/*`).
- Current repository enrichment in `labs_post_writer/helper.py` remains and is complemented, not replaced.
- GitHub API access stays unauthenticated for now; rate-limit handling is required.

## Milestone 1: Contract and Prompt Foundation
1. Implement schemas in `labs/agents/labs_code_example/schema.py`:
- `LabCodeExampleRequest` (`notes_context`, `repositories`, `max_examples`).
- `LabCodeExampleItem` (`repository`, `file_path`, `language`, `snippet`, `why_it_matters`, `integration_hint`).
- `LabCodeExampleResponse` (`examples`, `summary`, `warnings`).
2. Implement prompt builder in `labs/agents/labs_code_example/prompts.py`:
- Require provenance-backed examples only (repo + file path).
- Enforce concise snippets and no hallucinated APIs/paths.
- Force structured output-compatible instructions.

Deliverables:
- Typed request/response models and deterministic prompt constraints for code-example generation.

## Milestone 2: Code Example Agent Engine
1. Implement `labs/agents/labs_code_example/agent.py`:
- Build chat model with structured output (OpenAI provider).
- Extract/normalize repository targets (`owner/repo`) from request context.
- Fetch lightweight GitHub data (repo metadata, README, selected source files only).
2. Implement candidate-file selection strategy:
- Prioritize practical files (`main`, `app`, `router`, `service`, `config`, handlers).
- Limit fetched file count and snippet size to avoid prompt bloat.
3. Implement resilience:
- Return `LabCodeExampleResponse(examples=[], warnings=[...])` on fetch/LLM errors.
- Log actionable warnings without raising pipeline-breaking exceptions.

Deliverables:
- Working extraction agent with bounded GitHub fetch behavior and safe fallback response.

## Milestone 3: Writer Integration
1. Update `labs/agents/labs_post_writer/agent.py`:
- Instantiate `LabCodeExampleAgent`.
- After `enrich_context_with_repositories(...)`, call code-example agent.
- Append `## Code Examples Context` section with normalized example entries before first draft prompt.
2. Preserve pipeline robustness:
- If no examples are returned, continue with existing writer behavior.
- If warnings exist, log them and continue.

Deliverables:
- Writer receives structured technical example context when available, without changing public service contracts.

## Milestone 4: Reviewer Collaboration Update
1. Update reviewer-facing instructions in writer revision prompt:
- Require maintaining at least one concrete repository-grounded example when relevant.
- Require checking technical accuracy and explanatory clarity of included snippets.
2. Recommended prompt alignment in `labs/agents/labs_reviewer/prompts.py`:
- Add explicit rubric item for code example correctness and usefulness.

Deliverables:
- Review cycles intentionally improve technical narrative quality around code examples.

## Milestone 5: Test Coverage and Verification
1. Add unit tests for `labs_code_example` (new `tests/test_labs_code_example_agent.py`):
- Successful structured response path.
- GitHub fetch failures (404/network/rate-limit) return warnings and empty examples.
- Malformed LLM output path falls back safely.
2. Add/update writer integration tests (`tests/test_labs_post_writer_agent.py`):
- Assert code examples are included in writer prompt context when available.
- Assert pipeline continues when code-example agent returns no data.
3. Verification commands:
- `venv/bin/python -m compileall labs tests`
- `venv/bin/python -m pytest -q tests/test_labs_code_example_agent.py tests/test_labs_post_writer_agent.py tests/test_service.py`

Deliverables:
- Automated evidence that example extraction and integration work and do not regress existing flow.

## Execution Order
1. Milestone 1
2. Milestone 2
3. Milestone 3
4. Milestone 4
5. Milestone 5

## Risks
- GitHub API rate limits or unavailable repos can reduce example yield.
- Prompt/context growth may degrade writer output quality.
- Hallucinated example references can reduce post credibility.

Mitigations:
- Keep fetches minimal and fail-soft with warnings.
- Cap snippet length and max examples.
- Enforce provenance fields and reviewer checks for technical consistency.

## Rollback Strategy
1. Remove `LabCodeExampleAgent` invocation from `labs_post_writer/agent.py`.
2. Keep existing repository-enrichment-only behavior intact.
3. Leave `labs_code_example` module isolated and removable without endpoint changes.

## Definition of Done
- `labs_code_example` is implemented with typed schema, prompt, and resilient runtime behavior.
- Writer pipeline includes `Code Examples Context` when repositories are available.
- Review loop checks and improves code-example technical quality.
- Failures in example extraction do not break markdown output generation.
- Targeted compile/tests pass for new and affected components.
