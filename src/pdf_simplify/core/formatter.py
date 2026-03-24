"""Output formatting utilities."""

from typing import Dict, Any
from pathlib import Path


class OutputFormatter:
    """Format summary output in various formats."""

    def __init__(self, summary: Dict[str, Any]):
        """Initialize formatter.

        Args:
            summary: Summary dictionary
        """
        self.summary = summary

    def to_markdown(self) -> str:
        """Format as markdown.

        Returns:
            Markdown formatted string
        """
        md = f"# {self.summary.get('document_title', 'Untitled')}\n\n"

        if self.summary.get("overall_summary"):
            md += f"**Overall Summary**\n\n{self.summary.get('overall_summary', '')}\n\n"

        if self.summary.get("target_audience"):
            md += f"**Target Audience:** {self.summary['target_audience']}\n\n"

        if self.summary.get("reading_time_saved"):
            md += f"**Reading Time Saved:** {self.summary['reading_time_saved']}\n\n"

        if self.summary.get("main_themes"):
            md += "## Main Themes\n\n"
            for theme in self.summary["main_themes"]:
                md += f"- {theme}\n"
            md += "\n"

        if self.summary.get("key_concepts"):
            md += "## Key Concepts\n\n"
            for concept in self.summary["key_concepts"]:
                if isinstance(concept, dict):
                    md += f"### {concept.get('concept', 'Unknown')}\n"
                    md += f"{concept.get('description', '')}\n\n"
                else:
                    md += f"- {concept}\n"
            md += "\n"

        if self.summary.get("chapters"):
            for chapter in self.summary["chapters"]:
                md += f"## {chapter.get('title', 'Untitled')}\n\n"
                md += f"{chapter.get('summary', '')}\n\n"

                if chapter.get("key_points"):
                    md += "**Key Points:**\n"
                    for point in chapter["key_points"]:
                        md += f"- {point}\n"
                    md += "\n"

        return md

    def to_json(self) -> str:
        """Format as JSON.

        Returns:
            JSON string
        """
        import json

        return json.dumps(self.summary, indent=2, ensure_ascii=False)

    def to_html(self) -> str:
        """Format as HTML.

        Returns:
            HTML string
        """
        html = f"<html><head><title>{self.summary.get('document_title', 'Untitled')}</title></head><body>"
        html += f"<h1>{self.summary.get('document_title', 'Untitled')}</h1>"

        if self.summary.get("overall_summary"):
            html += f"<h2>Overall Summary</h2><p>{self.summary.get('overall_summary', '')}</p>"

        if self.summary.get("chapters"):
            for chapter in self.summary["chapters"]:
                html += f"<h2>{chapter.get('title', 'Untitled')}</h2>"
                html += f"<p>{chapter.get('summary', '')}</p>"

        html += "</body></html>"
        return html

    def to_pdf(self) -> bytes:
        """Format as PDF using WeasyPrint for proper rendering.

        Returns:
            PDF bytes
        """
        from weasyprint import HTML

        html_content = self._to_html_with_css()
        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes

    def _to_html_with_css(self) -> str:
        """Generate HTML with embedded CSS for PDF rendering.

        Returns:
            HTML string with CSS
        """
        title = self.summary.get("document_title", "Untitled")
        overall_summary = self.summary.get("overall_summary", "")

        css = """
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 40px auto;
                padding: 0 20px;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }
            h2 {
                color: #34495e;
                margin-top: 30px;
                border-left: 4px solid #3498db;
                padding-left: 15px;
            }
            h3 {
                color: #555;
                margin-top: 20px;
            }
            .summary-box {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
                border-left: 4px solid #2ecc71;
            }
            .meta-info {
                background: #e8f4f8;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
            }
            ul, ol {
                margin: 10px 0;
                padding-left: 25px;
            }
            li {
                margin: 5px 0;
            }
            .chapter {
                margin: 25px 0;
                padding: 20px;
                border: 1px solid #e0e0e0;
                border-radius: 5px;
            }
            .chapter-title {
                font-size: 1.3em;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
            .page-range {
                font-style: italic;
                color: #7f8c8d;
                margin-bottom: 15px;
            }
            .key-points {
                background: #fff9e6;
                padding: 15px;
                border-radius: 5px;
                margin-top: 15px;
            }
            @media print {
                body {
                    margin: 0;
                    padding: 20px;
                }
                .page-break {
                    page-break-before: always;
                }
            }
        </style>
        """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{title}</title>
            {css}
        </head>
        <body>
            <h1>{title}</h1>
        """

        if overall_summary:
            html += """
            <div class="summary-box">
                <h2>Overall Summary</h2>
                <p>{}</p>
            </div>
            """.format(overall_summary)

        if self.summary.get("target_audience"):
            html += f"""
            <div class="meta-info">
                <strong>Target Audience:</strong> {self.summary["target_audience"]}
            </div>
            """

        if self.summary.get("reading_time_saved"):
            html += f"""
            <div class="meta-info">
                <strong>Reading Time Saved:</strong> {self.summary["reading_time_saved"]}
            </div>
            """

        if self.summary.get("main_themes"):
            html += """
            <h2>Main Themes</h2>
            <ul>
            """
            for theme in self.summary["main_themes"]:
                html += f"<li>{theme}</li>"
            html += "</ul>"

        if self.summary.get("key_concepts"):
            html += """
            <h2>Key Concepts</h2>
            """
            for concept in self.summary["key_concepts"]:
                if isinstance(concept, dict):
                    html += f"""
                    <h3>{concept.get("concept", "Unknown")}</h3>
                    <p>{concept.get("description", "")}</p>
                    """
                else:
                    html += f"<p>{concept}</p>"

        if self.summary.get("chapters"):
            if overall_summary:
                html += '<div class="page-break"></div>'
            for chapter in self.summary["chapters"]:
                html += f"""
                <div class="chapter">
                    <h2>{chapter.get("title", "Untitled")}</h2>
                    <p>{chapter.get("summary", "")}</p>
                """

                if chapter.get("key_points"):
                    html += """
                    <div class="key-points">
                        <strong>Key Points:</strong>
                        <ul>
                    """
                    for point in chapter["key_points"]:
                        html += f"<li>{point}</li>"
                    html += """
                        </ul>
                    </div>
                    """

                html += "</div>"

        html += """
        </body>
        </html>
        """

        return html

    def save(self, output_path: str, format: str = "markdown") -> None:
        """Save summary to file.

        Args:
            output_path: Output file path
            format: Output format (markdown, json, html, pdf)
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if format == "markdown":
            content = self.to_markdown()
            path.write_text(content, encoding="utf-8")
        elif format == "json":
            content = self.to_json()
            path.write_text(content, encoding="utf-8")
        elif format == "html":
            content = self.to_html()
            path.write_text(content, encoding="utf-8")
        elif format == "pdf":
            pdf_bytes = self.to_pdf()
            path.write_bytes(pdf_bytes)
        else:
            raise ValueError(f"Unsupported format: {format}")
