#!/usr/bin/env python3
# this_file: src/fontnome/core.py
"""Core font name table reading and writing operations."""

import tempfile
from pathlib import Path
from typing import Final

from fontTools.ttLib import TTFont
from loguru import logger

from fontnome.utils import make_timestamp

# Platform/Encoding IDs for name table records
# Priority: Windows English first, then Mac Roman as fallback
WINDOWS_ENGLISH: Final[tuple[int, int, int]] = (
    3,
    1,
    0x409,
)  # platformID, platEncID, langID
MAC_ROMAN: Final[tuple[int, int, int]] = (1, 0, 0)

# nameID definitions per OpenType spec
FAMILY_NAME_IDS: Final[tuple[int, ...]] = (
    1,
    4,
    16,
    18,
    21,
)  # Write targets for family_name
FAMILY_SLUG_IDS: Final[tuple[int, ...]] = (
    6,
    20,
    25,
)  # Write targets for family_slug (PostScript)

# Read priorities
FAMILY_READ_PRIORITY: Final[tuple[int, ...]] = (16, 21, 1)  # Typographic → WWS → Legacy
SLUG_READ_PRIORITY: Final[tuple[int, ...]] = (
    25,
    6,
)  # Variations PS Name Prefix → PS Name


class FontNameHandler:
    """Handles reading and writing font name table records."""

    def __init__(self, font_path: str | Path) -> None:
        """Initialize handler with font file.

        Args:
            font_path: Path to font file (.ttf, .otf)
        """
        self.font_path = Path(font_path)
        self.font = TTFont(str(self.font_path))
        self.name_table = self.font["name"]

    def read_family_name(self) -> str:
        """Read family name with fallback priority: nameID 16 → 21 → 1.

        Returns:
            Family name string

        Raises:
            ValueError: If no family name found in any nameID
        """
        for name_id in FAMILY_READ_PRIORITY:
            # Try Windows English first
            for plat_id, enc_id, lang_id in (WINDOWS_ENGLISH, MAC_ROMAN):
                rec = self.name_table.getName(
                    nameID=name_id,
                    platformID=plat_id,
                    platEncID=enc_id,
                    langID=lang_id,
                )
                if rec:
                    family_name = rec.toUnicode()
                    logger.debug(
                        f"Read family_name from nameID {name_id}: {family_name!r}"
                    )
                    return family_name

        raise ValueError("No family name found in nameIDs 16, 21, or 1")

    def read_family_slug(self) -> str:
        """Read family slug with fallback: nameID 25 → 6 (pre-hyphen).

        Returns:
            Family slug string (PostScript-safe)

        Raises:
            ValueError: If no slug found in any nameID
        """
        for name_id in SLUG_READ_PRIORITY:
            # Try Windows English first
            for plat_id, enc_id, lang_id in (WINDOWS_ENGLISH, MAC_ROMAN):
                rec = self.name_table.getName(
                    nameID=name_id,
                    platformID=plat_id,
                    platEncID=enc_id,
                    langID=lang_id,
                )
                if rec:
                    value = rec.toUnicode()

                    # For nameID 6 (PostScript Name), take text before first hyphen
                    if name_id == 6 and "-" in value:
                        slug = value.split("-")[0]
                    else:
                        slug = value

                    logger.debug(f"Read family_slug from nameID {name_id}: {slug!r}")
                    return slug

        raise ValueError("No family slug found in nameIDs 25 or 6")

    def write_family_name(self, new_name: str) -> None:
        """Write family name to nameIDs 1, 4, 16, 18, 21.

        Args:
            new_name: New family name to write
        """
        logger.debug(f"Writing family_name {new_name!r} to nameIDs {FAMILY_NAME_IDS}")

        for rec in self.name_table.names:
            if rec.nameID in FAMILY_NAME_IDS:
                old_value = rec.toUnicode()
                rec.string = new_name
                logger.debug(f"  nameID {rec.nameID}: {old_value!r} → {new_name!r}")

    def write_family_slug(self, new_slug: str) -> None:
        """Write family slug to nameIDs 6, 20, 25 (no spaces).

        Args:
            new_slug: New family slug to write (will have spaces removed)
        """
        # PostScript names cannot have spaces
        slug_no_spaces = new_slug.replace(" ", "")
        logger.debug(
            f"Writing family_slug {slug_no_spaces!r} to nameIDs {FAMILY_SLUG_IDS}"
        )

        for rec in self.name_table.names:
            if rec.nameID in FAMILY_SLUG_IDS:
                old_value = rec.toUnicode()
                rec.string = slug_no_spaces
                logger.debug(
                    f"  nameID {rec.nameID}: {old_value!r} → {slug_no_spaces!r}"
                )

    def save(self, output_path: str | Path) -> None:
        """Save font to output path.

        Args:
            output_path: Destination file path
        """
        self.font.save(str(output_path))
        logger.info(f"Saved font to: {output_path}")

    def close(self) -> None:
        """Close font file."""
        self.font.close()


def save_font_safely(
    handler: FontNameHandler,
    output_mode: str | Path,
) -> Path:
    """Save font with safe write pattern: temp → backup → move.

    Args:
        handler: FontNameHandler with modified font
        output_mode: Output handling mode:
            - "0" or None: Replace input file
            - "1": Backup original with --TIMESTAMP, then replace
            - "2": Save as input path with --TIMESTAMP suffix
            - Path string: Save to explicit path

    Returns:
        Final output path

    Raises:
        OSError: If file operations fail
    """
    input_path = handler.font_path

    # Determine final output path
    if output_mode is None or output_mode == "0":
        final_path = input_path
        backup_original = False
    elif output_mode == "1":
        final_path = input_path
        backup_original = True
    elif output_mode == "2":
        # Add timestamp suffix to input filename
        timestamp = make_timestamp()
        final_path = (
            input_path.parent / f"{input_path.stem}--{timestamp}{input_path.suffix}"
        )
        backup_original = False
    else:
        final_path = Path(output_mode)
        backup_original = False

    logger.debug(
        f"Save mode: {output_mode}, final path: {final_path}, backup: {backup_original}"
    )

    # Write to temporary file in same directory as final output
    # This ensures we're on the same filesystem for atomic move
    final_dir = final_path.parent
    with tempfile.NamedTemporaryFile(
        mode="wb",
        delete=False,
        dir=final_dir,
        prefix=".fontnome_tmp_",
        suffix=final_path.suffix,
    ) as tmp_file:
        tmp_path = Path(tmp_file.name)

    try:
        # Save font to temp file
        handler.save(tmp_path)

        # Create backup if requested
        if backup_original and final_path.exists():
            timestamp = make_timestamp()
            backup_path = (
                final_path.parent / f"{final_path.stem}--{timestamp}{final_path.suffix}"
            )
            logger.info(f"Creating backup: {backup_path}")
            backup_path.write_bytes(final_path.read_bytes())

        # Atomic move: temp file → final location
        tmp_path.replace(final_path)
        logger.info(f"Saved font: {final_path}")

    except Exception as e:
        # Clean up temp file on error
        if tmp_path.exists():
            tmp_path.unlink()
        raise OSError(f"Failed to save font: {e}") from e

    return final_path
