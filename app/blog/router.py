"""HTTP routes for Blog Post Writer features."""

from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile

from blog.agents.blog_reviewer.schema import BlogReviewerRequest, BlogReviewerResponse
from blog.service import BlogPostService

router = APIRouter(prefix="/blog-post-writer", tags=["Blog Post Writer"])
service = BlogPostService()


@router.post("/organize-notes")
async def organize_notes(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
) -> dict[str, str]:
    """Transform markdown notes into a structured blog post."""
    raw_content = await file.read()
    try:
        context = raw_content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=400, detail="File must be UTF-8 encoded.") from exc

    return service.enqueue_markdown_organization(
        background_tasks=background_tasks,
        filename=file.filename or "",
        context=context,
    )
