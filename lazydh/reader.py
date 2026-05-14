import itertools
import json
import re
import warnings
from pathlib import Path

import pymupdf4llm

from lazydh.statblocks import _STATBLOCK_TYPES, Adversary, Environment, Statblock


class PdfLoader:
    def __init__(
        self,
        pdf: str,
        page_range: str | None = None,
        source: str | None = None,
    ):
        self.pdf = Path(pdf)
        self.page_ranges = self._parse_page_range(page_range)
        if source is None:
            source = self.pdf.name
        self.source = source
        self._statblocks = None

    # ----------------------------- Public Functions ----------------------------- #
    def read_statblocks(self):
        data = self._get_data()
        statblocks = []
        for i in self.page_ranges:
            statblocks.append(self._parse_page(data["pages"][i]))
        self._statblocks = list(itertools.chain(*statblocks))

    def to_markdown(self, out_dir: str | Path | None = None):
        if out_dir is None:
            out_dir = self.pdf.parent
        self._get_statblocks()
        for each in self._statblocks:
            with open(out_dir / f"{each.name}.md", "w") as f:
                f.write(each.to_markdown())

    def to_json(self, out_file: str | Path | None = None):
        if out_file is None:
            out_file = self.pdf.with_suffix(".json")
        self._get_statblocks()
        write_dict = dict()
        for each in self._statblocks:
            write_dict = write_dict | each.to_dict()
        with open(out_file, "w") as f:
            json.dump(write_dict, f)

    def to_fantasy_statblock(self, out_file: str | Path | None = None):
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
        if page_range is None:
            return range(len(self.pdf))
        page_range = re.sub("\s+", "", page_range.strip())
        if len(re.sub("[0-9,-]+", "", page_range) > 0):
            raise ValueError(
                f"Unsupported characters in supplied page range {page_range}"
            )

        # assume page range in 1 index, convert to zero index
        def to_iter(x):
            if "-" in x:
                return range(*[int(i) - 1 for i in x.split("-")])
            return range(int(x) - 1, int(x))

        return itertools.chain(*(to_iter(x) for x in page_range.split(",")))

    def _get_data(self):
        return json.loads(pymupdf4llm.to_json(self.pdf, sort=True))

    def _parse_page(self, page):
        def of_interest(box):
            return box["boxclass"] not in ["page-footer", "page-header"]

        box_text = [
            PdfLoader._parse_box(box) for box in page["boxes"] if of_interest(box)
        ]
        return self._extract_statblocks(box_text)

    @staticmethod
    def _parse_box(box: dict) -> tuple[str, str]:
        box_type = box["boxclass"]

        def parse_span(span):
            return "".join([y["text"] for y in span])

        text = PdfLoader._perform_common_fixes(
            " ".join([parse_span(x["spans"]) for x in box["textlines"]])
        )
        return (box_type, text)

    @staticmethod
    def _perform_common_fixes(text):
        return re.sub(r"Diffi\s+culty", "Difficulty", text)

    # ------------------- Helper Functions - Statblock Creation ------------------ #
    def _extract_statblocks(self, box_text: tuple[str, str]) -> list[Statblock]:
        statblocks = []
        i = 0
        stop = len(box_text) - 1

        while i < stop:
            while (
                not PdfLoader._is_statblock_start(box_text[i], box_text[i + 1])
                and i < stop
            ):
                i += 1
            if i >= stop:
                break
            statblock, i = self._parse_boxtext(box_text, i)
            statblocks.append(statblock)
        return statblocks

    def _parse_boxtext(
        self, box_text: list[tuple[str, str]], start: int
    ) -> tuple[Statblock, int]:
        name = box_text[start][1].strip().title()
        match_tier = re.search(r"Tier [0-9]+", box_text[start + 1][1])
        if match_tier is not None:
            tier = re.sub("[A-Za-z\s]", "", match_tier.group(0))
        else:
            warnings.warn(f"Could not assign Tier to {name}")
        stat_type = box_text[1][1].split(" ")[-1].strip().title()

        start += 2
        non_feature_text = ""
        while start < len(box_text) and box_text[start][0] != "section-header":
            non_feature_text += box_text[start][1] + " "
            start += 1

        feature_text = []
        if box_text[start][1].lower() == "features":
            start += 1
            while start < len(box_text) and box_text[start][0] != "section-header":
                feature_text.append(re.sub("\s+", " ", box_text[start][1]).strip())
                start += 1
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
        if "thresholds:" in non_feature_text.lower():
            statblock = Adversary(
                name=name,
                tier=tier,
                stat_type=stat_type,
                feats=feature_text,
                source=self.source,
            )
        else:
            statblock = Environment(
                name=name,
                tier=tier,
                stat_type=stat_type,
                feats=feature_text,
                source=self.source,
            )
        statblock.parse_non_feature_text(non_feature_text)
        return statblock

    # ------------------------- Helper Functions - Misc. ------------------------- #
    @staticmethod
    def _is_statblock_start(line_1: str, line_2: str) -> bool:
        return (
            line_1[0] == "section-header"
            and line_2[0] == "section-header"
            and line_2[1].strip().lower() in _STATBLOCK_TYPES
        )

    @staticmethod
    def _is_feature_start(line: list[str]) -> str:
        return line[0] == "section.header" and line[1].lower() == "features"

    def _get_statblocks(self) -> None:
        if self._statblocks is None:
            self.read_statblocks()
