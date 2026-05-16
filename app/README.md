# Blog Reviewer API

FastAPI service that converts raw Markdown notes into a reviewed blog post, translates it to pt-BR, and provides direct blog revision endpoints using LLM agents.

## Features
- Organize raw notes into a polished Markdown post.
- Automatically generate a Brazilian Portuguese version.
- Revise existing blog posts with structured feedback:
  - `errors_found`
  - `improvement_tips`
  - `next_revision_checklist`

## Project Structure
- `main.py`: app entrypoint and middleware.
- `blog/router.py`: API routes (`/blog-post-writer/*`).
- `blog/service.py`: orchestration for writer, translator, and reviewer agents.
- `blog/agents/`: feature-specific agents and schemas.
- `blog/posts/`: generated output markdown files.
- `core/`: shared config and LLM setup.

## Requirements
- Python 3.12+
- API keys for configured providers (`OPENAI_API_KEY`, optional `GROQ_API_KEY`)

## Setup
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` with your keys and runtime values.

## Run Locally
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 3015
```

Health check:
```bash
curl http://127.0.0.1:3015/
```

## API Endpoints
### `POST /blog-post-writer/organize-notes`
Accepts a UTF-8 `.md` upload (`file`). Processing runs in background.

Example:
```bash
curl -X POST http://127.0.0.1:3015/blog-post-writer/organize-notes \
  -F "file=@notes.md"
```

Returns output path for the reviewed file. The service also writes a translated file with `_pt_br` suffix.

## Docker
```bash
docker build -t blog-reviewer-app .
docker run --env-file .env -p 3015:80 blog-reviewer-app
```

## Notes
- Only `.md` files are accepted in `organize-notes`.
- Output filenames are derived from the uploaded filename and written under `blog/posts/`.
- Do not commit `.env` or real API keys.
