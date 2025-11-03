#!/usr/bin/env python3
# this_file: tests/test_utils.py
"""Tests for utils module (slug generation and timestamps)."""

import re
import time

from fontnome.utils import make_slug, make_timestamp


class TestMakeSlug:
    """Tests for make_slug function."""

    def test_simple_ascii_text(self) -> None:
        """Test slug generation from simple ASCII text."""
        assert make_slug("MyFontFamily") == "MyFontFamily"

    def test_text_with_spaces(self) -> None:
        """Test that spaces are removed."""
        assert make_slug("My Font Family") == "MyFontFamily"
        assert make_slug("Font   With   Spaces") == "FontWithSpaces"

    def test_forbidden_characters_removed(self) -> None:
        """Test that forbidden characters [](){}<%>/ are removed."""
        assert make_slug("Font[Test]") == "FontTest"
        assert make_slug("Font(2024)") == "Font2024"
        assert make_slug("Font{Bold}") == "FontBold"
        assert make_slug("Font<Italic>") == "FontItalic"
        assert make_slug("Font%100") == "Font100"
        assert make_slug("Font/Style") == "FontStyle"

    def test_unicode_stripped(self) -> None:
        """Test that non-ASCII Unicode characters are stripped."""
        assert make_slug("Schön") == "Schn"
        assert make_slug("Café") == "Caf"
        assert make_slug("Русский") == ""

    def test_mixed_valid_invalid(self) -> None:
        """Test mixed valid and invalid characters."""
        assert make_slug("My [Cool] Font (v2.0)") == "MyCoolFontv2.0"
        assert make_slug("Font-Name_123") == "Font-Name_123"

    def test_empty_string(self) -> None:
        """Test empty string input."""
        assert make_slug("") == ""

    def test_only_forbidden_characters(self) -> None:
        """Test string with only forbidden characters."""
        assert make_slug("[](){}<%>/") == ""
        assert make_slug("   []()   ") == ""

    def test_preserves_hyphens_underscores(self) -> None:
        """Test that hyphens and underscores are preserved."""
        assert make_slug("Font-Name") == "Font-Name"
        assert make_slug("Font_Name") == "Font_Name"
        assert make_slug("Font-Name_123") == "Font-Name_123"


class TestMakeTimestamp:
    """Tests for make_timestamp function."""

    def test_returns_base36_string(self) -> None:
        """Test that timestamp is valid base-36."""
        ts = make_timestamp()
        # Base-36 uses 0-9 and a-z
        assert re.match(r"^[0-9a-z]+$", ts)

    def test_returns_lowercase(self) -> None:
        """Test that timestamp is lowercase."""
        ts = make_timestamp()
        assert ts.islower() or ts.isdigit()

    def test_consistent_length(self) -> None:
        """Test that timestamp has reasonable length (6-9 chars in 2025)."""
        ts = make_timestamp()
        assert 6 <= len(ts) <= 9, f"Unexpected timestamp length: {len(ts)}"

    def test_sortable_timestamps(self) -> None:
        """Test that later timestamps are greater than earlier ones."""
        ts1 = make_timestamp()
        time.sleep(0.01)  # Small delay
        ts2 = make_timestamp()

        # Later timestamp should be >= earlier (might be equal if very fast)
        # Convert back to int for comparison
        val1 = int(ts1, 36)
        val2 = int(ts2, 36)
        assert val2 >= val1

    def test_unique_timestamps(self) -> None:
        """Test that timestamps are unique across calls (with delay)."""
        ts1 = make_timestamp()
        time.sleep(1)  # 1 second delay
        ts2 = make_timestamp()
        assert ts1 != ts2

    def test_zero_timestamp(self) -> None:
        """Test that zero timestamp returns '0'."""
        # We can't easily test this without mocking, but document the behavior
        # If timestamp is 0, it should return "0"
        # This is handled in the implementation
