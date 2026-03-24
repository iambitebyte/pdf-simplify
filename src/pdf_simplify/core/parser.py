"""PDF document parser."""

from pathlib import Path
from typing import List, Optional
import pdfplumber


class PDFParser:
    """Parse PDF documents and extract text content."""

    def __init__(self, pdf_path: str):
        """Initialize PDF parser.

        Args:
            pdf_path: Path to PDF file
        """
        self.pdf_path = Path(pdf_path)
        self._document: Optional[pdfplumber.PDF] = None

    def parse(self) -> List[dict]:
        """Parse PDF document.

        Returns:
            List of pages with text content
        """
        with pdfplumber.open(self.pdf_path) as pdf:
            pages = []
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text() or ""
                pages.append({"page_number": page_num, "text": text, "char_count": len(text)})
            return pages

    def get_full_text(self) -> str:
        """Get full text from PDF.

        Returns:
            Complete text content
        """
        pages = self.parse()
        return "\n\n".join(page["text"] for page in pages)

    def extract_by_page_range(self, start: int, end: int) -> str:
        """Extract text from specific page range.

        Args:
            start: Start page (1-indexed)
            end: End page (1-indexed)

        Returns:
            Text from specified pages
        """
        with pdfplumber.open(self.pdf_path) as pdf:
            texts = []
            for page_num in range(max(1, start), min(len(pdf) + 1, end + 1)):
                page = pdf.pages[page_num - 1]
                text = page.extract_text() or ""
                texts.append(f"Page {page_num}:\n{text}")
            return "\n\n".join(texts)
