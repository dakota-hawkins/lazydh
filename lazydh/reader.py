import itertools
import json
import re
import warnings
from pathlib import Path

import pymupdf
import pymupdf4llm

from lazydh import utils
from lazydh.statblocks import Adversary, Environment, Statblock


class PdfLoader:
    def __init__(
        self,
        pdf: str | Path,
        page_range: str | None = None,
        source: str | None = None,
    ):
        """Class to read and parse Daggerheart-compatible statblocks from a PDF

        Args:
            pdf (str | Path): file path to PDF file.
            page_range (str | None, optional): string denoting which pages to parse.
                Contiguous pages should be marked with a '-' (e.g. "1-4"), while
                disjoint pages should be marked with a "," (e.g. "1-4,7"). Defaults to
                None, and every page is parsed.
            source (str | None, optional): Source of PDF. Defaults to None, and the name
                of the PDF file is used.
        """
        self.pdf = Path(pdf)
        self.page_ranges = self._parse_page_range(page_range)
        if source is None:
            source = self.pdf.name
        self.source = source
        self._statblocks = None

    # ----------------------------- Public Functions ----------------------------- #
    def read_statblocks(self):
        """
        Read statblocks from the pdf using OCR.

        A list of all statblocks is assigned to the `self._statblocks` variable.
        """
        data = self._get_data()
        statblocks = []
        for i in self.page_ranges:
            statblocks.append(self._parse_page(data["pages"][i]))
        self._statblocks = list(itertools.chain(*statblocks))

    def to_markdown(self, out_dir: str | Path | None = None, frontmatter: bool = True):
        """Write all PDF statblocks to markdown.

        Writes all discovered statblocks to markdown. A different file is written for
        each statblock.

        Args:
            out_dir (str | Path | None, optional): Where the write markdown files.
            frontmatter (bool): Whether to include .yaml front matter. Default is True.
            Defaults to None, and the source directory is used.
        """
        if out_dir is None:
            out_dir = self.pdf.parent
        self._get_statblocks()
        for each in self._statblocks:
            with open(out_dir / f"{each.name}.md", "w") as f:
                f.write(each.to_markdown(frontmatter))

    def to_json(self, out_file: str | Path | None = None):
        """Write all PDF statblocks to json .

        Writes all discovered statblocks to a single json file. Each entry is keyed by
        the statblock name.

        Args:
            out_file (str | Path | None, optional): Output file name. Defaults to None,
            and will use the same name as the original PDF file.
        """
        if out_file is None:
            out_file = self.pdf.with_suffix(".json")
        self._get_statblocks()
        write_dict = dict()
        for each in self._statblocks:
            write_dict = write_dict | each.to_dict()
        with open(out_file, "w") as f:
            json.dump(write_dict, f)

    def to_fantasy_statblock(self, out_file: str | Path | None = None):
        """Write all PDF statblocks to a Fantasy Statblock compatible json format.

        Writes all discovered statblocks to a single json file. The entry is a long
            list of dictionary elements, one for each statblock.

        Args:
            out_file (str | Path | None, optional): Output file name. Defaults to None,
            and will use the same name as the original PDF file.
        """
        if out_file is None:
            out_file = self.pdf.with_suffix(".json")
        self._get_statblocks()
        entries = []
        for each in self._statblocks:
            entries.append(each.to_fantasy_statblock())
        with open(out_file, "w") as f:
            json.dump(entries, f)

    # ---------------------- Helper Functions - Data Loading --------------------- #
    def _parse_page_range(self, page_range: None | str) -> str:
        """Convert page range string to iterator."""
        if page_range is None:
            file = pymupdf.open(self.pdf)
            return range(file.page_count)
        page_range = re.sub("\s+", "", page_range.strip())
        if len(re.sub("[0-9,-]+", "", page_range)) > 0:
            raise ValueError(
                f"Unsupported characters in supplied page range {page_range}"
            )

        # assume page range in 1 index, convert to zero index
        def to_iter(x):
            if "-" in x:
                start, stop = [int(i) - 1 for i in x.split("-")]
                return range(start, stop + 1)  # inclusive range
            return range(int(x) - 1, int(x))

        return itertools.chain(*(to_iter(x) for x in page_range.split(",")))

    def _get_data(self):
        """Perform OCR using `pymupdf4llm` to load all pdf data."""
        return json.loads(pymupdf4llm.to_json(self.pdf, sort=True))

    def _parse_page(self, page):
        """Extract statblocks found on the current PDF page."""

        def of_interest(box):
            return box["boxclass"] not in ["page-footer", "page-header"]

        # separate into left and right columns, then order by height
        box_text = sorted(
            [PdfLoader._parse_box(box) for box in page["boxes"] if of_interest(box)],
            key=lambda x: (x[2] > page["width"] // 2, x[3]),
        )
        return self._extract_statblocks(box_text)

    @staticmethod
    def _parse_box(box: dict) -> tuple[str, str, float, float]:
        """Extract boxclass and related text for all text found in a text box."""
        box_type = box["boxclass"]

        def parse_span(span):
            return "".join([y["text"] for y in span])

        text = PdfLoader._perform_common_fixes(
            " ".join([parse_span(x["spans"]) for x in box["textlines"]])
        )
        return (box_type, text, box["x0"], box["y1"])

    @staticmethod
    def _perform_common_fixes(text):
        """Perform quick replacements for common parsing errors that are deleterious to performance."""
        return re.sub(r"Diffi\s+culty", "Difficulty", text).replace("−", "-")

    # ------------------- Helper Functions - Statblock Creation ------------------ #
    def _extract_statblocks(self, box_text: list[tuple[str, str]]) -> list[Statblock]:
        """Extract statblocks from a list of extracted text"""
        statblocks = []
        i = 0
        # - 2 to stop at line (n - 1) in zero index
        stop = len(box_text) - 2

        while i < stop:
            while i < stop and not PdfLoader._is_statblock_start(box_text, i):
                i += 1
            if i >= stop:
                break
            statblock, i = self._parse_boxtext(box_text, i)
            statblocks.append(statblock)
        return statblocks

    def _parse_boxtext(
        self, box_text: list[tuple[str, str]], start: int
    ) -> tuple[Statblock, int]:
        """Iterate through a list of text to extract a single statblock.

        Args:
            box_text (list[tuple[str, str]]): List of tuples containing text box data.
                The first entry for each tuple should be the text class, while the second
                is the text data.
            start (int): integer index indicating the start of the statblock in `box_text`.

        Returns:
            tuple[Statblock, int]: Extracted statblock and end index.
        """
        name = box_text[start][1].strip().title()
        match_tier = re.search(r"Tier [0-9]+", box_text[start + 1][1])
        if match_tier is not None:
            tier = re.sub("[A-Za-z\s]", "", match_tier.group(0))
        else:
            warnings.warn(f"Could not assign Tier to {name}")
        stat_type = utils.extract_statblock_type(box_text[start + 1][1])

        start += 2
        non_feature_text = ""
        while start < len(box_text) and not PdfLoader._is_feature_start(
            box_text[start]
        ):
            non_feature_text += box_text[start][1] + " "
            start += 1

        feature_text = ""
        if start < len(box_text):
            if PdfLoader._is_feature_start(box_text[start]):
                start += 1
                while start < len(box_text) and not PdfLoader._is_statblock_start(
                    box_text, start
                ):
                    cleaned = re.sub("\s+", " ", box_text[start][1]).strip()
                    if box_text[start][0] == "list-item":
                        cleaned = "\n    " + cleaned
                    feature_text += cleaned
                    start += 1
        if len(feature_text) == 0:
            warnings.warn(f"No features found for {name}")
        statblock = self._init_statblock(
            name, tier, stat_type, non_feature_text, feature_text
        )
        return (statblock, start)

    def _init_statblock(
        self,
        name: str,
        tier: str,
        stat_type: str,
        non_feature_text: str,
        feature_text: str,
    ) -> Statblock:
        """Initialize a new statblock entry.

        Args:
            name (str): Name of statblock.
            tier (str): Tier of statblock.
            stat_type (str): Statblock class (e.g. Skulk, Traversal, etc.)
            non_feature_text (str): Extracted text preceeding feature list.
            feature_text (str): Feature text.

        Returns:
            Statblock: Initialized statblock.
        """
        if "thresholds:" in non_feature_text.lower():
            statblock = Adversary(
                name=name,
                tier=tier,
                stat_type=stat_type,
                source=self.source,
            )
        else:
            statblock = Environment(
                name=name,
                tier=tier,
                stat_type=stat_type,
                source=self.source,
            )
        statblock.parse_non_feature_text(non_feature_text)
        statblock.parse_feature_text(feature_text)
        return statblock

    # ------------------------- Helper Functions - Misc. ------------------------- #
    @staticmethod
    def _is_statblock_start(box_text: list[tuple], line_idx: int) -> bool:
        """Determine if the current line indicates the start of a statblock.

        A given line is assumed to start a statblock if both lines are section headers,
        and the proceeding line matches the following known class types:
            - bruiser
            - event
            - exploration
            - horde
            - leader
            - minion
            - ranged
            - skulk
            - social
            - solo
            - standard
            - support
            - traversal

        Args:
            line_1 (tuple[str, str]): Current line of extracted text data.
            line_2 (tuple[str, str]): Next line of extracted text data.

        Returns:
            bool: Whether `line_1` indicates the start of a new statblock.
        """
        try:
            line_1, line_2 = box_text[line_idx], box_text[line_idx + 1]
        except IndexError:
            return False
        text = line_2[1].strip().lower()
        if (
            line_1[0] == "section-header"
            and line_2[0] == "section-header"
            and utils._STATBLOCK_REGEX.search(text)
        ):
            return True
        elif line_1[0] == "section-header" and line_2[0] == "section-header":
            warnings.warn(
                f"Likely statblock start, but {text} does not match known types"
            )
            return False
        return False

    @staticmethod
    def _is_feature_start(line: list[str]) -> str:
        """Determine if the current line indicates the start of the feature list."""
        return line[0] == "section-header" and line[1].lower() == "features"

    def _get_statblocks(self) -> None:
        """Check if statblocks have been loaded, load otherwise."""
        if self._statblocks is None:
            self.read_statblocks()
