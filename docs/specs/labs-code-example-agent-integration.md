## Title
Labs Code Example Agent Integration

## Objective
- Implement `labs/agents/labs_code_example` so it extracts practical code examples from GitHub repositories referenced in sketch notes metadata.
- Feed those examples into the post-writing pipeline so `labs_post_writer` and `labs_reviewer` can produce a technically stronger final post.

## Background
- Current flow in `labs/service.py` and `labs/helpers/markdown_helper.py` runs: post writer -> metadata -> translator -> file outputs.
- `labs_post_writer` already enriches context with repository metadata and README excerpts (`labs/agents/labs_post_writer/helper.py`), but it does not extract focused code examples.
- `labs_code_example` directory exists but is empty (`agent.py`, `schema.py`, `prompts.py`), so there is no structured example extraction available.
- `labs_reviewer` can improve prose and structure, but it currently has no dedicated input channel for vetted example snippets.

## Scope
### In Scope
- Define schema, prompt, and agent implementation for `labs_code_example`.
- Parse sketch-note metadata/frontmatter and/or markdown body to identify target GitHub repositories.
- Fetch repository content selectively and produce structured, concise code examples with explanation.
- Integrate example output into `labs_post_writer.organize_notes` context before draft generation.
- Include reviewer-aware guidance so examples are preserved, technically checked, and improved during revision cycles.
- Add tests for extraction logic and pipeline integration behavior.

### Out of Scope
- Full repository indexing or cloning entire repos.
- Building a vector database or long-term cache for examples.
- Changes to API routes in `labs/router.py`.
- UI changes for output visualization.

## Proposed Approach
- Implement a new agent contract:
  - `LabCodeExampleRequest` with fields:
    - `notes_context: str`
    - `repositories: list[str]` (normalized as `owner/repo`)
    - `max_examples: int = 3`
  - `LabCodeExampleItem` with fields:
    - `repository: str`
    - `file_path: str`
    - `language: str`
    - `snippet: str`
    - `why_it_matters: str`
    - `integration_hint: str` (how writer should weave it into post)
  - `LabCodeExampleResponse` with fields:
    - `examples: list[LabCodeExampleItem]`
    - `summary: str`
    - `warnings: list[str]`
- In `labs_code_example/agent.py`:
  - Reuse repository URL extraction patterns from writer helper behavior (or move to shared helper to avoid duplication).
  - Call GitHub API for lightweight discovery (default branch, tree/file candidates, README) and fetch only candidate files for snippet extraction.
  - Build deterministic prompt input and invoke structured output via OpenAI model (same provider style as metadata/writer).
  - Add resilient fallback: return empty `examples` plus warning if fetch/LLM fails.
- In `labs_code_example/prompts.py`:
  - System prompt constraints:
    - Only use fetched repository material.
    - Prefer short production-relevant snippets (e.g., handlers, service logic, config usage).
    - Avoid hallucinated file names/APIs.
    - Return concise, publication-ready explanation per snippet.
- In `labs_post_writer/agent.py`:
  - Initialize `LabCodeExampleAgent`.
  - After existing repository-context enrichment, request code examples and append an explicit `## Code Examples Context` section to writer input.
  - If examples exist, include reviewer instruction in improvement prompt to verify technical narrative around each example and retain at least one concrete snippet in final post.
- Optional (recommended) reviewer adjustment in `labs_reviewer/prompts.py`:
  - Add rubric item: validate technical correctness and explanatory clarity of included code examples.

Impacted files/modules:
- `labs/agents/labs_code_example/agent.py`
- `labs/agents/labs_code_example/schema.py`
- `labs/agents/labs_code_example/prompts.py`
- `labs/agents/labs_post_writer/agent.py`
- `labs/agents/labs_post_writer/helper.py` (if helper reuse/refactor is needed)
- `labs/agents/labs_reviewer/prompts.py` (recommended)
- `tests/test_labs_code_example_agent.py` (new)
- `tests/test_labs_post_writer_agent.py` (new/updated)

## Milestones
1. Agent contract + prompt foundation
- Implement `schema.py` and `prompts.py` for structured request/response and output constraints.

2. Code example extraction engine
- Implement `agent.py` fetch + selection + structured-generation flow with fallback handling and logging.

3. Writer/reviewer integration
- Wire `LabCodeExampleAgent` into `labs_post_writer` pipeline.
- Inject example context into initial draft generation and revision loops.

4. Validation and tests
- Add unit tests for repository parsing/fallback paths.
- Add integration-style tests (mocked LLM + mocked GitHub calls) to verify example context reaches writer prompts.

## Edge Cases
- Notes contain no GitHub repository URL.
- Invalid/private/deleted repositories or rate-limited GitHub responses.
- Non-UTF8 source files or very large files.
- Repository language mismatch with post language.
- LLM structured output returns malformed items.

## Acceptance Criteria
- [ ] `labs_code_example` provides non-crashing structured responses for success and failure scenarios.
- [ ] When notes include at least one accessible GitHub repository, writer input contains `Code Examples Context` with at least one normalized example item.
- [ ] If extraction fails, writer pipeline still completes and logs warning without breaking markdown generation.
- [ ] Reviewer loop preserves or improves technical explanation for included examples.
- [ ] New tests cover normal path and at least two failure paths.

## Test Plan
- Unit:
  - `labs_code_example` schema validation and normalization behavior.
  - GitHub fetch error handling returns warnings and empty examples.
- Integration:
  - Mock GitHub + mock LLM, run `LabPostWriterAgent.organize_notes`, assert prompt/context includes structured examples.
  - Validate revision-loop prompt contains reviewer instructions for example quality.
- Manual verification:
  - Upload a markdown file with frontmatter pointing to one public GitHub repo and confirm generated markdown references concrete snippet(s).

## Risks and Mitigations
- Risk: GitHub API rate limits degrade extraction.
  - Mitigation: keep calls minimal, short-circuit on first useful files, add warnings/fallback.
- Risk: Hallucinated code references reduce trust.
  - Mitigation: prompt guardrails + require file path/repo provenance in every example item.
- Risk: Longer context harms writer quality.
  - Mitigation: cap examples/snippet length and include concise summaries only.

## Open Questions
- Should repository references be read only from frontmatter metadata, markdown body links, or both? Recommendation: both, with deduplication.
- Should snippets be embedded as full fenced blocks in final post or summarized with short excerpts? Recommendation: short excerpts by default.
- Should `labs_reviewer` receive examples as explicit structured input in schema (future enhancement) instead of text-only prompt injection? Yes
