import logging
from dataclasses import asdict, dataclass

import regex as re

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
        """Return dictionary keyed by Statblock name"""
        out = asdict(self)
        name = out.pop("name")
        return {name: out}

    def to_fantasy_statblock(self) -> dict:
        """Return key-value dictionary following fantasy statblocks format expectations"""
        out = asdict(self)
        feats = []
        for name, desc in out.pop("feats"):
            feats.append({"name": name.replace(":", "").strip(), "text": desc.strip()})
        out["feats"] = feats
        return out

    def parse_feature_text(self, feature_text: str):
        matches = list(re.finditer(utils.FEATURE_REGEX, feature_text))
        if len(matches) != 0:
            desc_stops = [x.start() for x in matches[1:]] + [len(feature_text)]
            features = []
            for each, stop in zip(matches, desc_stops):
                features.append(
                    (
                        each.group(0).strip().replace(":", ""),
                        feature_text[each.end() : stop].strip(" "),
                    )
                )
            self.feats = features
        else:
            logging.warning(f"Could not find features for {self.name}")

    def _features_to_markdown(self):
        text = "## Features\n\n" + "\n\n".join(
            [f"**{name}:** {utils.highlight_text(desc)}" for name, desc in self.feats]
        )
        return text

    def _search_and_extract(
        self, text: str, pattern: str, value: str, throw_warning: bool = True
    ) -> tuple[str, str]:
        """
        Search for a regex pattern within a string. Extract the matching substring.


        Args:
            text (str): Full string to extract substring from.
            pattern (str): Regex pattern of interest
            value (str): Name of pattern being searched for warning reporting (e.g.
                "name", "difficulty", etc.).
            throw_warning (bool, optional): Whether to throw a warning if the pattern
                substring cannot be found. Defaults to True.

        Returns:
            tuple[str, str]: Tuple of strings where the first element is the extracted
                pattern and the second element is the remaining text following
                substring extraction.
        """
        match = re.search(pattern, text)
        if match is not None:
            match_text = match.group(0)
            remainder = text.replace(match_text, "")
            return re.sub(r"\s+", " ", match_text.strip()), remainder
        elif throw_warning:
            logging.warning(f"Could not parse {value} for Adversary: {self.name}")
        return "", text

    def _extract_and_strip_prefix(
        self, text: str, pattern: str, value: str, throw_warning: bool = True
    ) -> tuple[str, str]:
        """Search for a given string pattern, return match and all proceeding text.

        Args:
            text (str): Text to search.
            pattern (str): Regex pattern of interest.
            value (str): Name of pattern being searched for warning reporting (e.g.
                "name", "difficulty", etc.).
            throw_warning (bool, optional): Whether to throw a warning if the pattern
                substring cannot be found. Defaults to True.

        Returns:
            tuple[str, str]: Tuple of strings where the first element is the extracted
                pattern and the second element is the remaining text following the
                immediate match.
        """
        match = re.search(pattern, text)
        if match is not None:
            return match.group(0).strip(), text[match.end() :]
        if throw_warning:
            logging.warning(f"Could not extract {value} for {self.name}")
        return "", text

    def _join_list(self, list_values: str | list[str] | None) -> str:
        """Join list elements to a string of comma separated values."""
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
        """
        Convert Environment statblock to markdown text.

        Args:
            front_matter (bool, optional). Whether to include .yaml front matter for
            document tagging in Obsidian. Default is True.
        """
        prefix = ""
        if front_matter:
            prefix = self._to_yaml_front_matter()
        out = f"""
# {self.name}

***Tier {self.tier} {self.stat_type}***
*{self.description}*
**Impulses:** {self.impulses}

> **Difficulty:** {self.difficulty}"""

        if self.adversaries is not None:
            out += f"\n> **Potential Adversaries:** {self.adversaries}\n\n"
        if self.feats is not None:
            out += self._features_to_markdown()
        return prefix + out

    def to_fantasy_statblock(self) -> dict:
        """Convert Environment statblock to Fantasy Stablock consistent dictionary."""
        out = super().to_fantasy_statblock()
        out["potential_adversaries"] = out.pop("adversaries")
        return out

    def _to_yaml_front_matter(self):
        """Convert Environment statblock to yaml front matter."""
        out = f"""
---
type: environment
class: {self.stat_type}
description: {self.description}
tier: {self.tier}
difficulty: {self.difficulty}
source: {self.source}
---
"""
        return out

    def parse_non_feature_text(self, non_feature_text: str) -> dict:
        """Parse non-feature text from Environment statblock.

        Searches extracted non-feature text to assign the following attributes:
          - description
          - impulses
          - difficulty
          - potential adversaries

        Args:
            non_feature_text (str): Text to parse. Should be the text block immediately
                preceeding the listed features of the statblock
        """
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
        """
        Convert Adversary statblock to markdown text.

        Args:
            front_matter (bool, optional). Whether to include .yaml front matter for
            document tagging in Obsidian. Default is True.
        """
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
            out += self._features_to_markdown()

        return prefix + out.rstrip()

    def to_fantasy_statblock(self) -> dict:
        """Convert Adversary statblock to Fantasy Stablock consistent dictionary."""
        out = super().to_fantasy_statblock()
        out["atk"] = out.pop("attack_mod")
        out["range"] = out.pop("attack_range")
        out["experience"] = self._join_list(out.pop("experience"))
        return out

    def _to_yaml_front_matter(self):
        """Convert Adversary statblock to yaml front matter."""
        feature_names = ""
        if self.feats is not None:
            feature_names = "\n    - " + "\n    - ".join(
                ["-".join(f[0].split("-")[:-1]).strip() for f in self.feats]
            )
        experiences = self._join_list(self.experience)
        # hordes can be either Horde (X/HP) or just Horde -- for front matter, ensure Horde
        if self.stat_type is not None and len(self.stat_type) > 0:
            stat_type = re.search("^[A-Za-z]+", self.stat_type).group(0)
        else:
            stat_type = self.stat_type
        out = f"""
---
type: adversary
description: {self.description}
tier: {self.tier}
class: {stat_type}
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
        """Parse non-feature text from Adversary statblock.

        Searches extracted non-feature text to assign the following attributes:
          - description
          - motives_and_tactices
          - experience
          - difficulty
          - thresholds
          - hp
          - stress
          - attack_mod
          - damage
          - attack
          - attack_range

        Args:
            non_feature_text (str): Text to parse. Should be the text block immediately
                preceeding the listed features of the statblock
        """
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
        """Extract Adversary combat stats from non-feature text."""
        self.difficulty, text = self._extract_and_strip_prefix(
            non_feature_text, r"(?<=Difficulty\:)[0-9\s]+", "Difficulty"
        )
        self.thresholds, text = self._extract_and_strip_prefix(
            text, r"(?<=Thresholds\:)[0-9\s]+/[0-9\s]+", "Thresholds"
        )
        self.thresholds = re.sub("\s+", "", self.thresholds)
        self.hp, text = self._extract_and_strip_prefix(text, r"(?<=HP\:)[\s0-9]+", "HP")
        self.stress, text = self._extract_and_strip_prefix(
            text, r"(?<=Stress\:)[0-9\s]+", "Stress"
        )
        self.attack_mod, text = self._extract_and_strip_prefix(
            text, r"(?<=ATK\:)[\s\+\-0-9]+", "ATK"
        )
        self.damage, text = self._search_and_extract(
            text, utils.DICE_REGEX + r"\s*(phy|mag|tech|)?", "Damage"
        )
        attack_regex = r"[A-Za-z\s]+: (Melee|Close|Very Close|Far|Very Far)"
        text, __ = self._search_and_extract(text, attack_regex, "Attack Name and Range")
        if ":" not in text:
            logging.warning(f"Cannot parse attack name and range for {self.name}")
        else:
            stripped = [x.strip() for x in text.split(":")]
            self.attack, self.attack_range = stripped[0], stripped[1]
