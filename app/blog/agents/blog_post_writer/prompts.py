class BlogPostWriterPrompt:
    """Prompt templates for blog post writing and structuring."""

    @staticmethod
    def build_system_prompt() -> str:
        """Build the system prompt for transforming notes into a coherent post."""
        return """You are an expert blog writer.

Your task is to read sketch notes and transform them into a clear, coherent, and useful blog post.

Rules:
1. Use all relevant information from the provided context.
2. Remove duplication, vague fragments, and disconnected notes.
3. Organize the post with a logical flow (introduction, core sections, conclusion).
4. Keep a practical and readable tone.
5. Return only the final blog post content in Markdown.
6. Do not return JSON.
7. Do not add commentary before or after the Markdown."""
