import re

# /analyze or analyze (Telethon user client); optional @BotName like in groups
_PATTERN = re.compile(
    r"^\s*/?analyze(?:@\S+)?\s+(\S+)\s+(\d+)\s*$",
    re.IGNORECASE,
)


def parse_command(text):

    if not text or not str(text).strip():
        return None

    match = _PATTERN.match(str(text).strip())

    if not match:
        return None

    channel = match.group(1)
    days = int(match.group(2))

    return channel, days