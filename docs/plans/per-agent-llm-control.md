# Plan: Per-Agent LLM Control

## Goal
Enable explicit LLM provider/model/temperature control per labs agent while preserving current `/labs/review` behavior and fallback safety.

## Confirmed Decisions
- Keep `core/llm_config.py` as the central model factory.
- Use env-first configuration for this phase (no YAML yet).
- Introduce role-based model selection per agent.
- Keep backward compatibility with existing global keys (`OPENAI_MODEL`, `GROQ_MODEL`, etc.).
- Do not apply request-header overrides in this phase.

## Assumptions
- Existing provider support remains `openai` and `groq` only.
- Agent constructor refactor can be done without changing external HTTP contracts.
- Missing/invalid role config should not break startup when fallback is possible.

## Milestone 1: Extend LLM Factory with Agent Roles
1. Update `core/llm_config.py`:
- Add `AgentRole` enum for current labs agents:
  - `POST_WRITER`, `CODE_EXAMPLE`, `REVIEWER`, `METADATA`, `TRANSLATOR`.
- Add `build_chat_model_for_agent(agent_role: AgentRole)`.
- Implement env key resolution:
  - `LLM_<ROLE>_PROVIDER`
  - `LLM_<ROLE>_MODEL`
  - `LLM_<ROLE>_TEMPERATURE`
- Implement fallback chain:
  1) role-specific keys
  2) provider-level global keys
  3) hardcoded defaults
2. Add provider/model compatibility validation and warning logs with safe fallback.

Deliverables:
- Role-aware model factory API with deterministic fallback behavior.

## Milestone 2: Constants and Config Surface
1. Update `core/contants.py` if needed:
- Ensure allowed provider/model sets are reusable by factory validation.
2. Update `.env.example`:
- Add all per-agent keys with defaults.
- Keep existing global keys for compatibility.

Deliverables:
- Documented and usable config surface for per-agent LLM control.

## Milestone 3: Agent Constructor Refactor for Injection
1. Update constructors to accept optional injected LLM:
- `labs/agents/labs_post_writer/agent.py`
- `labs/agents/labs_code_example/agent.py`
- `labs/agents/labs_reviewer/agent.py`
- `labs/agents/labs_post_metadata/agent.py`
- `labs/agents/labs_post_translator/agent.py`
2. Keep backward compatibility:
- If `llm is None`, resolve via `build_chat_model_for_agent(...)`.

Deliverables:
- Agents support dependency injection and still work with default construction.

## Milestone 4: Centralized Service Wiring
1. Update `labs/service.py`:
- Build per-agent LLM instances via factory once in service initialization.
- Inject these LLMs into each agent constructor.
2. Keep route/service contracts unchanged.

Deliverables:
- Single central wiring point for agent LLM policy.

## Milestone 5: Test Coverage and Verification
1. Add `tests/test_llm_config.py`:
- Role-specific config resolution.
- Fallback to global config when role keys missing.
- Invalid role-model compatibility fallback behavior.
2. Update service/agent tests as needed:
- `tests/test_service.py` for service construction/wiring stability.
- Adapt existing writer/code-example tests if constructor signatures changed.
3. Verification commands:
- `venv/bin/python -m compileall core labs tests`
- `venv/bin/python -m pytest -q tests/test_llm_config.py tests/test_service.py tests/test_labs_code_example_agent.py tests/test_labs_post_writer_agent.py`

Deliverables:
- Automated validation of role-based config and no regression in core pipeline.

## Milestone 6: Operational Validation
1. Manual local run:
- Set mixed role config (example: reviewer=groq, writer=openai).
- Run API and trigger `POST /labs/review` with sample markdown.
2. Confirm:
- pipeline completes
- expected role-level providers/models are logged/used
- fallback works on invalid role config.

Deliverables:
- Manual evidence that per-agent control works in realistic runtime conditions.

## Execution Order
1. Milestone 1
2. Milestone 2
3. Milestone 3
4. Milestone 4
5. Milestone 5
6. Milestone 6

## Risks
- Misconfigured role env values can silently degrade output quality.
- Constructor refactor can break tests relying on prior defaults.
- Provider/model validation rules may drift from actual provider availability.

Mitigations:
- Emit explicit warnings whenever fallback is applied.
- Keep constructor defaults and update tests incrementally.
- Centralize provider/model allowlists and test them.

## Rollback Strategy
1. Revert `labs/service.py` to direct agent construction without injected LLMs.
2. Revert agents to provider-hardcoded constructor behavior.
3. Keep role-based keys ignored while preserving global model keys.

## Definition of Done
- Each labs agent can be configured independently via env provider/model/temperature keys.
- Existing flows still work with only global config keys.
- Service initializes all agents with explicit role-based LLM wiring.
- Validation and fallback behavior are covered by tests.
- Compile and targeted tests pass.
