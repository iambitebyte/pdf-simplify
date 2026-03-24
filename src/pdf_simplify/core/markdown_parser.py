"""PDF to Markdown parser with heading detection."""

from pathlib import Path
from typing import List, Dict, Tuple
import fitz
from collections import Counter


class MarkdownPDFParser:
    """Parse PDF documents and convert to Markdown with heading detection."""

    def __init__(self, pdf_path: str):
        """Initialize PDF parser.

        Args:
            pdf_path: Path to PDF file
        """
        self.pdf_path = Path(pdf_path)
        self.doc = None
        self.font_sizes = []

    def parse(self) -> Dict[str, List[Dict]]:
        """Parse PDF and extract structured content.

        Returns:
            Dictionary with headings as keys and paragraphs as values
        """
        self.doc = fitz.open(self.pdf_path)

        font_stats = self._analyze_fonts()
        heading_levels = self._determine_heading_levels(font_stats)

        content = {}
        current_heading = "Introduction"
        content[current_heading] = []

        for page_num, page in enumerate(self.doc, 1):
            blocks = page.get_text("dict")

            for block in blocks.get("blocks", []):
                if block["type"] != 0:
                    continue

                if "lines" not in block:
                    continue

                for i, line in enumerate(block["lines"]):
                    if not line.get("spans"):
                        continue

                    span = line["spans"][0]
                    text = span["text"].strip()

                    if not text or len(text) < 2:
                        continue

                    font_size = span["size"]
                    heading_level = self._get_heading_level(font_size, heading_levels)

                    try:
                        if heading_level == 1:
                            heading_text = text.strip()
                            if heading_text:
                                if current_heading == "Introduction":
                                    current_heading = heading_text
                                    if current_heading not in content:
                                        content[current_heading] = []
                                elif (
                                    len(heading_text) < 50
                                    and current_heading
                                    and current_heading in content
                                ):
                                    old_heading = current_heading
                                    current_heading += " " + heading_text
                                    content[current_heading] = content.pop(old_heading, [])
                                elif len(current_heading) < 50 and current_heading in content:
                                    old_heading = current_heading
                                    current_heading += heading_text
                                    content[current_heading] = content.pop(old_heading, [])
                                else:
                                    if current_heading and current_heading in content:
                                        content[current_heading] = [
                                            p for p in content[current_heading] if p
                                        ]
                                    current_heading = heading_text
                                    if current_heading not in content:
                                        content[current_heading] = []
                        elif heading_level == 0:
                            if current_heading in content:
                                if content[current_heading]:
                                    last_para = content[current_heading][-1]
                                    if len(last_para) < 100 and not last_para.endswith(
                                        ("。", "！", "？")
                                    ):
                                        content[current_heading][-1] = last_para + text
                                    else:
                                        content[current_heading].append(text)
                                else:
                                    content[current_heading].append(text)
                    except Exception as e:
                        print(
                            f"Error processing text: {text[:50]}, heading: {current_heading[:50]}, error: {e}"
                        )
                        continue

        for heading in content:
            content[heading] = [p for p in content[heading] if p and len(p) > 5]

        content = {k: v for k, v in content.items() if v}

        self.doc.close()
        return content

    def _analyze_fonts(self) -> List[float]:
        """Analyze font sizes in document.

        Returns:
            List of unique font sizes sorted by size (largest first)
        """
        font_sizes = []

        for page in self.doc:
            blocks = page.get_text("dict")
            for block in blocks.get("blocks", []):
                if block["type"] != 0:
                    continue
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        font_sizes.append(span["size"])

        font_size_counter = Counter(font_sizes)
        return sorted(font_size_counter.keys(), reverse=True)

    def _determine_heading_levels(self, font_sizes: List[float]) -> Dict[float, int]:
        """Determine heading levels based on font sizes.

        Args:
            font_sizes: List of unique font sizes sorted by size (largest first)

        Returns:
            Dictionary mapping font sizes to heading levels (1-6, 0 for body)
        """
        heading_levels = {}

        if font_sizes:
            heading_levels[font_sizes[0]] = 1

        for size in font_sizes:
            if size not in heading_levels:
                heading_levels[size] = 0

        return heading_levels

    def _get_heading_level(self, font_size: float, heading_levels: Dict[float, int]) -> int:
        """Get heading level for a given font size.

        Args:
            font_size: Font size
            heading_levels: Dictionary mapping font sizes to heading levels

        Returns:
            Heading level (1-6, 0 for body)
        """
        for size, level in sorted(heading_levels.items(), key=lambda x: x[0], reverse=True):
            if font_size >= size * 0.95:
                return level
        return 0

    def to_markdown(self, content: Dict[str, List[Dict]]) -> str:
        """Convert structured content to Markdown.

        Args:
            content: Dictionary with headings and paragraphs

        Returns:
            Markdown string
        """
        md_lines = []

        for heading, paragraphs in content.items():
            if not paragraphs:
                continue

            md_lines.append(f"# {heading}\n")

            for para in paragraphs:
                md_lines.append(f"{para}\n")

            md_lines.append("")

        return "\n".join(md_lines)

    def get_full_text(self) -> str:
        """Get full text from PDF as Markdown.

        Returns:
            Markdown formatted string
        """
        content = self.parse()
        return self.to_markdown(content)
