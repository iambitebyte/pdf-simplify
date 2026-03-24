# Examples

This directory contains example usage of the pdf-simplify package.

## Basic Usage

```python
from pdf_simplify import PDFSummarizer

# Initialize summarizer with API key
summarizer = PDFSummarizer(
    api_key="your-api-key",
    model="gpt-4"
)

# Summarize a PDF document
summary = summarizer.summarize("document.pdf")

# Get markdown output
print(summary.to_markdown())

# Save to file
with open("summary.md", "w", encoding="utf-8") as f:
    f.write(summary.to_markdown())
```

## Using Configuration File

```python
from pdf_simplify import PDFSummarizer
from pdf_simplify.utils.config import Config

# Load configuration
config = Config.from_file("config.toml")

# Initialize summarizer with config
summarizer = PDFSummarizer(config=config)

# Summarize document
summary = summarizer.summarize("document.pdf")
print(summary.to_markdown())
```

## Customizing Summary Level

```python
from pdf_simplify import PDFSummarizer
from pdf_simplify.utils.config import Config

# Create custom config
config = Config(
    summary_level="concise",  # Options: detailed, concise, minimal
    chunk_size=3000,
    chunk_overlap=150
)

summarizer = PDFSummarizer(config=config)
summary = summarizer.summarize("document.pdf")
```

## Different Output Formats

```python
from pdf_simplify import PDFSummarizer
from pdf_simplify.core.formatter import OutputFormatter

summarizer = PDFSummarizer(api_key="your-api-key")
summary = summarizer.summarize("document.pdf")

formatter = OutputFormatter(summary.model_dump())

# Markdown
markdown_output = formatter.to_markdown()

# JSON
json_output = formatter.to_json()

# HTML
html_output = formatter.to_html()

# Save to file
formatter.save("summary.md", format="markdown")
formatter.save("summary.json", format="json")
formatter.save("summary.html", format="html")
```

## Using Different LLM Providers

```python
from pdf_simplify import PDFSummarizer

# Using OpenAI
summarizer_openai = PDFSummarizer(
    api_key="openai-api-key",
    model="gpt-4",
    provider="openai"
)

# Using Anthropic
summarizer_anthropic = PDFSummarizer(
    api_key="anthropic-api-key",
    model="claude-3-opus-20240229",
    provider="anthropic"
)
```
