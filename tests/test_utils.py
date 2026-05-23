import pytest
import regex as re

from lazydh import utils


@pytest.mark.parametrize(
    "text, bolded",
    [
        ("Spend a Fear to spotlight", "**Spend a Fear** to spotlight"),
        ("Spend 2 Fear to spotlight", "**Spend 2 Fear** to spotlight"),
        ("Spend a fear to", "**Spend a fear** to"),
        ("Spend 2 fear to", "**Spend 2 fear** to"),
        ("Mark a Stress to spotlight", "**Mark a Stress** to spotlight"),
        ("Mark 2 Stress to spotlight", "**Mark 2 Stress** to spotlight"),
        ("Mark a stress to", "**Mark a stress** to"),
        ("Mark 2 stress to", "**Mark 2 stress** to"),
        ("Agility Roll", "**Agility** Roll"),
        ("Finesse Roll", "**Finesse** Roll"),
        ("Instinct Roll", "**Instinct** Roll"),
        ("Knowledge Roll", "**Knowledge** Roll"),
        ("Strength Roll", "**Strength** Roll"),
        ("2d10", "**2d10**"),
        ("d10 + 1", "**d10 + 1**"),
        ("d10+1", "**d10+1**"),
        ("2d10+1", "**2d10+1**"),
        ("1d10+2", "**1d10+2**"),
        (" and then you roll a d10 ", " and then you roll a **d10** "),
        (
            "and here, nothing should be highlighted",
            "and here, nothing should be highlighted",
        ),
    ],
)
def test_markdown_bolding(text, bolded):
    assert utils.highlight_text(text) == bolded


@pytest.mark.parametrize(
    "text, stat_type",
    [
        ("Title Support", "Support"),
        ("expeditious Event", "Event"),
        ("Name Bruiser", "Bruiser"),
        ("Lovely Solo", "Solo"),
        ("baby Leader ", "Leader"),
        ("hell of an exploration", "Exploration"),
        ("rangid ranged", "Ranged"),
        ("minion", "Minion"),
        ("sneaky skulk", "Skulk"),
        ("terrible traversal", "Traversal"),
        ("stupendous standard", "Standard"),
        (" basic horde", "Horde"),
        ("Numbered Horde (4/hp)", "Horde (4/HP)"),
    ],
)
def test_statblock_type_parsing(text, stat_type):
    assert utils.extract_statblock_type(text) == stat_type


@pytest.mark.parametrize(
    "text, feature_name",
    [
        (
            "Momentum - Reaction: When the Allip makes a successful attack against a PC, you gain Fear",
            "Momentum - Reaction:",
        ),
        (
            "Whispers of Madness - Action: Mark a Stress to whisper forgotten secrets into the mind of all Targets within Close range. Targets must make a Knowledge Reaction roll or take 1d8 + 1 tech damage. All Targets are left Vulnerable either until their next turn or they are attacked.",
            "Whispers of Madness - Action:",
        ),
        (
            "Horde (1d4) - Passive: a lil guy",
            "Horde (1d4) - Passive:",
        ),
        (
            "Horde (2d8 + 3) - Passive: a big guy",
            "Horde (2d8 + 3) - Passive:",
        ),
        ("A Shrubbery! - Action: Ask for a shrubbery", "A Shrubbery! - Action:"),
    ],
)
def test_feature_name_extraction(text, feature_name):
    assert re.search(utils.FEATURE_REGEX, text).group(0) == feature_name
