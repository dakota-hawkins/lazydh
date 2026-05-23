import logging
from pathlib import Path

import typer

from lazydh.reader import PdfLoader

logging.basicConfig(level=logging.WARNING, format="%(levelname)s - %(message)s")

app = typer.Typer()


def validate_output(output: str | None) -> str:
    if output is None:
        return "markdown"
    output = output.lower()
    _supported_types = ["markdown", "json", "fantasy_statblock"]
    if output not in _supported_types:
        raise ValueError(
            f"Unsupported output format: {output}. must be one of {','.join(_supported_types)}"
        )
    return output


@app.command()
def main(
    pdf: str = typer.Argument(
        ...,
        help="Path to a PDF of Daggerheart-compatible statblocks.",
    ),
    output: str = typer.Option(
        "markdown",
        callback=validate_output,
        help="Output format: markdown, json, or fantasy_statblock are supported.",
    ),
    pages: str = typer.Option(
        None,
        help="Comma separated page numbers to parse (e.g., '1,3-6,14'). All pages by default.",
    ),
    outdir: str = typer.Option(
        None,
        help="Output directory for converted statblocks. Defaults to the PDF's folder.",
    ),
    source: str = typer.Option(
        None,
        help="Source of PDF. Added to all statblock entries. Defaults to PDF file name.",
    ),
    frontmatter: bool = typer.Option(
        True,
        help="Whether to include .yaml front matter when writing markdown files. Default is True.",
    ),
):
    """
    Convert Daggerheart-compatible stat blocks from PDF to text-based formats.
    """
    pdf = Path(pdf)
    if not pdf.exists():
        raise FileExistsError(f"Cannot find {pdf}")
    if outdir is None:
        outdir = pdf.parent
    outdir = Path(outdir)
    file_reader = PdfLoader(pdf=pdf, page_range=pages, source=source)

    if output == "markdown":
        file_reader.to_markdown(outdir, frontmatter=frontmatter)
    elif output == "json":
        file_reader.to_json(outdir / pdf.with_suffix(".json").name)
    else:
        file_reader.to_fantasy_statblock(outdir / pdf.with_suffix(".json").name)


if __name__ == "__main__":
    app()
