"""Tests for pdf-simplify package."""

import pytest
from pdf_simplify.core.parser import PDFParser
from pdf_simplify.core.chunker import TextChunker


@pytest.fixture
def sample_text():
    """Sample text for testing."""
    return """
    This is a sample document. It contains multiple sentences. Each sentence ends with a period!
    The purpose of this text is to test the chunking functionality. We need to ensure that
    text is split correctly at sentence boundaries when possible. The chunker should be
    smart enough to avoid breaking mid-sentence unless absolutely necessary.

    Here is another paragraph with different content. This paragraph discusses the importance
    of proper text processing. When working with large documents, it's crucial to handle
    text in manageable chunks. This approach ensures better performance and accuracy.
    """


class TestTextChunker:
    """Tests for TextChunker class."""

    def test_basic_chunking(self, sample_text):
        """Test basic text chunking."""
        chunker = TextChunker(chunk_size=200, chunk_overlap=50)
        chunks = chunker.chunk_text(sample_text)

        assert len(chunks) > 0
        assert all("text" in chunk for chunk in chunks)

    def test_sentence_boundary_respect(self, sample_text):
        """Test that sentence boundaries are respected."""
        chunker = TextChunker(chunk_size=200, chunk_overlap=50, respect_sentences=True)
        chunks = chunker.chunk_text(sample_text)

        for chunk in chunks:
            text = chunk["text"]
            if len(text) < len(sample_text):
                assert text.rstrip()[-1] in {".", "!", "?", "\n"}
