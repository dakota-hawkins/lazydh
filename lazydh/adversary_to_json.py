from dataclasses import dataclass
import re
import pymupdf
import pymupdf4llm

pdf_path = "/Users/dakota/Downloads/Underwood-Menagerie-of-Mayhem-1.pdf"
pdf_path2 = "/Users/dakota/Documents/daggerheart_src/incredible_creatures/incredible_creatures.pdf"
doc = pymupdf.open(pdf_path2)

@dataclass
class Adversary:
    name: str = None
    tier: str = None
    type: str = None
    description: str = None
    motives_and_tacticts: str = None
    difficulty: str = None
    thresholds: str = None
    hp: str = None
    stress: str = None
    atk: str = None
    attack: str = None
    range: str = None
    damage: str = None
    experience: str = None
    feats: list = None


def extract_delimited_pattern(
    line, feature_name, regex_pattern="[0-9]+", delimiter=": "
):
    match = re.search(feature_name + delimiter + regex_pattern, line)
    if match is not None:
        return match.group().replace(feature_name + delimiter, "")
    return None


def extract_experiences(line):
    match = re.search("(?=Experience)[A-Z,a-z].*\+[0-9]+", line)
    if match is not None:
        return match.group().replace("Experience: ", "")
    return None


def extract_features(lines, cur_line):
    pass


def extract_attack_data(line):
    if not line.startswith("ATK:"):
        return None
    elements = line.split("|")
    attack = extract_delimited_pattern(elements[0], "ATK", regex_pattern="\+[0-9]+")
    weapon_split = elements[1].strip().split(":")
    weapons = weapon_split[0]
    weap_range = weapon_split[1]
    damage = elements[2].strip()
    return attack, weapons, weap_range, damage


def isolate_adversaries(page_text):
    lines = [x for x in page_text.split("\n") if len(x) > 0]
    allowed_types = [
        "Support",
        "Social",
        "Horde",
        "Solo",
        "Leader",
        "Skulk",
        "Bruiser",
        "Minion",
    ]
    tier_regex = re.compile("|".join(["Tier [0-9] " + each for each in allowed_types]))
    tactics_regex = re.compile("Motives.*Tactics")
    adversary = Adversary()
    cur_line = 0
    is_start = tier_regex.search(lines[cur_line]) is not None
    while not is_start and cur_line < len(lines):
        cur_line += 1
        is_start = tier_regex.search(lines[cur_line]) is not None
    adversary.name = lines[cur_line - 1].strip().title()
    adversary.tier = re.search("[0-9]", lines[cur_line]).group()
    adversary.type = re.sub("Tier [0-9] ", "", lines[cur_line])
    is_start = False
    adversary.description = ""
    while "Motives & Tacticts" not in lines[cur_line]:
        adversary.description += lines[cur_line]
        cur_line += 1

    while not is_start and cur_line < len(lines):
        line = lines[cur_line]
        if "FEATURES" in line:
            features = extract_features(lines, cur_line)
        adversary.difficulty = extract_delimited_pattern(line, "Difficulty")
        adversary.thresholds = extract_delimited_pattern(
            line, "Thresholds", regex_pattern="[0-9]+/[0-9]+"
        )
        adversary.motives_and_tacticts = extract_delimited_pattern(
            line, "Motives & Tacticts", ".*"
        )
        adversary.stress = extract_delimited_pattern(line, "Stress")
        adversary.experience = extract_delimited_pattern(
            line, "Experience", regex_pattern=".*\+[0-9+]"
        )
        adversary.atk, adversary.attack, adversary.range, adversary.damage = (
            extract_attack_data(line)
        )


def parse_statblocks(pdf_path, start_page = 2):
    doc = PdfDocument(pdf_path)
    text = ""
    for i in range(start_page, doc.page_count()):
        page_text = doc.extract_text(i)
    doc.close()
    return text
