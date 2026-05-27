from pydantic import BaseModel, Field


class LabCodeExampleRequest(BaseModel):
    """Input context used to extract repository-grounded code examples."""

    notes_context: str = Field(
        ...,
        description="Raw sketch notes plus any enriched repository context.",
    )
    repositories: list[str] = Field(
        default_factory=list,
        description="Normalized repositories in owner/repo format.",
    )
    max_examples: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Maximum number of examples to return.",
    )


class LabCodeExampleItem(BaseModel):
    """A single repository-backed code example."""

    repository: str = Field(..., description="Repository identifier in owner/repo format.")
    file_path: str = Field(..., description="Path to the file containing the snippet.")
    language: str = Field(..., description="Detected language for the snippet.")
    snippet: str = Field(..., description="Short code snippet extracted from repository files.")
    why_it_matters: str = Field(..., description="Why this snippet is relevant to the post.")
    integration_hint: str = Field(
        ...,
        description="How the writer should integrate this example into the post narrative.",
    )


class LabCodeExampleResponse(BaseModel):
    """Structured response for extracted code examples."""

    examples: list[LabCodeExampleItem] = Field(default_factory=list)
    summary: str = Field(
        default="",
        description="High-level summary of suggested examples.",
    )
    warnings: list[str] = Field(
        default_factory=list,
        description="Non-fatal warnings encountered during extraction.",
    )
