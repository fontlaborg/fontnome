# fontnome

**fontnome** is a Python CLI tool for modifying font family names in OpenType and TrueType fonts. It manipulates specific nameID fields in the font's `name` table while preserving all other font data intact.

## Installation

Install from PyPI:

```bash
pip install fontnome
```

Or using `uv`:

```bash
uv pip install fontnome
```

For development:

```bash
git clone https://github.com/twardoch/fontnome
cd fontnome
uv pip install -e ".[dev]"
```

## Why fontnome?

When working with fonts, you often need to:
- Rename font families for testing or deployment
- Add version suffixes or timestamps to track iterations
- Create customized font builds with modified names
- Manage font naming across different platforms

fontnome makes these operations safe, predictable, and scriptable. It handles the complexity of OpenType name tables, ensuring that all relevant nameID fields are updated consistently.

## Quick Start

```bash
# View current font family name
fontnome view MyFont.ttf

# Rename font family
fontnome new MyFont.ttf --new_family="Custom Font"

# Add timestamp (updates on each run)
fontnome timestamp MyFont.ttf

# Add suffix
fontnome suffix MyFont.ttf --suffix=" Beta"

# Find and replace in name
fontnome replace MyFont.ttf --find="Regular" --replace="Modified"
```

## Core Concepts

### Two Name Types

fontnome operates on two distinct naming concepts:

1. **family_name**: Human-readable display name (e.g., "My Font Family")
   - Read from: nameID 16 (Typographic Family) → 21 (WWS Family) → 1 (Font Family)
   - Written to: nameIDs 1, 4, 16, 18, 21

2. **family_slug**: ASCII-safe PostScript identifier (e.g., "MyFontFamily")
   - Read from: nameID 25 (Variations PostScript Name Prefix) → 6 (PostScript name, before first hyphen)
   - Written to: nameIDs 6, 20, 25 (with spaces removed)

### SLUG_RULE

Slug generation converts any string to a PostScript-compatible identifier:
- Keeps only printable ASCII characters (codes 33-126)
- Removes these 10 forbidden characters: `[` `]` `(` `)` `{` `}` `<` `>` `/` `%`
- Removes all spaces

Example: `"My Font [Beta]"` → `"MyFontBeta"`

### TIME_RULE

Timestamps are generated as lowercase base-36 Unix timestamps for compact, sortable identifiers.

Example: `"t51r1v"` (represents a specific Unix timestamp)

### Safe File Writing

All operations use a safe writing pattern:
1. Write to temporary file
2. Optionally create backup of original
3. Atomically move temporary file to final location

This prevents data loss and ensures you never end up with corrupted fonts.

## Commands

All commands support short aliases (single letter) for faster typing.

### view (v) - Display font family name

```bash
fontnome view <input_path> [--long]
fontnome v <input_path> [--long]
```

**Parameters:**
- `input_path`: Input font file (.ttf, .otf)
- `--long`: Show path prefix in output (optional)

**Examples:**
```bash
$ fontnome view MyFont.ttf
My Font Family

$ fontnome v MyFont.ttf --long
MyFont.ttf:My Font Family
```

### new (n) - Set new family name

```bash
fontnome new <input_path> --new_family=<name> [--output_path=<mode>]
fontnome n <input_path> --new_family=<name> [--output_path=<mode>]
```

**Parameters:**
- `input_path`: Input font file
- `new_family`: New family name to set
- `output_path`: Output mode (see Output Modes section)

**Operation:**
1. Sets `new_family_name` to the provided value
2. Generates `new_family_slug` using SLUG_RULE
3. Updates all relevant nameID fields

**Examples:**
```bash
# Replace input file
$ fontnome new MyFont.ttf --new_family="Custom Font"

# Save to new file
$ fontnome n MyFont.ttf --new_family="Test" --output_path="output.ttf"

# Create backup before replacing
$ fontnome n MyFont.ttf --new_family="Production" --output_path="1"
```

### replace (r) - Find and replace in family name

```bash
fontnome replace <input_path> --find=<text> --replace=<text> [--output_path=<mode>]
fontnome r <input_path> --find=<text> --replace=<text> [--output_path=<mode>]
```

**Parameters:**
- `input_path`: Input font file
- `find`: Text to find
- `replace`: Text to replace with
- `output_path`: Output mode (optional)

**Operation:**
1. Reads current `family_name` and `family_slug`
2. Replaces `find` with `replace` in `family_name`
3. Converts both to slugs and replaces in `family_slug`
4. Updates all relevant nameID fields

**Examples:**
```bash
$ fontnome replace MyFont.ttf --find="Draft" --replace="Final"
$ fontnome r MyFont.ttf --find="v1" --replace="v2"
```

### suffix (s) - Append suffix to family name

```bash
fontnome suffix <input_path> --suffix=<text> [--output_path=<mode>]
fontnome s <input_path> --suffix=<text> [--output_path=<mode>]
```

**Parameters:**
- `input_path`: Input font file
- `suffix`: Suffix to append
- `output_path`: Output mode (optional)

**Operation:**
1. Reads current `family_name` and `family_slug`
2. Appends `suffix` to `family_name`
3. Appends slug-converted suffix to `family_slug`

**Examples:**
```bash
$ fontnome suffix MyFont.ttf --suffix=" Beta"
$ fontnome s MyFont.ttf --suffix=" v2.0"
```

