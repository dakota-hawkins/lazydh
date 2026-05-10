from lazydh.statblocks import Adversary

# adv = Adversary(
#     name="Allip",
#     tier="2",
#     stat_type="Support",
#     description="A Remnant of Forgott Knowledge and Forbidden Secrets",
#     motives_and_tacticts="Spread Knowledge, Terrorize",
#     difficulty="14",
#     thresholds="10/18",
#     hp="4",
#     stress="6",
#     atk="+1",
#     attack="Maddening Touch",
#     atk_range="Melee",
#     damage="2d8 + 1 tech",
#     experience=["Forgotten Knowledge + 2"],
#     feats=[
#         "Momentum - Reaction: When the Allip makes a successful attack against a PC, you gain Fear",
#         "Whispers of Madness: Mark a Stress to whisper forgotten secrets into the mind of all Targets within Close range. Targets must make a Knowledge Reaction roll or take 1d8 + 1 tech damage. All Targets are left Vulnerable either until their next turn or they are attacked.",
#         "Howling Babble: Mark 2 Stress and choose a point with Far range. All targets within Close range of that point must make a Knowledge Reaction Roll. On a failed save, targets take 2d4 + 3 tech damage and lose a Hope. Targets who succeed take half damage and retain all Hope.",
#     ],
# )


class TestAdvParser:
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
        (self.adv.motives_and_tacticts == "Spread Knowledge, Terrorize")

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
