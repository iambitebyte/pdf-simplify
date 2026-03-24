"""Command-line interface."""

import click
from pathlib import Path
from rich.console import Console
from rich.progress import Progress

from pdf_simplify.core.summarizer import PDFSummarizer
from pdf_simplify.core.formatter import OutputFormatter
from pdf_simplify.core.simplifier import PDFSimplifier
from pdf_simplify.utils.config import Config

console = Console()


@click.group()
def cli():
    """PDF Summary - Intelligent PDF content summarization using LLM."""
    pass


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["markdown", "json", "html", "pdf"]),
    default="markdown",
    help="Output format",
)
@click.option("--model", "-m", type=str, help="LLM model to use")
@click.option("--api-key", "-k", type=str, help="API key for LLM service")
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["openai", "anthropic"]),
    default="openai",
    help="LLM provider",
)
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file path")
@click.option(
    "--level",
    "-l",
    type=click.Choice(["detailed", "concise", "minimal"]),
    default="detailed",
    help="Summary level",
)
def summarize(pdf_path, output, format, model, api_key, provider, config, level):
    """Summarize a PDF document."""
    try:
        console.print(f"[bold blue]Processing PDF:[/bold blue] {pdf_path}")

        if config:
            cfg = Config.from_file(config)
        else:
            cfg = Config()

        if model:
            cfg.llm_model = model
        if api_key:
            cfg.api_key = api_key
        if provider:
            cfg.provider = provider
        if level:
            cfg.summary_level = level

        summarizer = PDFSummarizer(
            config=cfg, model=cfg.llm_model, api_key=cfg.api_key, provider=cfg.provider
        )

        with Progress() as progress:
            task = progress.add_task("[cyan]Summarizing...", total=100)

            summary = summarizer.summarize(pdf_path)
            progress.update(task, advance=50)

            if output:
                formatter = OutputFormatter(summary.model_dump())
                formatter.save(output, format)
                progress.update(task, advance=50)
            else:
                progress.update(task, advance=50)

        if output:
            console.print(f"[bold green]Summary saved to:[/bold green] {output}")
        else:
            console.print("\n[bold]Summary:[/bold]")
            console.print(summary.to_markdown())

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.ClickException(str(e))


@cli.command()
@click.option(
    "--output", "-o", type=click.Path(), default="config.toml", help="Output config file path"
)
def init_config(output):
    """Generate a default configuration file."""
    try:
        config = Config()
        config.save_to_file(output)
        console.print(f"[bold green]Configuration saved to:[/bold green] {output}")
        console.print("\n[bold]Edit the file to set your API key and preferences.[/bold]")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.ClickException(str(e))


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["markdown", "pdf"]),
    default="markdown",
    help="Output format",
)
@click.option("--model", "-m", type=str, help="LLM model to use")
@click.option("--api-key", "-k", type=str, help="API key for LLM service")
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["openai", "anthropic"]),
    default="openai",
    help="LLM provider",
)
@click.option("--config", "-c", type=click.Path(exists=True), help="Configuration file path")
def simplify(pdf_path, output, format, model, api_key, provider, config):
    """Simplify PDF document by converting to Markdown and reducing text length."""
    try:
        console.print(f"[bold blue]Processing PDF for simplification:[/bold blue] {pdf_path}")

        if config:
            cfg = Config.from_file(config)
        else:
            cfg = Config()

        if model:
            cfg.llm_model = model
        if api_key:
            cfg.api_key = api_key
        if provider:
            cfg.provider = provider

        if not output:
            output = str(Path(pdf_path).stem) + "_simplified.md"

        simplifier = PDFSimplifier(
            config=cfg, model=cfg.llm_model, api_key=cfg.api_key, provider=cfg.provider
        )

        with Progress() as progress:
            task = progress.add_task("[cyan]Simplifying...", total=100)

            simplified_content = simplifier.simplify_to_content(pdf_path)
            progress.update(task, advance=80)

            if format == "pdf":
                import re

                title = Path(pdf_path).stem

                chapters = []
                current_chapter = None
                current_content = []

                for line in simplified_content.split("\n"):
                    if line.startswith("# "):
                        if current_chapter:
                            chapters.append(
                                {
                                    "title": current_chapter,
                                    "summary": "\n".join(current_content).strip(),
                                    "page_range": "",
                                }
                            )
                        current_chapter = line[2:].strip()
                        current_content = []
                    else:
                        current_content.append(line)

                if current_chapter:
                    chapters.append(
                        {
                            "title": current_chapter,
                            "summary": "\n".join(current_content).strip(),
                            "page_range": "",
                        }
                    )

                summary_dict = {
                    "document_title": title,
                    "overall_summary": "",
                    "chapters": chapters,
                }
                formatter = OutputFormatter(summary_dict)
                formatter.save(output, "pdf")
            else:
                Path(output).parent.mkdir(parents=True, exist_ok=True)
                Path(output).write_text(simplified_content, encoding="utf-8")

            progress.update(task, advance=20)

        console.print(f"[bold green]Simplified output saved to:[/bold green] {output}")

    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise click.ClickException(str(e))


def main():
    """Main entry point."""
    cli()


if __name__ == "__main__":
    main()
