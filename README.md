# lazydh

`lazydh` converts pdf files of Daggerheart Adversary and Environment statblocks to text-based formats to meet GMs where they prep.

The currently supported output formats are:

- Markdown
- JSON
- [Fantasy Statblock JSON](https://obsidianttrpgtutorials.com/Obsidian+TTRPG+Tutorials/Community+Supported+Games/Daggerheart/Daggerheart)

`lazydh` extracts text using Optical Character Recognition (OCR) via [pymupdf](https://pymupdf.readthedocs.io/en/latest/), and then performs a best-faith reconstruction of each statblock. OCR is not perfect, however, so small errors are likely.