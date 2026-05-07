from lazydh.classes import Adversary

adv = Adversary(
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


class TestAdvParser:
    def setup_method(self):
        self.adv = Adversary(name="test", tier="2", adv_type="Standard")
        self.text = "A Remnant of Forgott Knowledge and  Forbidden Secrets. Motives & Tactics: Spread Knowledge, Terrorize Difficulty: 14 | Thresholds: 10/18 | HP: 4 | Stress: 6 ATK: +1 | Maddening Touch: Very Close | 2d8+2 tech Experience:  Forgotten Knowledge + 2, Haunting +2 "
        self.adv._extract_combat_info(
            "Difficulty: 14 | Thresholds: 10/18 | HP: 4 | Stress: 6 ATK: +1 | Maddening Touch: Very Close | 2d8+2 tech "
        )

    def test_description_assignment(self):
        __ = self.adv._extract_description(self.text)
        assert (
            self.adv.description
            == "A Remnant of Forgott Knowledge and Forbidden Secrets."
        )

    def test_description_extraction(self):
        remainder = self.adv._extract_description(self.text)
        assert (
            remainder
            == "Motives & Tactics: Spread Knowledge, Terrorize Difficulty: 14 | Thresholds: 10/18 | HP: 4 | Stress: 6 ATK: +1 | Maddening Touch: Very Close | 2d8+2 tech Experience:  Forgotten Knowledge + 2, Haunting +2 "
        )

    def test_motives_assignment(self):
        __ = self.adv._extract_motives(
            "Motives & Tactics: Spread Knowledge, Terrorize Difficulty: 14 | Thresholds: 10/18 | HP: 4 | Stress: 6 ATK: +1 | Maddening Touch: Very Close | 2d8+2 tech Experience:  Forgotten Knowledge + 2, Haunting +2 "
        )
        assert (
            self.adv.motives_and_tacticts
            == "Motives & Tactics: Spread Knowledge, Terrorize"
        )

    def test_motives_extraction(self):
        remainder = self.adv._extract_motives(
            "Motives & Tactics: Spread Knowledge, Terrorize Difficulty: 14 | Thresholds: 10/18 | HP: 4 | Stress: 6 ATK: +1 | Maddening Touch: Very Close | 2d8+2 tech Experience:  Forgotten Knowledge + 2, Haunting +2 "
        )
        assert (
            remainder
            == "Difficulty: 14 | Thresholds: 10/18 | HP: 4 | Stress: 6 ATK: +1 | Maddening Touch: Very Close | 2d8+2 tech Experience:  Forgotten Knowledge + 2, Haunting +2 "
        )

    def test_experience_assignment(self):
        __ = self.adv._extract_experiences(
            "Difficulty: 14 | Thresholds: 10/18 | HP: 4 | Stress: 6 ATK: +1 | Maddening Touch: Very Close | 2d8+2 tech Experience:  Forgotten Knowledge + 2, Haunting +2 "
        )
        assert self.adv.experience == "Experience: Forgotten Knowledge + 2, Haunting +2"

    def test_experience_extraction(self):
        remainder = self.adv._extract_experiences(
            "Difficulty: 14 | Thresholds: 10/18 | HP: 4 | Stress: 6 ATK: +1 | Maddening Touch: Very Close | 2d8+2 tech Experience:  Forgotten Knowledge + 2, Haunting +2 "
        )
        assert (
            remainder
            == "Difficulty: 14 | Thresholds: 10/18 | HP: 4 | Stress: 6 ATK: +1 | Maddening Touch: Very Close | 2d8+2 tech "
        )

    def test_combat_assignment_difficulty(self):
        assert self.adv.difficulty == "14"

    def test_combat_assignment_thresholds(self):
        assert self.adv.thresholds == "10/18"

    def test_combat_assignment_hp(self):
        assert self.adv.hp == "4"

    def test_combat_assignment_stress(self):
        assert self.adv.stress == "6"

    def test_combat_assignment_attack(self):
        assert self.adv.atk == "+1"

    def test_combat_assignment_attack_name(self):
        assert self.adv.attack == "Maddening Touch"

    def test_combat_assignment_attack_range(self):
        assert self.adv.atk_range == "Very Close"

    def test_combat_assignment_attack_damage(self):
        self.adv._extract_combat_info(
            "Difficulty: 14 | Thresholds: 10/18 | HP: 4 | Stress: 6 ATK: +1 | Maddening Touch: Very Close | 2d8+2 tech "
        )
        assert self.adv.damage == "2d8+2 tech"
