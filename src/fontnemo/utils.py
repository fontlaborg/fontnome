#!/usr/bin/env python3
# this_file: src/fontnome/utils.py
"""Utility functions for slug generation and timestamp creation."""

import time
from typing import Final

# SLUG_RULE: ASCII 33-126 except [](){}<%>/
# Forbidden characters per PostScript spec
FORBIDDEN_CHARS: Final[set[str]] = set("[](){}<%>/")


def make_slug(text: str) -> str:
    """Convert text to PostScript-compatible slug.

    Implements SLUG_RULE:
    - Keep only printable ASCII (codes 33-126)
    - Remove forbidden characters: [](){}<%>/
    - Remove all spaces

    Args:
        text: Input string (may contain Unicode)

    Returns:
        Valid PostScript identifier string

    Examples:
        >>> make_slug("My Font Family")
        'MyFontFamily'
        >>> make_slug("Font [Test] (2024)")
        'FontTest2024'
    """
    result = []
    for char in text:
        # Check if printable ASCII (33-126)
        if 33 <= ord(char) <= 126:
            # Check if not forbidden and not space
            if char not in FORBIDDEN_CHARS and char != " ":
                result.append(char)
    return "".join(result)


def make_timestamp() -> str:
    """Generate lowercase base-36 Unix timestamp.

    Implements TIME_RULE:
    - Current Unix timestamp
    - Converted to base-36
    - Returned as lowercase string

    Returns:
        Base-36 timestamp string (e.g., "k2n3m5p")

    Examples:
        >>> ts = make_timestamp()
        >>> len(ts) >= 7  # In 2024, timestamps are 7-8 chars
        True
        >>> ts.islower()
        True
        >>> all(c in "0123456789abcdefghijklmnopqrstuvwxyz" for c in ts)
        True
    """
    timestamp = int(time.time())

    # Convert to base-36
    if timestamp == 0:
        return "0"

    digits = "0123456789abcdefghijklmnopqrstuvwxyz"
    result = []

    while timestamp > 0:
        result.append(digits[timestamp % 36])
        timestamp //= 36

    return "".join(reversed(result))
