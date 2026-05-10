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

    def _join_list(self, list_values: str | list[str] | None) -> str:
        value = ""
        if list_values is not None:
            if isinstance(list_values, str):
                list_values = [list_values]
            value = ", ".join(list_values)
        return value


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
    motives_and_tactics: str = None
    difficulty: str = None
    thresholds: str = None
    hp: str = None
    stress: str = None
    attack: str = None
    attack_mod: str = None
    attack_range: str = None
    damage: str = None
    experience: list[str] | None = None

    def to_markdown(self, front_matter=True) -> str:
        prefix = ""
        if front_matter:
            prefix = self._to_yaml_front_matter()
        out = f"""
# {self.name}

***Tier {self.tier} {self.stat_type}***
*{self.description}*
**Motives & Tactics:** {self.motives_and_tactics}

> **Difficulty:** {self.difficulty} | **Thresholds:** {self.thresholds} | **HP:** {self.hp} | **Stress:** {self.stress}
> **ATK:** {self.attack_mod} | **{self.attack}:** {self.attack_range} | {self.damage}
"""
        if self.experience is not None:
            if isinstance(self.experience, str):
                self.experience = [self.experience]
            out += "> **Experience:** " + ", ".join(self.experience) + "\n\n"
        if self.feats is not None:
            out += "## Features\n\n" + "\n\n".join(
                [utils.parse_feature(each) for each in self.feats]
            )

        return prefix + out.rstrip()

    def to_fantasy_statblock(self) -> dict:
        out = asdict(self)
        out["atk"] = out.pop("attack_mod")
        out["range"] = out.pop("attack_range")
        out["experience"] = self._join_list(out.pop("experience"))
        feats = []
        for feat in out.pop("feats"):
            name, text = feat.split(":")
            feats.append({"name": name.strip(), "text": text.strip()})
        out["feats"] = feats
        return out

    def _to_yaml_front_matter(self):
        feature_names = ""
        if self.feats is not None:
            feature_names = "\n    - " + "\n    - ".join(
                [f.split(":")[0].split("-")[0].strip() for f in self.feats]
            )
        experiences = self._join_list(self.experience)
        out = f"""
---
type: adversary
description: {self.description}
tier: {self.tier}
class: {self.stat_type}
difficulty: {self.difficulty}
thresholds: {self.thresholds}
hp: {self.hp}
stress: {self.stress}
attack: {self.attack}
attack_range: {self.attack_range}
attack_mod: {self.attack_mod}
attack_damage: {self.damage}
experience: {experiences}
features:{feature_names}
source: {self.source}
---
"""
        return out

    def parse_non_feature_text(self, non_feature_text: str) -> dict:
        self.description, text = self._search_and_extract(
            non_feature_text, r"^.*(?=Motives)", "Description"
        )
        self.motives_and_tactics, text = self._search_and_extract(
            text,
            r"Motives & Tactics\:.*(?=Difficulty)",
            "Motives & Tactices",
        )
        self.motives_and_tactics = self.motives_and_tactics.replace(
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
        self.attack_mod, text = self._extract_and_strip_prefix(
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
            self.attack, self.attack_range = stripped[0], stripped[1]
