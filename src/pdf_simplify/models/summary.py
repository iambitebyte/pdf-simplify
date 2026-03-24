"""Summary data models."""

from typing import List, Optional
from pydantic import BaseModel, Field


class KeyConcept(BaseModel):
    """Key concept extracted from document."""

    concept: str = Field(description="The key concept")
    description: str = Field(description="Description of the concept")
    importance: str = Field(description="Importance level: high, medium, or low")


class Chapter(BaseModel):
    """Chapter or section of the document."""

    title: str = Field(description="Chapter or section title")
    page_range: str = Field(description="Page range (e.g., '1-25')")
    summary: str = Field(description="Summary of this chapter")
    key_points: List[str] = Field(default_factory=list, description="Key points in this chapter")
    key_concepts: List[KeyConcept] = Field(
        default_factory=list, description="Key concepts in this chapter"
    )


class Summary(BaseModel):
    """Complete document summary."""

    document_title: str = Field(description="Title of the document")
    document_path: str = Field(description="Path to the document")
    overall_summary: str = Field(description="Overall summary of the entire document")
    chapters: List[Chapter] = Field(default_factory=list, description="Chapter summaries")
    key_concepts: List[KeyConcept] = Field(
        default_factory=list, description="Key concepts across document"
    )
    main_themes: List[str] = Field(default_factory=list, description="Main themes of the document")
    target_audience: str = Field(description="Target audience of the document")
    reading_time_saved: str = Field(description="Estimated reading time saved")

    def to_markdown(self) -> str:
        """Convert summary to markdown format.

        Returns:
            Markdown formatted summary
        """
        md = f"# {self.document_title}\n\n"
        md += f"**Overall Summary**\n\n{self.overall_summary}\n\n"

        if self.target_audience:
            md += f"**Target Audience:** {self.target_audience}\n\n"

        if self.reading_time_saved:
            md += f"**Reading Time Saved:** {self.reading_time_saved}\n\n"

        if self.main_themes:
            md += "## Main Themes\n\n"
            for theme in self.main_themes:
                md += f"- {theme}\n"
            md += "\n"

        if self.key_concepts:
            md += "## Key Concepts\n\n"
            for concept in self.key_concepts:
                md += f"### {concept.concept}\n"
                md += f"{concept.description}\n"
                md += f"*Importance: {concept.importance}*\n\n"

        if self.chapters:
            md += "## Chapter Summaries\n\n"
            for chapter in self.chapters:
                md += f"### {chapter.title}\n"
                md += f"*Pages: {chapter.page_range}*\n\n"
                md += f"{chapter.summary}\n\n"

                if chapter.key_points:
                    md += "**Key Points:**\n"
                    for point in chapter.key_points:
                        md += f"- {point}\n"
                    md += "\n"

                if chapter.key_concepts:
                    md += "**Key Concepts:**\n"
                    for concept in chapter.key_concepts:
                        md += f"- {concept.concept}: {concept.description}\n"
                    md += "\n"

        return md

    def to_json(self) -> str:
        """Convert summary to JSON format.

        Returns:
            JSON string of summary
        """
        return self.model_dump_json(indent=2)
