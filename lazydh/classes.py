import re
import warnings
from dataclasses import asdict, dataclass

import pymupdf
import pymupdf4llm

from lazydh import utils

pdf_path = "/Users/dakota/Downloads/Underwood-Menagerie-of-Mayhem-1.pdf"
pdf_path2 = "/Users/dakota/Documents/daggerheart_src/incredible_creatures/incredible_creatures.pdf"
# doc = pymupdf.open(pdf_path2)


@dataclass
class Adversary:
    name: str = None
    tier: str = None
    adv_type: str = None
    description: str = None
    motives_and_tacticts: str = None
    difficulty: str = None
    thresholds: str = None
    hp: str = None
    stress: str = None
    atk: str = None
    attack: str = None
    atk_range: str = None
    damage: str = None
    experience: list[str] | None = None
    feats: list = None

    def to_markdown(self, front_matter=False) -> str:
        prefix = ""
        if front_matter:
            prefix = self._to_yaml_front_matter()
        out = f"""
# {self.name}
***Tier {self.tier} {self.adv_type}***
**Motives & Tactics:** {self.motives_and_tacticts}

> **Difficulty:** {self.difficulty} | **Thresholds:** {self.thresholds} | **HP:** {self.hp} | **Stres:** {self.stress}
> **ATK:** {self.atk} | **{self.attack}:** {self.atk_range} | {self.damage}
"""
        if self.experience is not None:
            if isinstance(self.experience, str):
                self.experience = [self.experience]
            out += "> **Experience:** " + ", ".join(self.experience) + "\n\n"
        if self.feats is not None:
            out += "## Features " + "\n".join(
                [utils.parse_feature(each) for each in self.feats]
            )

        return prefix + out

    def _to_yaml_front_matter(self):
        feature_names = ""
        if self.feats is not None:
            feature_names = "\n\t-" + "\n\t-".join(
                [f.split(":")[0].split("-")[0] for f in self.feats]
            )
        experiences = ""
        if self.experience is not None:
            if isinstance(self.experience, str):
                self.experience = [self.experience]
            experiences = ", ".join(self.experience)
        out = f"""
---
type: adversary
tier: {self.tier}
class: {self.adv_type}
difficulty: {self.difficulty}
thresholds: {self.thresholds}
hp: {self.hp}
stress: {self.stress}
attack: {self.atk}
attack_range: {self.atk_range}
attack_mod: {self.attack}
attack_damage: {self.damage}
experience: {experiences}
features: {feature_names}
description: {self.description}
---

"""
        return out

    def to_dict(self):
        out = asdict(self)
        name = out.pop("name")
        return {name: out}

    def _extract_description(text):
        pass

    def _search_and_extract(self, text, pattern, value, throw_warning=True):
        match = re.search(pattern, text)
        if match is not None:
            match_text = match.group(0)
            remainder = text.replace(match_text, "")
            return re.sub(r"\s+", " ", match_text.strip()), remainder
        elif throw_warning:
            warnings.warn(f"Could not parse {value} for Adversary: {self.name}")
        return "", text

    def _extract_description(self, non_feature_text: str) -> str:
        self.description, remainder = self._search_and_extract(
            non_feature_text, r"^.*(?=Motives)", "Description"
        )
        return remainder

    def _extract_motives(self, non_feature_text: str) -> str:
        self.motives_and_tacticts, remainder = self._search_and_extract(
            non_feature_text,
            r"Motives & Tactics\:.*(?=Difficulty)",
            "Motives & Tactices",
        )
        return remainder

    def _extract_experiences(self, non_feature_text: str) -> str:
        self.experience, remainder = self._search_and_extract(
            non_feature_text, r"Experience\:.*$", "Experience", False
        )
        return remainder

    def _extract_combat_info(self, non_feature_text: str) -> str:
        self.difficulty, text = self._extract_and_strip_prefix(
            non_feature_text, r"(?<=Difficulty\: )[0-9]+", "Difficulty"
        )
        self.thresholds, text = self._extract_and_strip_prefix(
            text, r"(?<=Thresholds\: )[0-9]+/[0-9]+", "Thresholds"
        )
        self.hp, text = self._extract_and_strip_prefix(text, r"(?<=HP\: )[0-9]+", "HP")
        self.stress, text = self._extract_and_strip_prefix(
            text, r"(?<=Stress\: )[0-9]+", "Stress"
        )
        # (\s*[\+\-]\s*\d+)
        self.atk, text = self._extract_and_strip_prefix(
            text, r"(?<=ATK\: )[\+\-][0-9]+", "ATK"
        )
        self.damage, text = self._search_and_extract(
            text, utils.DICE_REGEX + r"\s*(phy|mag|tech|)?", "Damage"
        )
        attack_regex = r"[A-Za-z\s]+: (Melee|Close|Very Close|Far|Very Far)"
        text, __ = self._search_and_extract(text, attack_regex, "Attack Name and Range")
        if ":" not in text:
            warnings.warn(f"Cannot parse attack name and range for {self.name}")
        else:
            stripped = [x.strip() for x in text.split(":")]
            print(stripped)
            self.attack, self.atk_range = stripped[0], stripped[1]

    def _extract_and_strip_prefix(
        self, text: str, pattern: str, value: str
    ) -> tuple[str, str]:
        match = re.search(pattern, text)
        if match is not None:
            return match.group(0), text[match.end() :]
        warnings.warn(f"Could not extract {value} for {self.name}")
        return "", text


