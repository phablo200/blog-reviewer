class LabPostMetadataPrompt:
    """Prompt templates for metadata extraction."""

    @staticmethod
    def build_system_prompt() -> str:
        return """You generate blog post metadata from reviewed markdown content.

Output metadata in English with these fields:
- title
- date (YYYY-MM-DD)
- summary
- tags (list of strings)
- published (boolean)

Rules:
- Keep title concise and specific.
- Keep summary to 1-2 sentences.
- Prefer practical professional tags.
- If uncertain, still provide best-effort values.
- Do not include markdown body content in metadata fields."""
