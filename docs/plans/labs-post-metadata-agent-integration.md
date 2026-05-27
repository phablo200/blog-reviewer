# Plan: Labs Post Metadata Agent Integration

## Goal
Implement and integrate a dedicated metadata agent that runs before post writing, then injects generated frontmatter into final reviewed EN/PT-BR markdown outputs.

## Confirmed Decisions
- Metadata source: generate metadata from the reviewed body for better quality.
- Missing date behavior: use generation date (today) when missing.
- PT-BR output behavior: keep frontmatter in EN for robustness.

## Assumptions
- Endpoint contracts stay unchanged in this task (`POST /labs/review`, `GET /outputs/*`).
- Existing filename/output conventions remain unchanged (`*_reviewd*`).
- Metadata agent output is best-effort and must not break the processing pipeline.

## Milestone 1: Metadata Agent Implementation
1. Implement metadata schemas in `labs/agents/labs_post_metadata/schema.py`:
- `LabPostMetadataRequest` with source content input.
- `LabPostMetadataResponse` with `title`, `date`, `summary`, `tags`, `published`.
2. Implement prompt template in `labs/agents/labs_post_metadata/prompts.py`:
- Constrain output to required fields and expected format semantics.
- Ensure EN metadata expectation is explicit.
3. Implement `LabPostMetadataAgent` in `labs/agents/labs_post_metadata/agent.py`:
- Use `build_chat_model(...)` from `core.llm_config`.
- Use structured output validation with fallback handling for partial/invalid results.

Deliverables:
- Working metadata agent with typed input/output and predictable fallback behavior.

## Milestone 2: Markdown Helper Integration
1. Update `labs/helpers/markdown_helper.py` orchestration flow:
- Generate reviewed body through writer agent.
- Run metadata agent using reviewed body as input.
- Build normalized frontmatter block from metadata.
- Compose final markdown as `frontmatter + reviewed body`.
2. Keep resilience behavior:
- If metadata call fails, keep pipeline running with per-field fallback defaults.
- If writer output contains frontmatter, normalize to one authoritative frontmatter block.
3. Keep translation/PDF flow unchanged after final EN markdown is composed.

Deliverables:
- Metadata-first final composition integrated into markdown processing pipeline.

## Milestone 3: Service Wiring
1. Update `labs/service.py` dependency wiring:
- Instantiate `LabPostMetadataAgent` in service constructor.
- Pass metadata agent into `MarkdownHelper.process_and_save_markdown(...)`.
2. Keep route/service API responses unchanged.

Deliverables:
- Runtime flow includes metadata agent without contract changes.

## Milestone 4: Test Coverage
1. Add metadata-agent tests (new file, e.g. `tests/test_post_metadata_agent.py`):
- Valid structured output path.
- Partial/invalid output fallback behavior.
2. Update `tests/test_helper.py`:
- Verify final markdown includes a single frontmatter block.
- Verify frontmatter uses metadata-agent values when available.
- Verify fallback defaults are applied for missing fields.
3. Update/add service-level tests (`tests/test_service.py`):
- Validate metadata integration call path in background orchestration.

Deliverables:
- Passing tests that cover metadata generation, composition, and fallback safety.

## Milestone 5: Verification and Cleanup
1. Static verification:
- `venv/bin/python -m compileall labs tests`
2. Focused tests:
- `venv/bin/python -m pytest -q tests/test_post_metadata_agent.py tests/test_helper.py tests/test_service.py tests/test_outputs_router.py`
3. Manual validation:
- Submit a markdown file to `POST /labs/review`.
- Verify EN and PT-BR markdown outputs include required frontmatter keys.
- Verify PDF generation and `/outputs/pdf` listing still behave as before.

Deliverables:
- Verified end-to-end behavior without regressions in outputs flow.

## Execution Order
1. Milestone 1
2. Milestone 2
3. Milestone 3
4. Milestone 4
5. Milestone 5

## Risks
- Structured output drift from metadata model may produce malformed fields.
- Frontmatter duplication if writer output includes its own metadata block.
- Additional latency due to one extra model invocation.

Mitigations:
- Strict schema validation and per-field fallback defaults.
- Explicit normalization to one final frontmatter block.
- Keep prompt concise and add logging around metadata step timing.

## Rollback Strategy
1. Revert metadata-agent invocation in `labs/helpers/markdown_helper.py`.
2. Restore previous fallback-only frontmatter composition behavior.
3. Keep new agent files isolated and removable without endpoint changes.

## Definition of Done
- Metadata agent runs in runtime flow and is integrated before final markdown persistence.
- Final EN/PT-BR markdown outputs include required keys from metadata agent when available.
- Fallback defaults preserve successful processing on metadata failures.
- Existing outputs/PDF/listing behavior remains stable.
- Targeted compile and test commands pass.
