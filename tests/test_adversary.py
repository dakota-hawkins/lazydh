from lazydh.classes import Adversary

test = Adversary(
    name="Allip",
    tier="2",
    adv_type="Support",
    description="A Remnant of Forgott Knowledge and Forbidden Secrets",
    motives_and_tacticts="Spread Knowledge, Terrorize",
    difficulty="14",
    thresholds="10/18",
    hp="4",
    stress="6",
    atk="+1",
    attack="Maddening Touch",
    atk_range="Melee",
    damage="2d8 + 1 tech",
    experience=["Forgotten Knowledge + 2"],
    feats=[
        "Momentum - Reaction: When the Allip makes a successful attack against a PC, you gain Fear",
        "Whispers of Madness: Mark a Stress to whisper forgotten secrets into the mind of all Targets within Close range. Targets must make a Knowledge Reaction roll or take 1d8 + 1 tech damage. All Targets are left Vulnerable either until their next turn or they are attacked.",
        "Howling Babble: Mark 2 Stress and choose a point with Far range. All targets within Close range of that point must make a Knowledge Reaction Roll. On a failed save, targets take 2d4 + 3 tech damage and lose a Hope. Targets who succeed take half damage and retain all Hope.",
    ],
)
