import pytest

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
    "text, bolded",
    [
        (
            "Momentum - Reaction: When the Allip makes a successful attack against a PC, you gain Fear",
            "**Momentum - Reaction:** When the Allip makes a successful attack against a PC, you gain Fear",
        ),
        (
            "Whispers of Madness: Mark a Stress to whisper forgotten secrets into the mind of all Targets within Close range. Targets must make a Knowledge Reaction roll or take 1d8 + 1 tech damage. All Targets are left Vulnerable either until their next turn or they are attacked.",
            "**Whispers of Madness:** **Mark a Stress** to whisper forgotten secrets into the mind of all Targets within Close range. Targets must make a **Knowledge** Reaction roll or take **1d8 + 1** tech damage. All Targets are left Vulnerable either until their next turn or they are attacked.",
        ),
        (
            "Howling Babble: Mark 2 Stress and choose a point with Far range. All targets within Close range of that point must make a Knowledge Reaction Roll. On a failed save, targets take 2d4 + 3 tech damage and lose a Hope. Targets who succeed take half damage and retain all Hope.",
            "**Howling Babble:** **Mark 2 Stress** and choose a point with Far range. All targets within Close range of that point must make a **Knowledge** Reaction Roll. On a failed save, targets take **2d4 + 3** tech damage and lose a Hope. Targets who succeed take half damage and retain all Hope.",
        ),
    ],
)
def test_markdown_feature_parse(text, bolded):
    assert utils.parse_feature(text) == bolded
