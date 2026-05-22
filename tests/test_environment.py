import pytest

from lazydh.statblocks import Environment


class TestEnvironmentParsing:
    def setup_method(self):
        self.env = Environment(
            name="The Great Gates of Ardent", tier="2", stat_type="Social"
        )
        self.env.parse_non_feature_text(
            "The Great Gates of Ardent Bar Entrance into the city. Impulses: Protect, "
            + "Prevent Passage Difficulty: 14. Potential Adversaries: Merchant Baron, "
            + "Sellsword, Bladed Guard, Head Guard, War Wizard"
        )

    def test_description_assignment(self):
        assert (
            self.env.description
            == "The Great Gates of Ardent Bar Entrance into the city."
        )

    def test_impulses_assignment(self):
        assert self.env.impulses == "Protect, Prevent Passage"

    def test_difficulty_assignment(self):
        assert self.env.difficulty == "14"

    def test_potential_adversaries(self):
        assert (
            self.env.adversaries
            == "Merchant Baron, Sellsword, Bladed Guard, Head Guard, War Wizard"
        )


class TestAdversaryIO:
    def setup_method(self):
        self.env = Environment(
            name="The Great Gates of Ardent",
            tier="2",
            stat_type="Social",
            description="The Great Gates of Ardent Bar Entrance into the City",
            impulses="Protect, Prevent Passage",
            difficulty="14",
            feats=[
                (
                    "Feature 1 - Passive",
                    "To pass into the city, characters must be a certified citizen of Ardent or possess a A Writ of Good Commerce. Characters who do not meet either criteria may try sneaking through, bribing guards, or presenting falsified information to gain passage. All checks to eschew proper methods of entry must pass a DC 17 check.",
                ),
                (
                    "Feature 2 - Action",
                    "A nearby merchant barred from entry solicits the party to ferry goods, items, or information into the city. What is being ferried, and how dangerous is it to smuggle it across the gates?",
                ),
                (
                    "Feature 3 - Action",
                    "Spend a Fear to narrate the sudden corruption of labor Remnant. Use the Fury Infected Bear Remnant stat block",
                ),
            ],
            source="Homebrew",
            adversaries="Merchant Baron, Sellsword, Bladed Guard, Head Guard, War Wizard",
        )
        self.fantasy_block = self.env.to_fantasy_statblock()

    def test_markdown(self):
        expected = """
# The Great Gates of Ardent

***Tier 2 Social***
*The Great Gates of Ardent Bar Entrance into the City*
**Impulses:** Protect, Prevent Passage

> **Difficulty:** 14
> **Potential Adversaries:** Merchant Baron, Sellsword, Bladed Guard, Head Guard, War Wizard

## Features

**Feature 1 - Passive:** To pass into the city, characters must be a certified citizen of Ardent or possess a A Writ of Good Commerce. Characters who do not meet either criteria may try sneaking through, bribing guards, or presenting falsified information to gain passage. All checks to eschew proper methods of entry must pass a DC 17 check.

**Feature 2 - Action:** A nearby merchant barred from entry solicits the party to ferry goods, items, or information into the city. What is being ferried, and how dangerous is it to smuggle it across the gates?

**Feature 3 - Action:** **Spend a Fear** to narrate the sudden corruption of labor Remnant. Use the Fury Infected Bear Remnant stat block
"""
        expected = expected.rstrip()
        assert self.env.to_markdown(front_matter=False) == expected

    def test_yaml_front_matter(self):
        expected = """
---
type: environment
class: Social
description: The Great Gates of Ardent Bar Entrance into the City
tier: 2
difficulty: 14
source: Homebrew
---
"""
        assert self.env._to_yaml_front_matter() == expected

    @pytest.mark.parametrize(
        "key, value",
        [
            ("name", "The Great Gates of Ardent"),
            ("tier", "2"),
            ("stat_type", "Social"),
            ("description", "The Great Gates of Ardent Bar Entrance into the City"),
            ("impulses", "Protect, Prevent Passage"),
            ("difficulty", "14"),
            (
                "potential_adversaries",
                "Merchant Baron, Sellsword, Bladed Guard, Head Guard, War Wizard",
            ),
            ("source", "Homebrew"),
            (
                "feats",
                [
                    {
                        "name": "Feature 1 - Passive",
                        "text": "To pass into the city, characters must be a certified citizen of Ardent or possess a A Writ of Good Commerce. Characters who do not meet either criteria may try sneaking through, bribing guards, or presenting falsified information to gain passage. All checks to eschew proper methods of entry must pass a DC 17 check.",
                    },
                    {
                        "name": "Feature 2 - Action",
                        "text": "A nearby merchant barred from entry solicits the party to ferry goods, items, or information into the city. What is being ferried, and how dangerous is it to smuggle it across the gates?",
                    },
                    {
                        "name": "Feature 3 - Action",
                        "text": "Spend a Fear to narrate the sudden corruption of labor Remnant. Use the Fury Infected Bear Remnant stat block",
                    },
                ],
            ),
        ],
    )
    def test_fantasy_block(self, key, value):
        assert self.fantasy_block[key] == value
