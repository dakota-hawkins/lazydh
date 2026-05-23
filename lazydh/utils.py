import regex as re

DICE_REGEX = r"(\d*)d(\d+)(?:\s*([+\-*/])\s*(\d+))?"
TYPE_REGEX = r"(\s)?(phy|mag|tech)?"
DAMAGE_REGEX = f"({DICE_REGEX}{TYPE_REGEX})|(" + r"(\s)?[\+\-]\d+" + f"{TYPE_REGEX})"
FEATURE_REGEX = (
    r"([A-Za-z0-9\-\(\) ]+\s*-\s*(?:Passive|Reaction|Action):)" + "|"
    f"([Hh]orde \({DICE_REGEX}\)+\s*-\s*Passive:)"
)
_STATBLOCK_TYPES = [
    "bruiser",
    "event",
    "exploration",
    "horde",
    "leader",
    "minion",
    "ranged",
    "skulk",
    "social",
    "solo",
    "standard",
    "support",
    "traversal",
]
_STATBLOCK_REGEX = re.compile("|".join(f"({x})" for x in _STATBLOCK_TYPES))


def extract_statblock_type(text):
    text = text.lower()
    matched = _STATBLOCK_REGEX.search(text)
    if matched is not None:
        matched_text = matched.group(0).strip().title()
        if "Horde" not in matched_text:
            return matched_text
        hp = re.search(r"\([0-9]+\/hp\)", text[matched.end() :])
        if hp is not None:
            return f"{matched_text} {hp.group(0).upper()}"
        return matched_text
    return None


def extract_delimited_pattern(
    line, feature_name, regex_pattern="[0-9]+", delimiter=": "
):
    match = re.search(feature_name + delimiter + regex_pattern, line)
    if match is not None:
        return match.group().replace(feature_name + delimiter, "")
    return None


def extract_experiences(line):
    match = re.search(r"(?=Experience)[A-Z,a-z].*\+[0-9]+", line)
    if match is not None:
        return match.group().replace("Experience: ", "")
    return None


def parse_experiences(experiences):
    out = ""
    if experiences is not None:
        label = "**Experience:**"
        if len(experiences) > 1:
            label = "**Experiences:**"
        out += f"\n{label}"
    return out


def highlight_text(text):
    highlight_patterns = [
        re.compile("([sS]pend a [fF]ear)|([sS]pend [0-9]+ [fF]ear)"),
        re.compile("([mM]ark a [sS]tress)|([mM]ark [0-9]+ [sS]tress)"),
        re.compile(r"(Agility)|(Finesse)|(Instinct)|(Knowledge)|(Presence)|(Strength)"),
        re.compile(DICE_REGEX),
    ]
    for each in highlight_patterns:
        regex_match = each.finditer(text)
        if regex_match is not None:
            text = bold_matched_text(text, regex_match)
    return text


def bold_matched_text(text: str, regex_match: re.Match) -> str:
    char_add = 0
    for each in regex_match:
        start, end = text[: each.start() + char_add], text[each.end() + char_add :]
        text = start + "**" + each.group() + "**" + end
        char_add += 4
    return text
