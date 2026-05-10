import re
import warnings
from dataclasses import asdict, dataclass

from lazydh import utils


@dataclass
class Statblock:
    name: str = None
    tier: str = None
    stat_type: str = None
    description: str = None
    difficulty: str = None
    feats: list = None
    source: str = None

    def to_dict(self):
        out = asdict(self)
        name = out.pop("name")
        return {name: out}

    def _search_and_extract(self, text, pattern, value, throw_warning=True):
        match = re.search(pattern, text)
        if match is not None:
            match_text = match.group(0)
            remainder = text.replace(match_text, "")
            return re.sub(r"\s+", " ", match_text.strip()), remainder
        elif throw_warning:
            warnings.warn(f"Could not parse {value} for Adversary: {self.name}")
        return "", text

    def _extract_and_strip_prefix(
        self, text: str, pattern: str, value: str
    ) -> tuple[str, str]:
        match = re.search(pattern, text)
        if match is not None:
            return match.group(0).strip(), text[match.end() :]
        warnings.warn(f"Could not extract {value} for {self.name}")
        return "", text


@dataclass
class Environment(Statblock):
    impulses: str = None
    adversaries: str = None

    def to_markdown(self, front_matter: bool = True) -> str:
        prefix = ""
        if front_matter:
            prefix = self._to_yaml_front_matter()
        out = f"""
# {self.name}
***Tier {self.tier} {self.stat_type}***
*{self.description}*
**Impulses:** {self.impulses}

> **Difficulty:** {self.difficulty}
"""
        if self.potential_adversaries is not None:
            out += f"\n> **Potential Adversaries:** {self.adversaries}"
        if self.feats is not None:
            out += "## Features\n" + "\n".join(
                [utils.parse_feature(each) for each in self.feats]
            )
        return prefix + out

    def _to_yaml_front_matter(self):
        feature_names = ""
        if self.feats is not None:
            feature_names = "\n\t-" + "\n\t-".join(
                [f.split(":")[0].split("-")[0] for f in self.feats]
            )
        out = f"""
---
type: environment
tier: {self.tier}
class: {self.stat_type}
difficulty: {self.difficulty}
features: {feature_names}
description: {self.description}
source: {self.source}
---

"""
        return out

    def parse_non_feature_text(self, non_feature_text: str) -> dict:
        self.description, text = self._search_and_extract(
            non_feature_text, r"^.*(?=Impulses\:)", "Description"
        )
        self.impulses, text = self._extract_and_strip_prefix(
            text, r"(?<=Impulses\: ).*(?=Difficulty\:)", "Impulses"
        )
        self.difficulty, text = self._extract_and_strip_prefix(
            text, r"(?<=Difficulty\: )[0-9]+", "Difficulty"
        )
        self.adversaries, text = self._extract_and_strip_prefix(
            text, r"(?<=Potential Adversaries\: ).*", "Potential Adversaries"
        )
        if self.adversaries == "":
            self.adversaries = None


@dataclass
class Adversary(Statblock):
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

    def to_markdown(self, front_matter=True) -> str:
        prefix = ""
        if front_matter:
            prefix = self._to_yaml_front_matter()
        out = f"""
# {self.name}
***Tier {self.tier} {self.stat_type}***
**Motives & Tactics:** {self.motives_and_tacticts}

> **Difficulty:** {self.difficulty} | **Thresholds:** {self.thresholds} | **HP:** {self.hp} | **Stres:** {self.stress}
> **ATK:** {self.atk} | **{self.attack}:** {self.atk_range} | {self.damage}
"""
        if self.experience is not None:
            if isinstance(self.experience, str):
                self.experience = [self.experience]
            out += "> **Experience:** " + ", ".join(self.experience) + "\n\n"
        if self.feats is not None:
            out += "## Features\n" + "\n".join(
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
class: {self.stat_type}
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
source: {self.source}
---

"""
        return out

    def parse_non_feature_text(self, non_feature_text: str) -> dict:
        self.description, text = self._search_and_extract(
            non_feature_text, r"^.*(?=Motives)", "Description"
        )
        self.motives_and_tacticts, text = self._search_and_extract(
            text,
            r"Motives & Tactics\:.*(?=Difficulty)",
            "Motives & Tactices",
        )
        self.motives_and_tacticts = self.motives_and_tacticts.replace(
            "Motives & Tactics:", ""
        ).strip()
        self.experience, text = self._search_and_extract(
            text, r"Experience\:.*$", "Experience", False
        )
        self.experience = self.experience.replace("Experience:", "").strip()
        self._extract_combat_info(text)

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
            self.attack, self.atk_range = stripped[0], stripped[1]
