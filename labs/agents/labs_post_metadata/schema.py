"""Schemas for metadata generation."""

from pydantic import BaseModel, Field


class LabPostMetadataRequest(BaseModel):
    """Input payload for metadata generation."""

    content: str = Field(description="Reviewed markdown content used to infer metadata.")


class LabPostMetadataResponse(BaseModel):
    """Normalized metadata fields required in post frontmatter."""

    title: str = Field(default="", description="Post title in English.")
    date: str = Field(default="", description="Post date in YYYY-MM-DD.")
    summary: str = Field(default="", description="Short summary in English.")
    tags: list[str] = Field(default_factory=list, description="Post tags.")
    published: bool = Field(default=True, description="Publish flag.")
