from pydantic import BaseModel, Field


class BlogPostTranslatorRequest(BaseModel):
    """Reviewed English markdown post that should be translated."""

    content: str = Field(
        ...,
        description="Reviewed blog post content in English Markdown format.",
    )


class BlogPostTranslatorResponse(BaseModel):
    """Translated blog post content in Brazilian Portuguese."""

    translated_markdown: str = Field(
        ...,
        description="Final translated blog post in pt-BR Markdown format.",
    )
