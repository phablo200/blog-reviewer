from pydantic import BaseModel, Field


class LabReviewerRequest(BaseModel):
    """Raw markdown post that should be revised."""

    content: str = Field(
        ...,
        description="Original blog post content in Markdown.",
    )


class LabReviewerStructuredResponse(BaseModel):
    """Structured response produced by the model."""

    revised_post: str = Field(
        ...,
        description="Full revised version of the original blog post in Markdown.",
    )
    errors_found: list[str] = Field(
        ...,
        description="Concrete issues identified in the original post.",
    )
    improvement_tips: list[str] = Field(
        ...,
        description="Actionable tips to improve quality in future revisions.",
    )
    next_revision_checklist: list[str] = Field(
        ...,
        description="Checklist items for the next review pass.",
    )


class LabReviewerResponse(BaseModel):
    """Reviewed post and structured feedback."""

    revised_post: str = Field(
        ...,
        description="Full revised version of the original blog post in Markdown.",
    )
    errors_found: list[str] = Field(
        ...,
        description="Concrete issues identified in the original post.",
    )
    improvement_tips: list[str] = Field(
        ...,
        description="Actionable tips to improve quality in future revisions.",
    )
    next_revision_checklist: list[str] = Field(
        ...,
        description="Checklist items for the next review pass.",
    )