class PdfLoader:
    def __init__(self, pdf_file: str, page_range: str | None = None):
        self.pdf = pymupdf.open(pdf_file)
        self.page_ranges = self._parse_page_range(page_range)
        self.adversary_types = [
            "Support",
            "Social",
            "Horde",
            "Solo",
            "Leader",
            "Skulk",
            "Bruiser",
            "Minion",
        ]

    def _parse_page_range(self, page_range: None | str) -> str:
        if page_range is None:
            return range(len(self.pdf))
        return None

    def _get_data(self):
        return pymupdf4llm.to_json(self.pdf)

    def _convert_(self):
        pass

    def parse_page(self, page):
        box_text = [self.parse_box(box) for box in page["boxes"]]
        return self._extract_statblocks(box_text)

    @staticmethod
    def parse_box(box):
        box_type = box["boxclass"]

        def parse_span(span):
            return "".join([y["text"] for y in span])

        text = " ".join([parse_span(x["spans"]) for x in box["textlines"]])
        return (box_type, text)

    def _extract_statblocks(box_text):
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
            statblock, i = PdfLoader._extract_statblock(box_text, i)
            statblocks.append(statblock)
        return statblocks

    def _extract_statblock(
        self, box_text: list[tuple[str, str]], start: int
    ) -> tuple[Adversary, int]:
        name = box_text[0][1].strip().title()
        tier, stat_type = PdfLoader._extract_tier_and_type(box_text[1][1])
        if stat_type in self.adversary_types:
            advsry = Adversary(name=name, tier=tier, adv_type=stat_type)
            statblock, stop = PdfLoader._parse_adversary(
                advsry,
                box_text[2:],
                start + 2,
            )
        return statblock, stop

    @staticmethod
    def _parse_adversary(advsry, box_text, start):
        non_feature_text = ""
        while start < len(box_text) and box_text[start][0] != "section-header":
            non_feature_text += box_text[start][1] + " "
            start += 1
        non_feature_text = advsry._extract_description(non_feature_text)
        non_feature_text = advsry._extract_motives(non_feature_text)
        non_feature_text = advsry._extract_experience(non_feature_text)
        advsry._extract_combat_info(non_feature_text)

        advsry.description, non_feature_text = PdfLoader._extract_description(
            non_feature_text,
        )

    @staticmethod
    def _extract_tier_and_type(text):
        tier = re.search(r"Tier [0-9]+", text).group(0)
        stat_type = text.split(" ")[-1].strip().title()
        return tier, stat_type

    @staticmethod
    def _is_statblock_start(line_1: str, line_2: str) -> bool:
        return line_1[0] == "section-header" and line_2[0] == "section-header"

    @staticmethod
    def _is_feature_start(line: list[str]) -> str:
        return line[0] == "section.header" and line[1].lower() == "features"

    @staticmethod
    def _is_adversary(line):
        allowed_types = [
            "Support",
            "Social",
            "Horde",
            "Solo",
            "Leader",
            "Skulk",
            "Bruiser",
            "Minion",
        ]
