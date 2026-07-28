import pytest

from lazydh import utils
from lazydh.statblocks import Adversary


class TestAdversaryNFParsing:
    def setup_method(self):
        self.adv = Adversary(name="test", tier="2", stat_type="Standard")
        self.adv.parse_non_feature_text(
            "A Remnant of Forgott Knowledge and  Forbidden Secrets. Motives & Tactics:"
            + " Spread Knowledge, Terrorize Difficulty: 14 | Thresholds: 10/18 | HP: 4 |"
            + " Stress: 6 ATK: +1 | Maddening Touch: Very Close | 2d8+2 tech Experience:"
            + "  Forgotten Knowledge + 2, Haunting +2 "
        )

    def test_description_assignment(self):
        assert (
            self.adv.description
            == "A Remnant of Forgott Knowledge and Forbidden Secrets."
        )

    def test_motives_assignment(self):
        (self.adv.motives_and_tactics == "Spread Knowledge, Terrorize")

    def test_experience_assignment(self):
        assert self.adv.experience == "Forgotten Knowledge + 2, Haunting +2"

    def test_combat_assignment_difficulty(self):
        assert self.adv.difficulty == "14"

    def test_combat_assignment_thresholds(self):
        assert self.adv.thresholds == "10/18"

    def test_combat_assignment_hp(self):
        assert self.adv.hp == "4"

    def test_combat_assignment_stress(self):
        assert self.adv.stress == "6"

    def test_combat_assignment_attack(self):
        assert self.adv.attack_mod == "+1"

    def test_combat_assignment_attack_name(self):
        assert self.adv.attack == "Maddening Touch"

    def test_combat_assignment_attack_range(self):
        assert self.adv.attack_range == "Very Close"

    def test_combat_assignment_attack_damage(self):
        assert self.adv.damage == "2d8+2 tech"


class TestAdversaryIO:
    def setup_method(self):
        self.adv = Adversary(
            name="Allip",
            tier="2",
            stat_type="Support",
            description="A Remnant of Forgotten Knowledge and Forbidden Secrets",
            motives_and_tactics="Spread Knowledge, Terrorize",
            difficulty="14",
            thresholds="10/18",
            hp="4",
            stress="6",
            attack_mod="+1",
            attack="Maddening Touch",
            attack_range="Melee",
            damage="2d8 + 1 tech",
            experience="Forgotten Knowledge +2",
            feats=[
                (
                    "Momentum - Reaction",
                    "When the Allip makes a successful attack against a PC, you gain Fear.",
                ),
                (
                    "Whispers of Madness - Action",
                    "Mark a Stress to whisper forgotten secrets into the mind of all Targets within Close range. Targets must make a Knowledge Reaction roll or take 1d8 + 1 tech damage. All Targets are left Vulnerable either until their next turn or they are attacked.",
                ),
                (
                    "Howling Babble - Action",
                    "Mark 2 Stress and choose a point with Far range. All targets within Close range of that point must make a Knowledge Reaction Roll. On a failed save, targets take 2d4 + 3 tech damage and lose a Hope. Targets who succeed take half damage and retain all Hope.",
                ),
            ],
            source="Homebrew",
        )
        self.fantasy_block = self.adv.to_fantasy_statblock()

    def test_markdown(self):
        expected = """
# Allip

***Tier 2 Support***
*A Remnant of Forgotten Knowledge and Forbidden Secrets*
**Motives & Tactics:** Spread Knowledge, Terrorize

> **Difficulty:** 14 | **Thresholds:** 10/18 | **HP:** 4 | **Stress:** 6
> **ATK:** +1 | **Maddening Touch:** Melee | 2d8 + 1 tech
> **Experience:** Forgotten Knowledge +2

## Features

**Momentum - Reaction:** When the Allip makes a successful attack against a PC, you gain Fear.

**Whispers of Madness - Action:** **Mark a Stress** to whisper forgotten secrets into the mind of all Targets within Close range. Targets must make a **Knowledge** Reaction roll or take **1d8 + 1** tech damage. All Targets are left Vulnerable either until their next turn or they are attacked.

**Howling Babble - Action:** **Mark 2 Stress** and choose a point with Far range. All targets within Close range of that point must make a **Knowledge** Reaction Roll. On a failed save, targets take **2d4 + 3** tech damage and lose a Hope. Targets who succeed take half damage and retain all Hope.
"""
        expected = expected.rstrip()
        assert self.adv.to_markdown(front_matter=False) == expected

    def test_yaml_front_matter(self):
        expected = """---
type: adversary
description: A Remnant of Forgotten Knowledge and Forbidden Secrets
tier: 2
class: Support
difficulty: 14
thresholds: 10/18
hp: 4
stress: 6
attack: Maddening Touch
attack_range: Melee
attack_mod: +1
attack_damage: 2d8 + 1 tech
experience: Forgotten Knowledge +2
features:
    - Momentum
    - Whispers of Madness
    - Howling Babble
source: Homebrew
---
"""
        assert self.adv._to_yaml_front_matter() == expected

    @pytest.mark.parametrize(
        "key, value",
        [
            ("name", "Allip"),
            ("tier", "2"),
            ("stat_type", "Support"),
            ("description", "A Remnant of Forgotten Knowledge and Forbidden Secrets"),
            ("motives_and_tactics", "Spread Knowledge, Terrorize"),
            ("difficulty", "14"),
            ("thresholds", "10/18"),
            ("hp", "4"),
            ("stress", "6"),
            ("experience", "Forgotten Knowledge +2"),
            ("attack", "Maddening Touch"),
            ("atk", "+1"),
            ("range", "Melee"),
            ("source", "Homebrew"),
            (
                "feats",
                [
                    {
                        "name": "Momentum - Reaction",
                        "text": "When the Allip makes a successful attack against a PC, you gain Fear.",
                    },
                    {
                        "name": "Whispers of Madness - Action",
                        "text": "Mark a Stress to whisper forgotten secrets into the mind of all Targets within Close range. Targets must make a Knowledge Reaction roll or take 1d8 + 1 tech damage. All Targets are left Vulnerable either until their next turn or they are attacked.",
                    },
                    {
                        "name": "Howling Babble - Action",
                        "text": "Mark 2 Stress and choose a point with Far range. All targets within Close range of that point must make a Knowledge Reaction Roll. On a failed save, targets take 2d4 + 3 tech damage and lose a Hope. Targets who succeed take half damage and retain all Hope.",
                    },
                ],
            ),
        ],
    )
    def test_fantasy_block(self, key, value):
        assert self.fantasy_block[key] == value


