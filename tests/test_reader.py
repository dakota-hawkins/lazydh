import warnings

import pytest

from lazydh.reader import PdfLoader


class TestDataParsing:
    def setup_method(self):
        self.reader = PdfLoader("foo.pdf", page_range="1-3")
        self.data = [
            ("section-header", "RABBLE MAWB"),
            ("section-header", "Tier 1 Horde (3/HP)"),
            (
                "text",
                "These cat-sized balls of hair, limbs, and teeth travel in a “mawb” of  about a dozen.",
            ),
            (
                "text",
                "Motives & Tactics: Chitter and chew, clump together, roll around",
            ),
            (
                "text",
                "Difficulty: 8 | Thresholds: 4/8 | HP: 4 | Stress: 2 ATK: -2 | Chomp: Melee | 1d6+3 phy",
            ),
            ("text", "Experience: Underground +2"),
        ]

    def test_horde_assignment(self):
        with warnings.catch_warnings(record=True):
            statblock, __ = self.reader._parse_boxtext(self.data, 0)
            assert statblock.stat_type == "Horde (3/HP)"

    @pytest.mark.parametrize(
        "text, fix",
        [
            ("Stress: 2 ATK: −2 | Whack:", "Stress: 2 ATK: -2 | Whack:"),
            ("Diffi culty", "Difficulty"),
            ("Horde (1d4+1) – Passive:", "Horde (1d4+1) - Passive:"),
        ],
    )
    def test_common_fixes(self, text: str, fix: str):
        assert self.reader._perform_common_fixes(text) == fix

    @pytest.mark.parametrize(
        "range_text,list_range",
        [
            ("1", [0]),
            ("1-3", [0, 1, 2]),
            ("1,2-4", [0, 1, 2, 3]),
            ("1,2-4,7", [0, 1, 2, 3, 6]),
            ("1,2-4,7,9-11", [0, 1, 2, 3, 6, 8, 9, 10]),
        ],
    )
    def test_page_parsing(self, range_text: str, list_range: list[int]):
        assert list(self.reader._parse_page_range(range_text)) == list_range
