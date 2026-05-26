from pydantic import BaseModel, Field


class LabPostWriterRequest(BaseModel):
    """Raw sketch notes used to craft a structured blog post draft."""

    context: str = Field(
        ...,
        description="Raw notes and ideas that should be transformed into a coherent blog post.",
    )


class LabPostWriterResponse(BaseModel):
    """Reviewed blog post content in Markdown format."""

    reviewed_markdown: str = Field(
        description="Final reviewed blog post in pure Markdown format.",
    )
