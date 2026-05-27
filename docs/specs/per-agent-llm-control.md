## Title
Per-Agent LLM Control and Factory Integration

## Objective
- Enable explicit LLM selection per agent (provider, model, temperature) instead of relying only on global provider defaults.
- Keep current architecture (`core/llm_config.py`) as the central place for model construction and policy.
- Preserve safe fallback behavior and compatibility with existing `/labs/review` flow.

## Background
- Current `core/llm_config.py` supports only two providers (`openai`, `groq`) and global env keys (`OPENAI_MODEL`, `GROQ_MODEL`, temperatures).
- Agents instantiate their own models in constructors with fixed provider choices:
  - `LabPostWriterAgent` -> OpenAI
  - `LabCodeExampleAgent` -> OpenAI
  - `LabPostMetadataAgent` -> OpenAI
  - `LabPostTranslatorAgent` -> OpenAI
  - `LabReviewerAgent` -> Groq
- `RequiredHeadersMiddleware` validates optional `llm`, `llm_model`, `llm_temperature`, but those header values are not currently consumed by `build_chat_model(...)` or agent constructors.
- Result: model tuning per agent is not configurable without code edits.

## Scope
### In Scope
- Extend `core/llm_config.py` to build models by agent role using dedicated env configuration.
- Define a typed agent-role registry and defaults for all current labs agents.
- Update agent constructors to receive an injected LLM (dependency injection), with backward-compatible defaults.
- Centralize agent wiring in `LabPostService` so per-agent LLM policy is configured in one place.
- Update `.env.example` with per-agent configuration keys.
- Add tests for config resolution and agent wiring behavior.

### Out of Scope
- Adding new external providers immediately (e.g., Anthropic/Ollama) in this iteration.
- Dynamic per-request routing based on HTTP headers.
- Replacing env-based config with YAML in this first phase.
- Pricing/latency optimization engine or automatic model benchmarking.

## Proposed Approach
- Keep `core/llm_config.py` as the single factory module; add agent-aware API:
  - `AgentRole` enum (e.g., `POST_WRITER`, `CODE_EXAMPLE`, `REVIEWER`, `METADATA`, `TRANSLATOR`).
  - `build_chat_model_for_agent(agent_role: AgentRole)`.
- Add per-agent env keys with fallback chain:
  1. `LLM_<ROLE>_PROVIDER`, `LLM_<ROLE>_MODEL`, `LLM_<ROLE>_TEMPERATURE`
  2. Provider-level defaults (`OPENAI_MODEL`, `GROQ_MODEL`, etc.)
  3. hardcoded defaults in `core/contants.py`
- Validate provider/model compatibility in factory:
  - Reuse allowed values from `core/contants.py`.
  - If invalid per-agent model is configured, log warning and fallback to provider default model.
- Refactor agent constructors for injection:
  - `def __init__(self, llm: BaseChatModel | None = None)`
  - If `llm is None`, call `build_chat_model_for_agent(...)` for that role.
- Service-level wiring (`labs/service.py`):
  - Instantiate each agent with explicit LLM from factory once, so runtime policy is transparent.
- Keep middleware unchanged in this phase; document it as future extension for request-scoped overrides.

Impacted files/modules:
- `core/llm_config.py`
- `core/contants.py`
- `.env.example`
- `labs/service.py`
- `labs/agents/labs_post_writer/agent.py`
- `labs/agents/labs_code_example/agent.py`
- `labs/agents/labs_post_metadata/agent.py`
- `labs/agents/labs_post_translator/agent.py`
- `labs/agents/labs_reviewer/agent.py`
- `tests/test_llm_config.py` (new)
- `tests/test_service.py` (update)

### Configuration Shape (env-first)
- `LLM_POST_WRITER_PROVIDER=openai|groq`
- `LLM_POST_WRITER_MODEL=<provider-model>`
- `LLM_POST_WRITER_TEMPERATURE=<0..1>`
- `LLM_CODE_EXAMPLE_PROVIDER=...`
- `LLM_CODE_EXAMPLE_MODEL=...`
- `LLM_CODE_EXAMPLE_TEMPERATURE=...`
- `LLM_REVIEWER_PROVIDER=...`
- `LLM_REVIEWER_MODEL=...`
- `LLM_REVIEWER_TEMPERATURE=...`
- `LLM_METADATA_PROVIDER=...`
- `LLM_METADATA_MODEL=...`
- `LLM_METADATA_TEMPERATURE=...`
- `LLM_TRANSLATOR_PROVIDER=...`
- `LLM_TRANSLATOR_MODEL=...`
- `LLM_TRANSLATOR_TEMPERATURE=...`

## Milestones
1. Factory extension and role model
- Add `AgentRole` and `build_chat_model_for_agent(...)` in `core/llm_config.py`.
- Implement fallback and compatibility validation logic.

2. Agent injection refactor
- Update all labs agent constructors to accept injected `llm` with backward-compatible fallback.

3. Service wiring
- Update `LabPostService.__init__` to construct per-agent LLMs via factory and inject them.

4. Config docs and examples
- Update `.env.example` with role-specific keys and sane defaults (e.g., reviewer on Groq, others on OpenAI unless overridden).

5. Tests and verification
- Add unit tests for role config resolution and fallback behavior.
- Update service tests to ensure wiring succeeds with injected models.

## Edge Cases
- Per-agent provider is valid but model belongs to a different provider.
- Per-agent temperature is not numeric or out of range.
- Missing API key for selected provider.
- Unknown role key in env.
- Runtime provider outage for one agent while others remain functional.

## Acceptance Criteria
- [ ] Each labs agent can use a distinct provider/model/temperature configured without code changes.
- [ ] Existing `/labs/review` behavior remains functional when only old global env keys are present.
- [ ] Invalid per-agent config falls back safely with clear logs (no boot crash for recoverable cases).
- [ ] `LabPostService` is the central place where agent LLM policy is wired.
- [ ] Automated tests cover role config resolution and at least two fallback scenarios.

## Test Plan
- Unit:
  - `build_chat_model_for_agent(...)` returns expected provider/model for role-specific env.
  - Invalid role-specific model falls back to provider default.
  - Missing role-specific values fall back to global provider keys.
- Integration:
  - Service initialization builds all agents with injected LLM instances.
  - `/labs/review` happy-path smoke with mocks still completes.
- Manual verification:
  - Run with mixed role config (e.g., reviewer on Groq, writer on OpenAI) and verify logs/behavior.

## Risks and Mitigations
- Risk: Config sprawl in `.env` reduces maintainability.
  - Mitigation: strict naming convention + documented fallback chain + future YAML phase.
- Risk: Invalid model/provider pairs cause runtime failures.
  - Mitigation: startup-time validation with fallback and explicit warning logs.
- Risk: Refactor may break tests relying on constructor side effects.
  - Mitigation: keep constructor defaults backward-compatible and update stubs incrementally.

## Open Questions
- Should request headers (`llm`, `llm_model`, `llm_temperature`) override per-agent config for all agents in a request, or stay disabled for now? Recommendation: disabled for now; Use the values used in `models.yaml`.
- Should Anthropic/Ollama be added now or deferred? Recommendation: defer to phase 2 after env-based per-agent control is stable.
- Should we move from env to `models.yaml` in this same change? Yes models.yaml will become the main entry to control our llms.
