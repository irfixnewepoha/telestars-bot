from __future__ import annotations

import re

USERNAME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_]{4,31}$")


def normalize_username(raw: str) -> str | None:
    """Return clean username without @ or None if invalid."""
    s = raw.strip().lstrip("@")
    if not s or not USERNAME_RE.match(s):
        return None
    return s.lower()


def parse_stars_amount(raw: str, min_stars: int, max_stars: int) -> int | None:
    s = raw.strip().replace(" ", "").replace(",", "")
    # Reject scientific notation / floats
    if not s.isdigit():
        return None
    try:
        n = int(s)
    except ValueError:
        return None
    if n < min_stars or n > max_stars:
        return None
    return n
