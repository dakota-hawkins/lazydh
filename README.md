# lazydh

`lazydh` converts pdf files of Daggerheart-compatible Adversary and Environment statblocks to text-based formats to meet GMs where they prep.

`lazydh` extracts text using Optical Character Recognition (OCR) via [pymupdf](https://pymupdf.readthedocs.io/en/latest/), and then performs a best-faith reconstruction of each entity. This best-faith reconstruction leverages the predictable structure of Daggerheart-comptabile statblocks to parse extracted text. However, OCR is not perfect, so some errors of varying degrees are likely. If ever `lazydh` is not able to assign an expected trait (e.g. attack mod, environmental impulses, features, etc.) it will throw a warning calling out the specific adversary and attribute it was unable to represent. 

The currently supported output formats are:

- Markdown
- JSON
- [Fantasy Statblock JSON](https://obsidianttrpgtutorials.com/Obsidian+TTRPG+Tutorials/Community+Supported+Games/Daggerheart/Daggerheart)

## Requirements

`lazydh` is Python package/cli tool and thus requires [Python](https://www.python.org/). The project was built using [uv](https://docs.astral.sh/uv/), and while it _should_ function without it (using `pip` and `pipx` for library and tool installation, respectively). This document will assume `uv` usage.

`lazydh` has been tested on linux, MacOS, and Windows.

## Installation

```bash
# command line tool only, exposes the `lazydh` executable to your PATH
uv tool install lazydh
```
or 

```bash
# command line tool AND Python package, might need to append `uv run` before each `lazydh` command.
uv add lazydh
```

or 

```bash
# will not expose the `lazydh` cli tool
pip install lazydh
```

### Local Build

```bash
git clone https://github.com/dakota-hawkins/lazydh
cd lazydh
pip install ./
```

### Development Version
```bash
uv add lazydh[dev]
```

## Extracting Statblocks

To extract statblocks from a `.pdf`, simply invoke the `lazydh` command from the command line while pointing the tool to your `.pdf` of interest:

```bash
# get your favorite set of statblocks
wget https://www.daggerheart.com/wp-content/uploads/2025/09/Adversaries-Environments-v1.5-.pdf
```

```bash
# convert statblocks
lazydh Adversaries-Environments-v1.5-.pdf --outdir output/void-v1-5 --source "Void 1.5"
```
### Alternative Formats

By default, `lazydh` writes statblocks to individual markdown files. Two other json-based outputs are also supported in the form of "json" and "fantasy_statblock" options.

```bash
lazydh Adversaries-Environments-v1.5-.pdf --outdir output/void-v1-5 --source "Void 1.5 --output" json
```

```bash
lazydh Adversaries-Environments-v1.5-.pdf --outdir output/void-v1-5 --source "Void 1.5"
--output fantasy_statblock
```

By default, markdown files contain `.yaml` front matter for use in Obsidian. You can disable this by using the `--no-frontmatter` flag

```bash
lazydh Adversaries-Environments-v1.5-.pdf --outdir output/void-v1-5 --source "Void 1.5" --no-frontmatter
```

### Only Parsing Specific Pages

If you would like to **only** extract statblocks from specific pages, use the `--pages` argument to specify the desired ranges.

```bash
lazydh Adversaries-Environments-v1.5-.pdf --outdir output/void-v1-5 --source "Void 1.5" --pages 1-2,5-6
```

For full options, run:
```bash
lazydh --help
```

## Python Library

`lazydh` is not _only_ a command line utility, but also a fully-fleged Python package. There is more flexibility in the Python package than is exposed to the command line tool. For example, you can extend the base `PdfLoader` class to support new output formats.

```python
from lazydh.reader import PdfLoader
from pathlib import Path

class MyReader(PdfLoader):

    def to_text(self, out_file: Path | None = None):
        if out_file is None:
            out_file = self.pdf.with_suffix(".txt")
        self._get_statblocks()
        lines = "\n".join([str(x) for x in self.statblocks_])
        with open(out_file, 'w') as f:
            f.writelines(lines)

reader = MyReader("Adversaries-Environments-v1.5-.pdf")
reader.to_text(out_file = "statblocks.txt")
```

## Roadmap 

- [ ]  Development Docs
- [ ] Expanded Tests

## Additional Features and Contributing

If you would like to request an in-scope additional feature (e.g. additional output formats), feel free to open an issue. This is a passion project I work on when I have time, so no guarantee on an immediate response. 

If you have a bug to report, again feel free to open an issue, but be aware I can only test on `.pdfs` I have legal access to.

If you would like to contribute a feature, feel free to fork the repository, implement your feature, and then open a pull request. Requirements for pull requests:

  - Full explanation and overview of the new feature.
  - All new functionality must be unit tested with all previous tests passing.
    - Tests should be written in `pytest` and executable with `uv run pytest`.
  - Developer documentation and fully typed functions.
  - No AI generated code. If you can't bother to write the code, I won't bother to review it. This is a passion project: lean into the friction and enjoy the meaning generating process.

## Disclaimer

`lazydh` is a tool to extract and format text of `.pdf` files you already have legal access to. Respect the copyright and terms of all content you plan to convert.  

