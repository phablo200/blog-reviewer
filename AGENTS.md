# Repository Guidelines

## Project Structure & Module Organization
- `main.py`: FastAPI app entrypoint, CORS setup, and router registration.
- `blog/`: feature code for blog workflows.
- `blog/router.py`: HTTP routes under `/blog-post-writer`.
- `blog/service.py`: orchestration/business logic used by routes.
- `blog/agents/`: LLM agent implementations (`blog_post_writer`, `blog_reviewer`, `blog_post_translator`) with `agent.py`, `schema.py`, and prompt/constants helpers.
- `blog/posts/`: generated or reviewed markdown outputs.
- `core/`: shared config and LLM setup (`config.py`, `llm_config.py`).
- `.env.example`: required environment variables template.

## Build, Test, and Development Commands
- `python -m venv venv && source venv/bin/activate`: create and activate local environment.
- `pip install -r requirements.txt`: install runtime dependencies.
- `uvicorn main:app --reload --host 0.0.0.0 --port 3015`: run API locally with hot reload.
- `python -m compileall main.py blog core`: quick syntax validation across modules.
- `docker build -t blog-reviewer-app .`: build container image from `Dockerfile`.
- `docker run --env-file .env -p 3015:80 blog-reviewer-app`: run containerized API.

## Coding Style & Naming Conventions
- Use Python 3.12 style, 4-space indentation, UTF-8 source files.
- Prefer type hints on public functions and return values (as seen in `main.py` and `blog/router.py`).
- Keep modules focused: route handlers in `router.py`, orchestration in `service.py`, data contracts in `schema.py`.
- Use `snake_case` for functions/variables, `PascalCase` for classes, and explicit names for agent folders.

## Testing Guidelines
- There is no first-party test suite yet; add tests for new behavior.
- Place tests in a top-level `tests/` directory using names like `test_router.py` and `test_service.py`.
- Recommended stack: `pytest` + `fastapi.testclient`.
- Minimum expectation for PRs that change behavior: one request-level route test and one unit test for service/agent logic.

## Commit & Pull Request Guidelines
- This workspace does not expose git history; use Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`) in imperative mood.
- Keep each commit scoped to one logical change.
- PRs should include: summary, why the change is needed, test evidence (command/output), env/config changes, and sample request/response for API changes.
- Link related issue/task IDs and include screenshots only when UI/docs rendering is affected.

## Security & Configuration Tips
- Never commit `.env` or real API keys.
- Copy `.env.example` to `.env` and set `OPENAI_API_KEY`, `GROQ_API_KEY`, model names, and `MEBRAIN_SYSTEM_API_URL` per environment.
- Treat files under `blog/posts/` as generated artifacts unless intentionally curated.

## Rules
- Read `.codex/instructions.md` to specific rules of this system.