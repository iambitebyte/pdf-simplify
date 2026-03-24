"""Text chunking for LLM processing."""

from typing import List, Dict
import re


class TextChunker:
    """Split text into chunks for LLM processing."""

    def __init__(
        self, chunk_size: int = 4000, chunk_overlap: int = 200, respect_sentences: bool = True
    ):
        """Initialize text chunker.

        Args:
            chunk_size: Maximum characters per chunk
            chunk_overlap: Overlap between chunks
            respect_sentences: Try to split at sentence boundaries
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.respect_sentences = respect_sentences

    def chunk_text(self, text: str) -> List[Dict]:
        """Split text into chunks.

        Args:
            text: Input text

        Returns:
            List of chunks with metadata
        """
        chunks = []
        start = 0

        while start < len(text):
            end = start + self.chunk_size

            if end >= len(text):
                chunks.append(
                    {
                        "text": text[start:],
                        "start_pos": start,
                        "end_pos": len(text),
                        "chunk_id": len(chunks),
                    }
                )
                break

            if self.respect_sentences:
                end = self._find_sentence_boundary(text, end)

            chunks.append(
                {
                    "text": text[start:end],
                    "start_pos": start,
                    "end_pos": end,
                    "chunk_id": len(chunks),
                }
            )

            start = end - self.chunk_overlap

        return chunks

    def chunk_pages(self, pages: List[Dict]) -> List[Dict]:
        """Chunk text from pages.

        Args:
            pages: List of pages with text

        Returns:
            List of chunks across pages
        """
        full_text = "\n\n".join(page["text"] for page in pages)
        chunks = self.chunk_text(full_text)

        for chunk in chunks:
            chunk["source_type"] = "pages"

        return chunks

    def _find_sentence_boundary(self, text: str, position: int) -> int:
        """Find the nearest sentence boundary.

        Args:
            text: Text to search
            position: Approximate position

        Returns:
            Position at sentence boundary
        """
        window = 200
        search_text = text[position : min(position + window, len(text))]

        for i, char in enumerate(search_text):
            if char in {".", "!", "?"}:
                if i + 1 < len(search_text) and search_text[i + 1] in {" ", "\n"}:
                    return position + i + 1

        return position
