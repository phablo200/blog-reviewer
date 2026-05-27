# Title
Labs Post Metadata Agent Integration

## Objective
- Introduce a dedicated `labs_post_metadata` agent that generates post metadata before content writing.
- Ensure the final reviewed markdown (and translated markdown) includes agent-generated frontmatter instead of static fallback metadata.

## Background
- Current flow starts in `POST /labs/review`, then `LabPostService` enqueues `MarkdownHelper.process_and_save_markdown`.
- `MarkdownHelper` currently guarantees metadata with `ensure_required_frontmatter`, using hardcoded defaults for `title`, `date`, and `summary`.
- A new empty structure exists at `labs/agents/labs_post_metadata`, but it is not integrated yet.
- Writer pipeline (`LabPostWriterAgent.organize_notes`) currently produces body content only; metadata is added after writing.

## Scope
### In Scope
- Implement `labs/agents/labs_post_metadata` agent (`agent.py`, `schema.py`, `prompts.py`) to produce:
  - `title`
  - `date`
  - `summary`
  - `tags`
  - `published`
- Run metadata generation before post writing within markdown processing flow.
- Merge generated metadata with reviewed markdown body to produce final frontmatter+body output.
- Keep required key enforcement for resilience if metadata generation is partial/fails.
- Add/adjust tests for metadata generation and final markdown composition.

### Out of Scope
- Changing endpoint contracts (`POST /labs/review`, `/outputs/*`).
- Renaming existing writer method names (`organize_notes`) as part of this task.
- Changing storage paths or filename conventions (`*_reviewd*`).
- Introducing database persistence for metadata.

## Proposed Approach
- Implement a typed metadata contract in `labs/agents/labs_post_metadata/schema.py`:
  - `LabPostMetadataRequest` with source context text.
  - `LabPostMetadataResponse` with structured frontmatter fields.
- Implement metadata prompt in `labs/agents/labs_post_metadata/prompts.py` that constrains output to the required schema and language expectations.
- Implement `LabPostMetadataAgent` in `labs/agents/labs_post_metadata/agent.py` using `build_chat_model(...)` and structured output parsing pattern consistent with `labs_reviewer`.
- Extend `MarkdownHelper` to orchestrate:
  1. Metadata generation from raw `context`.
  2. Body generation via `writer_agent.organize_notes(...)`.
  3. Frontmatter composition from metadata + reviewed body.
  4. Translation and PDF generation as today.
- Refactor frontmatter utilities in `MarkdownHelper`:
  - Keep normalization/parsing helpers.
  - Add a deterministic `build_frontmatter(metadata)` formatter.
  - Apply fallback defaults only for missing fields when metadata output is incomplete.
- Update `LabPostService` initialization/dependencies to pass metadata agent into the processing path.

Impacted modules:
- `labs/agents/labs_post_metadata/agent.py`
- `labs/agents/labs_post_metadata/schema.py`
- `labs/agents/labs_post_metadata/prompts.py`
- `labs/helpers/markdown_helper.py`
- `labs/service.py`
- `tests/test_helper.py`
- New tests for metadata agent behavior (for example `tests/test_post_metadata_agent.py`)

## Milestones
1. Metadata agent implementation
- Define request/response schemas and prompt.
- Implement agent invocation + structured output fallback handling.

2. Pipeline integration
- Inject metadata agent into service/helper flow before writer execution.
- Compose final markdown with generated frontmatter + reviewed body.

3. Validation hardening
- Preserve existing fallback behavior for robustness.
- Add tests for metadata-first flow, fallback behavior, and final file outputs.

## Edge Cases
- Metadata agent returns empty/invalid fields:
  - Fill missing fields with current defaults and continue.
- Writer output already contains frontmatter:
  - Strip/normalize and replace with metadata-agent frontmatter to avoid duplicated blocks.
- Metadata agent failure (timeout/provider error):
  - Continue flow with existing fallback metadata behavior and log exception.
- Non-UTF8 or invalid input remains handled at router layer as currently implemented.

## Acceptance Criteria
- [ ] Metadata agent is implemented under `labs/agents/labs_post_metadata` and used in runtime flow.
- [ ] For a successful `/labs/review` request, generated markdown frontmatter comes from metadata agent output.
- [ ] Final EN/PT-BR markdown files include all required keys: `title`, `date`, `summary`, `tags`, `published`.
- [ ] If metadata agent fails or partially responds, pipeline still succeeds using fallback defaults for missing values.
- [ ] Existing PDF generation and outputs listing behavior remains unchanged.

## Test Plan
- Unit:
  - Metadata schema validation and normalization tests.
  - `MarkdownHelper` tests for frontmatter composition with:
    - full metadata
    - partial metadata
    - metadata failure fallback
- Integration:
  - Service-level test ensuring metadata generation is invoked before writer flow.
  - Output markdown contains exactly one frontmatter block with required keys.
- Manual verification:
  - Call `POST /labs/review` with sample `.md`.
  - Confirm resulting `public/markdown/*_reviewd.md` and `*_reviewd_pt_br.md` contain metadata-agent frontmatter.
  - Confirm corresponding PDFs are still generated.

## Risks and Mitigations
- Risk: LLM structured output drift causes malformed metadata.
  - Mitigation: Strict schema validation + fallback defaults per field.
- Risk: Frontmatter duplication from mixed writer/metadata outputs.
  - Mitigation: Normalize by extracting/removing any existing frontmatter before final composition.
- Risk: Added latency from extra agent call.
  - Mitigation: Keep metadata prompt concise; log timing for future optimization.

## Open Questions
- Should metadata be generated from raw user notes only, or from the reviewed body for better title/summary quality? From the reviewed body, for better title, summary and quality.
- Should `date` always be generation date (today) when missing, or should agent infer from content? The generation date.
- Should translated markdown reuse the same frontmatter language as EN or localize `title/summary/tags` for pt-BR output? The same EN, to better robustness.
