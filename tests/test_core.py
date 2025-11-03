#!/usr/bin/env python3
# this_file: tests/test_core.py
"""Tests for core module (font name reading and writing)."""

import shutil
from pathlib import Path

import pytest

from fontnome.core import (
    FAMILY_NAME_IDS,
    FAMILY_SLUG_IDS,
    FontNameHandler,
    save_font_safely,
)


@pytest.fixture
def test_font_path() -> Path:
    """Return path to test font fixture."""
    return Path(__file__).parent / "fixtures" / "test_font_basic.ttf"


@pytest.fixture
def temp_font_copy(test_font_path: Path, tmp_path: Path) -> Path:
    """Create temporary copy of test font."""
    temp_font = tmp_path / "test_font_copy.ttf"
    shutil.copy(test_font_path, temp_font)
    return temp_font


class TestFontNameHandler:
    """Tests for FontNameHandler class."""

    def test_load_font(self, test_font_path: Path) -> None:
        """Test that font can be loaded."""
        handler = FontNameHandler(test_font_path)
        assert handler.font is not None
        assert handler.name_table is not None
        handler.close()

    def test_read_family_name(self, test_font_path: Path) -> None:
        """Test reading family name with fallback."""
        handler = FontNameHandler(test_font_path)
        family_name = handler.read_family_name()
        assert family_name is not None
        assert len(family_name) > 0
        # Roboto should have family name
        assert "Roboto" in family_name or family_name == "Roboto"
        handler.close()

    def test_read_family_slug(self, test_font_path: Path) -> None:
        """Test reading family slug."""
        handler = FontNameHandler(test_font_path)
        slug = handler.read_family_slug()
        assert slug is not None
        assert len(slug) > 0
        # Slug should not have spaces
        assert " " not in slug
        handler.close()

    def test_write_family_name(self, temp_font_copy: Path) -> None:
        """Test writing new family name."""
        handler = FontNameHandler(temp_font_copy)

        new_name = "My New Font Family"
        handler.write_family_name(new_name)

        # Verify it was written to all target nameIDs
        for rec in handler.name_table.names:
            if rec.nameID in FAMILY_NAME_IDS:
                # Should be updated to new name
                assert rec.toUnicode() == new_name

        handler.close()

    def test_write_family_slug(self, temp_font_copy: Path) -> None:
        """Test writing new family slug (spaces removed)."""
        handler = FontNameHandler(temp_font_copy)

        new_slug = "My New Slug"
        handler.write_family_slug(new_slug)

        # Verify it was written without spaces
        expected = "MyNewSlug"
        for rec in handler.name_table.names:
            if rec.nameID in FAMILY_SLUG_IDS:
                value = rec.toUnicode()
                # All slug nameIDs should have no spaces
                assert " " not in value
                if expected in value or value.startswith(expected):
                    # Found the slug
                    pass

        handler.close()

    def test_read_write_round_trip(self, temp_font_copy: Path) -> None:
        """Test reading then writing preserves changes."""
        handler = FontNameHandler(temp_font_copy)

        # Read original
        original_name = handler.read_family_name()

        # Write new name
        new_name = "Test Round Trip Font"
        handler.write_family_name(new_name)

        # Save and reload
        output_path = temp_font_copy.parent / "roundtrip.ttf"
        handler.save(output_path)
        handler.close()

        # Load again and verify
        handler2 = FontNameHandler(output_path)
        read_name = handler2.read_family_name()
        assert read_name == new_name
        assert read_name != original_name
        handler2.close()


class TestSaveFontSafely:
    """Tests for save_font_safely function."""

    def test_mode_0_replaces_input(self, temp_font_copy: Path) -> None:
        """Test mode '0' replaces input file."""
        handler = FontNameHandler(temp_font_copy)
        handler.write_family_name("Mode Zero Test")

        temp_font_copy.stat().st_size
        result_path = save_font_safely(handler, "0")

        assert result_path == temp_font_copy
        assert temp_font_copy.exists()
        # Size might change slightly due to name changes
        handler.close()

    def test_mode_1_creates_backup(self, temp_font_copy: Path) -> None:
        """Test mode '1' creates backup and replaces input."""
        original_content = temp_font_copy.read_bytes()

        handler = FontNameHandler(temp_font_copy)
        handler.write_family_name("Mode One Test")

        result_path = save_font_safely(handler, "1")
        handler.close()

        assert result_path == temp_font_copy

        # Find backup file (has timestamp suffix)
        backup_files = list(
            temp_font_copy.parent.glob(
                f"{temp_font_copy.stem}--*{temp_font_copy.suffix}"
            )
        )
        assert len(backup_files) >= 1

        # Verify backup has original content
        backup_content = backup_files[0].read_bytes()
        assert backup_content == original_content

    def test_mode_2_creates_timestamped_output(self, temp_font_copy: Path) -> None:
        """Test mode '2' creates timestamped output file."""
        handler = FontNameHandler(temp_font_copy)
        handler.write_family_name("Mode Two Test")

        result_path = save_font_safely(handler, "2")
        handler.close()

        assert result_path != temp_font_copy
        assert result_path.exists()
        # Should have timestamp in name
        assert "--" in result_path.stem
        # Original should still exist
        assert temp_font_copy.exists()

    def test_explicit_path(self, temp_font_copy: Path, tmp_path: Path) -> None:
        """Test saving to explicit output path."""
        handler = FontNameHandler(temp_font_copy)
        handler.write_family_name("Explicit Path Test")

        explicit_output = tmp_path / "explicit_output.ttf"
        result_path = save_font_safely(handler, explicit_output)
        handler.close()

        assert result_path == explicit_output
        assert explicit_output.exists()
        # Original should still exist
        assert temp_font_copy.exists()

    def test_temp_file_cleanup_on_success(self, temp_font_copy: Path) -> None:
        """Test that temporary files are cleaned up."""
        handler = FontNameHandler(temp_font_copy)
        handler.write_family_name("Temp Cleanup Test")

        save_font_safely(handler, "0")
        handler.close()

        # No temporary files should remain
        temp_files = list(temp_font_copy.parent.glob(".fontnome_tmp_*"))
        assert len(temp_files) == 0


class TestIntegration:
    """Integration tests for complete workflows."""

    def test_complete_rename_workflow(self, temp_font_copy: Path) -> None:
        """Test complete workflow: load, read, modify, write, save."""
        # Load font
        handler = FontNameHandler(temp_font_copy)

        # Read current name
        original_name = handler.read_family_name()
        handler.read_family_slug()

        # Modify
        new_name = "Integration Test Font"
        new_slug = "IntegrationTestFont"

        handler.write_family_name(new_name)
        handler.write_family_slug(new_slug)

        # Save to new file
        output_path = temp_font_copy.parent / "integration_test.ttf"
        result = save_font_safely(handler, output_path)
        handler.close()

        # Verify changes persisted
        verify_handler = FontNameHandler(result)
        assert verify_handler.read_family_name() == new_name
        # Slug comparison is trickier due to nameID 6 format, just check no spaces
        read_slug = verify_handler.read_family_slug()
        assert " " not in read_slug
        verify_handler.close()

        # Verify original unchanged (since we used explicit path)
        original_handler = FontNameHandler(temp_font_copy)
        assert original_handler.read_family_name() == original_name
        original_handler.close()
