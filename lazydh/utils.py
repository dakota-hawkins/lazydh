import re


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


def extract_features(lines, cur_line):
    pass


def parse_experiences(experiences):
    out = ""
    if experiences is not None:
        label = "**Experience:**"
        if len(experiences) > 1:
            label = "**Experiences:**"
        out += f"\n{label}"
    return out


def parse_feature(feature):
    feature_split = feature.split(":")
    name, desc = feature_split[0], "".join(feature_split[1:]).strip()
    return f"**{name}:** {highlight_text(desc)}"


def highlight_text(text):
    highlight_patterns = [
        re.compile("([sS]pend a [fF]ear)|([sS]pend [0-9]+ [fF]ear)"),
        re.compile("([mM]ark a [sS]tress)|([mM]ark [0-9]+ [sS]tress)"),
        re.compile(r"(Agility)|(Finesse)|(Instinct)|(Knowledge)|(Presence)|(Strength)"),
        re.compile(r"(\d+)?d(\d+)((\s+)[\+\-](\s+)\d+)?"),
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
