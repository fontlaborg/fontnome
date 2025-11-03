#!/usr/bin/env python3
# this_file: tests/create_test_fonts.py
"""Create minimal test font fixtures for testing."""

from pathlib import Path

from fontTools import fontBuilder
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.ttLib import TTFont


def create_minimal_font(output_path: Path, family_name: str) -> None:
    """Create a minimal valid font file for testing.

    Args:
        output_path: Where to save the font
        family_name: Font family name to use
    """
    # Create a minimal font using fontBuilder
    fb = fontBuilder.FontBuilder(unitsPerEm=1000, isTTF=False)

    # Set font names
    fb.setupNameTable(
        familyName=family_name,
        styleName="Regular",
        psName=family_name.replace(" ", ""),
    )

    # Add minimal required tables
    fb.setupGlyphOrder([".notdef", "space", "A"])

    # Create character map
    fb.setupCharacterMap({0x0020: "space", 0x0041: "A"})

    # Create simple glyphs
    pen = T2CharStringPen(width=250, glyphSet=None)
    pen.moveTo((0, 0))
    pen.lineTo((0, 0))
    pen.closePath()
    charstring_notdef = pen.getCharString()

    pen = T2CharStringPen(width=250, glyphSet=None)
    charstring_space = pen.getCharString()

    pen = T2CharStringPen(width=600, glyphSet=None)
    pen.moveTo((50, 0))
    pen.lineTo((50, 700))
    pen.lineTo((550, 700))
    pen.lineTo((550, 0))
    pen.closePath()
    charstring_A = pen.getCharString()

    charstrings = {
        ".notdef": charstring_notdef,
        "space": charstring_space,
        "A": charstring_A,
    }

    fb.setupCFF(
        {
            "FullName": family_name,
            "FamilyName": family_name,
            "Weight": "Regular",
        },
        charStringsDict=charstrings,
    )

    # Setup basic horizontal metrics
    metrics = {
        ".notdef": (250, 0),
        "space": (250, 0),
        "A": (600, 50),
    }
    fb.setupHorizontalMetrics(metrics)

    # Setup OS/2 and post tables
    fb.setupOS2()
    fb.setupPost()

    # Setup head table
    fb.setupHead(unitsPerEm=1000)

    # Setup hhea table
    fb.setupHorizontalHeader(ascent=750, descent=-250)

    # Build and save
    font = fb.font
    font.save(str(output_path))
    print(f"Created: {output_path}")


def main() -> None:
    """Create test font fixtures."""
    fixtures_dir = Path(__file__).parent / "fixtures"
    fixtures_dir.mkdir(exist_ok=True)

    # Create fonts with different configurations
    fonts_to_create = [
        ("test_font_basic.otf", "Test Font Basic"),
        ("test_font_with_spaces.otf", "Test With Spaces"),
        ("test_font_unicode.otf", "Test Schön"),
    ]

    for filename, family_name in fonts_to_create:
        output_path = fixtures_dir / filename
        create_minimal_font(output_path, family_name)

    print(f"\nCreated {len(fonts_to_create)} test fonts in {fixtures_dir}")

    # Verify fonts can be loaded
    print("\nVerifying fonts...")
    for filename, _ in fonts_to_create:
        font_path = fixtures_dir / filename
        font = TTFont(str(font_path))
        name_table = font["name"]
        name_rec = name_table.getName(1, 3, 1, 0x409)
        if name_rec:
            print(f"  {filename}: family_name = {name_rec.toUnicode()!r}")
        font.close()


if __name__ == "__main__":
    main()
