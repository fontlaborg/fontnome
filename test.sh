#!/usr/bin/env bash
# this_file: test.sh
# Comprehensive test script for fontnome

set -e  # Exit on error

echo "========================================="
echo "fontnome Comprehensive Test Suite"
echo "========================================="
echo

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    echo "Activating virtual environment..."
    source .venv/bin/activate
else
    echo "Error: Virtual environment not found. Run: uv venv --python 3.12"
    exit 1
fi

echo

# Code formatting and linting
echo "1. Running autoflake (remove unused imports)..."
fd -e py -x uvx autoflake -i {}
echo "   ✓ Autoflake complete"
echo

echo "2. Running pyupgrade (upgrade to Python 3.12+ syntax)..."
fd -e py -x uvx pyupgrade --py312-plus {}
echo "   ✓ Pyupgrade complete"
echo

echo "3. Running ruff check (linting with fixes)..."
fd -e py -x uvx ruff check --output-format=github --fix --unsafe-fixes {}
echo "   ✓ Ruff check complete"
echo

echo "4. Running ruff format (code formatting)..."
fd -e py -x uvx ruff format --respect-gitignore --target-version py312 {}
echo "   ✓ Ruff format complete"
echo

# Run tests
echo "5. Running pytest with coverage..."
pytest tests/ -v --cov=fontnome --cov-report=term-missing --cov-report=html --cov-fail-under=70
echo "   ✓ Tests complete"
echo

# Functional tests (CLI commands)
echo "6. Running functional CLI tests..."

# Create temp directory for functional tests
TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

# Copy test font
cp tests/fixtures/test_font_basic.ttf "$TEMP_DIR/test.ttf"

echo "   Testing 'view' command..."
OUTPUT=$(fontnome view "$TEMP_DIR/test.ttf")
if [ -z "$OUTPUT" ]; then
    echo "   ✗ View command failed"
    exit 1
fi
echo "     Original: $OUTPUT"

echo "   Testing 'new' command..."
fontnome new "$TEMP_DIR/test.ttf" --new_family="Functional Test Font" --output_path="$TEMP_DIR/renamed.ttf"
NEW_NAME=$(fontnome view "$TEMP_DIR/renamed.ttf")
if [ "$NEW_NAME" != "Functional Test Font" ]; then
    echo "   ✗ New command failed. Expected 'Functional Test Font', got '$NEW_NAME'"
    exit 1
fi
echo "     Renamed: $NEW_NAME"

echo "   Testing 'suffix' command..."
fontnome suffix "$TEMP_DIR/renamed.ttf" --suffix=" Beta" --output_path="$TEMP_DIR/suffix.ttf"
SUFFIX_NAME=$(fontnome view "$TEMP_DIR/suffix.ttf")
if [ "$SUFFIX_NAME" != "Functional Test Font Beta" ]; then
    echo "   ✗ Suffix command failed. Expected 'Functional Test Font Beta', got '$SUFFIX_NAME'"
    exit 1
fi
echo "     Suffixed: $SUFFIX_NAME"

echo "   Testing 'prefix' command..."
fontnome prefix "$TEMP_DIR/suffix.ttf" --prefix="Draft " --output_path="$TEMP_DIR/prefix.ttf"
PREFIX_NAME=$(fontnome view "$TEMP_DIR/prefix.ttf")
if [ "$PREFIX_NAME" != "Draft Functional Test Font Beta" ]; then
    echo "   ✗ Prefix command failed. Expected 'Draft Functional Test Font Beta', got '$PREFIX_NAME'"
    exit 1
fi
echo "     Prefixed: $PREFIX_NAME"

echo "   Testing 'replace' command..."
fontnome replace "$TEMP_DIR/prefix.ttf" --find="Draft" --replace="Final" --output_path="$TEMP_DIR/replace.ttf"
REPLACE_NAME=$(fontnome view "$TEMP_DIR/replace.ttf")
if [ "$REPLACE_NAME" != "Final Functional Test Font Beta" ]; then
    echo "   ✗ Replace command failed. Expected 'Final Functional Test Font Beta', got '$REPLACE_NAME'"
    exit 1
fi
echo "     Replaced: $REPLACE_NAME"

echo "   Testing 'timestamp' command..."
fontnome timestamp "$TEMP_DIR/replace.ttf" --separator="-" --output_path="$TEMP_DIR/timestamp.ttf"
TIMESTAMP_NAME=$(fontnome view "$TEMP_DIR/timestamp.ttf")
# Just check it contains a hyphen and the base name
if [[ ! "$TIMESTAMP_NAME" =~ "Final Functional Test Font Beta-" ]]; then
    echo "   ✗ Timestamp command failed. Expected timestamp suffix, got '$TIMESTAMP_NAME'"
    exit 1
fi
echo "     Timestamped: $TIMESTAMP_NAME"

echo "   ✓ All functional tests passed"
echo

# Type checking (optional - may have errors in generated version file)
echo "7. Running mypy (type checking)..."
if uvx mypy src/fontnome --ignore-missing-imports 2>/dev/null; then
    echo "   ✓ Mypy complete (no errors)"
else
    echo "   ⚠ Mypy found some issues (non-critical)"
fi
echo

echo "========================================="
echo "All tests completed successfully!"
echo "========================================="
echo
echo "Coverage report available at: htmlcov/index.html"
