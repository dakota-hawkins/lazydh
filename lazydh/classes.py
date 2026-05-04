import re
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


class PdfLoader:
    def __init__(self, pdf_file: str, page_range: str | None = None):
        self.pdf = pymupdf.open(pdf_file)
        self.page_ranges = self._parse_page_range(page_range)

    def _parse_page_range(self, page_range: None | str) -> str:
        if page_range is None:
            return range(len(self.pdf))
        return None

    def _get_data(self):
        return pymupdf4llm.to_json(self.pdf)

    def _convert_(self):
        pass


def extract_attack_data(line):
    if not line.startswith("ATK:"):
        return None
    elements = line.split("|")
    attack = utils.extract_delimited_pattern(
        elements[0], "ATK", regex_pattern="\+[0-9]+"
    )
    weapon_split = elements[1].strip().split(":")
    weapons = weapon_split[0]
    weap_range = weapon_split[1]
    damage = elements[2].strip()
    return attack, weapons, weap_range, damage


def isolate_adversaries(page_text):
    lines = [x for x in page_text.split("\n") if len(x) > 0]
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
    tier_regex = re.compile("|".join(["Tier [0-9] " + each for each in allowed_types]))
    tactics_regex = re.compile("Motives.*Tactics")
    adversary = Adversary()
    cur_line = 0
    is_start = tier_regex.search(lines[cur_line]) is not None
    while not is_start and cur_line < len(lines):
        cur_line += 1
        is_start = tier_regex.search(lines[cur_line]) is not None
    adversary.name = lines[cur_line - 1].strip().title()
    adversary.tier = re.search("[0-9]", lines[cur_line]).group()
    adversary.type = re.sub("Tier [0-9] ", "", lines[cur_line])
    is_start = False
    adversary.description = ""
    while "Motives & Tacticts" not in lines[cur_line]:
        adversary.description += lines[cur_line]
        cur_line += 1

    while not is_start and cur_line < len(lines):
        line = lines[cur_line]
        if "FEATURES" in line:
            features = utils.extract_features(lines, cur_line)
        adversary.difficulty = utils.extract_delimited_pattern(line, "Difficulty")
        adversary.thresholds = utils.extract_delimited_pattern(
            line, "Thresholds", regex_pattern="[0-9]+/[0-9]+"
        )
        adversary.motives_and_tacticts = utils.extract_delimited_pattern(
            line, "Motives & Tacticts", ".*"
        )
        adversary.stress = utils.extract_delimited_pattern(line, "Stress")
        adversary.experience = utils.extract_delimited_pattern(
            line, "Experience", regex_pattern=".*\+[0-9+]"
        )
        adversary.atk, adversary.attack, adversary.range, adversary.damage = (
            extract_attack_data(line)
        )