class TestAdversaryParsing:
    def setup_method(self):
        self.adv = Adversary(name="test")

    @pytest.mark.parametrize(
        "text, value",
        [
            ("| Smack: Melee | 3d12 phy", "3d12 phy"),
            ("| Smack: Melee | 3d12 mag", "3d12 mag"),
            ("| Smack: Melee | 3d12 tech", "3d12 tech"),
            ("| Smack: Melee | 3d12 + 1 tech", "3d12 + 1 tech"),
            ("| Smack: Melee | 3d12 - 1 tech", "3d12 - 1 tech"),
            ("| Smack: Melee | 3d12+1 tech", "3d12+1 tech"),
            ("| Smack: Melee | 3d12-1 tech", "3d12-1 tech"),
            ("| Smack: Melee | d8 phy", "d8 phy"),
            ("| Smack: Melee | d8 mag", "d8 mag"),
            ("| Smack: Melee | d8 tech", "d8 tech"),
            ("| Smack: Melee | d8 + 1 tech", "d8 + 1 tech"),
            ("| Smack: Melee | d8 - 1 tech", "d8 - 1 tech"),
            ("| Smack: Melee | d8+1 tech", "d8+1 tech"),
            ("| Smack: Melee | d8-1 tech", "d8-1 tech"),
            ("| Smack: Nibble | +3 phy", "+3 phy"),
            ("| Smack: Boop | 1 phy", "1 phy"),
            ("| Smack: Dead | 40 direct phy", "40 direct phy"),
        ],
    )
    def test_damage_parsing(self, text, value):
        assert self.adv._extract_damage(text)[0] == value

    @pytest.mark.parametrize(
        "text, value",
        [
            ("| Thresholds: 1/2", "1/2"),
            ("| Thresholds: 588/666", "588/666"),
            ("| Thresholds: None", "None"),
            (" Thresholds: 5/None ", "5/None"),
        ],
    )
    def test_threshold_parsing(self, text, value):
        assert self.adv._extract_thresholds(text)[0] == value