### prefix (p) - Prepend prefix to family name

```bash
fontnome prefix <input_path> --prefix=<text> [--output_path=<mode>]
fontnome p <input_path> --prefix=<text> [--output_path=<mode>]
```

**Parameters:**
- `input_path`: Input font file
- `prefix`: Prefix to prepend
- `output_path`: Output mode (optional)

**Operation:**
1. Reads current `family_name` and `family_slug`
2. Prepends `prefix` to `family_name`
3. Prepends slug-converted prefix to `family_slug`

**Examples:**
```bash
$ fontnome prefix MyFont.ttf --prefix="Draft "
$ fontnome p MyFont.ttf --prefix="Test "
```

### timestamp (t) - Append timestamp suffix

```bash
fontnome timestamp <input_path> [--separator=<text>] [--replace_timestamp] [--output_path=<mode>]
fontnome t <input_path> [--separator=<text>] [--replace_timestamp] [--output_path=<mode>]
```

**Parameters:**
- `input_path`: Input font file
- `separator`: Separator before timestamp (default: `" tX"`)
- `replace_timestamp`: Remove old timestamp before adding new (default: `True`)
- `output_path`: Output mode (optional)

**Operation:**
1. Reads current `family_name` and `family_slug`
2. If `replace_timestamp=True` and using default separator:
   - Removes ` tX` and everything after from `family_name`
   - Removes `tX` and everything after from `family_slug`
3. Generates new timestamp using TIME_RULE
4. Appends `separator + timestamp` to `family_name`
5. Appends slug-converted suffix to `family_slug`

**Examples:**
```bash
# Default: replaces old timestamp on each run
$ fontnome timestamp MyFont.ttf
# First run:  "My Font" → "My Font tXt51r1v"
# Second run: "My Font tXt51r1v" → "My Font tXt51r2a"

# Keep accumulating timestamps
$ fontnome t MyFont.ttf --replace_timestamp=False

# Use custom separator
$ fontnome t MyFont.ttf --separator="-"
```

## Output Modes

All commands (except `view`) support flexible output handling via `--output_path`:

### Mode "0" (default)

Replace input file safely:

```bash
fontnome new MyFont.ttf --new_family="Test"  # --output_path="0" implied
```

### Mode "1"

Create backup with timestamp, then replace input:

```bash
fontnome new MyFont.ttf --new_family="Test" --output_path="1"
# Creates: MyFont--t51r1v.ttf (backup)
# Updates: MyFont.ttf (modified)
```

### Mode "2"

Save to timestamped output file, keep original:

```bash
fontnome new MyFont.ttf --new_family="Test" --output_path="2"
# Keeps: MyFont.ttf (original)
# Creates: MyFont--t51r1v.ttf (modified)
```

### Explicit Path

Save to specific file:

```bash
fontnome new MyFont.ttf --new_family="Test" --output_path="Output.ttf"
# Keeps: MyFont.ttf (original)
# Creates: Output.ttf (modified)
```

## Verbose Logging

Enable debug logging for troubleshooting:

```bash
fontnome --verbose view MyFont.ttf
fontnome --verbose new MyFont.ttf --new_family="Test"
```

## Technical Details

### Platform/Encoding Priority

When reading name records, fontnome tries:
1. Windows English: `(platformID=3, platEncID=1, langID=0x409)`
2. Mac Roman fallback: `(platformID=1, platEncID=0, langID=0)`

### nameID Field Mapping

**family_name** operations update:
- nameID 1: Font Family name (legacy)
- nameID 4: Full font name
- nameID 16: Typographic Family name
- nameID 18: Typographic Subfamily name
- nameID 21: WWS Family Name

**family_slug** operations update (no spaces):
- nameID 6: PostScript name
- nameID 20: PostScript CID findfont name
- nameID 25: Variations PostScript Name Prefix

### Reference Code

The implementation is based on fonttools patterns. Reference code studied:
- `vendors/fonttools/Snippets/rename-fonts.py`
- `vendors/fonttools/Lib/fontTools/varLib/instancer/names.py`

Note: The `vendors/` directory contains reference code only. fontnome uses the `fonttools` package from PyPI.

## Requirements

- Python 3.12+
- fonttools >= 4.50.0
- fire >= 0.6.0
- loguru >= 0.7.0

## Development

```bash
# Clone repository
git clone https://github.com/twardoch/fontnome
cd fontnome

# Create virtual environment
uv venv --python 3.12
source .venv/bin/activate  # or `.venv\Scripts\activate` on Windows

# Install in development mode
uv pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
ruff check src/
ruff format src/

# Run comprehensive test suite
./test.sh
```

## Testing

fontnome includes comprehensive tests:

```bash
# Unit tests
pytest tests/test_utils.py -v  # Slug and timestamp functions
pytest tests/test_core.py -v   # Font name operations

# All tests with coverage
pytest tests/ --cov=fontnome --cov-report=html

# Functional tests (via test.sh)
./test.sh
```

Test coverage: 93-95% on core modules (utils.py, core.py).

## License

Apache License 2.0

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Links

- PyPI: https://pypi.org/project/fontnome/
- GitHub: https://github.com/twardoch/fontnome
- Issues: https://github.com/twardoch/fontnome/issues

## Credits

Created by Adam Twardoch

Based on fonttools by Just van Rossum and contributors.
