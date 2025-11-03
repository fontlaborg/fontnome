# Dependencies

This document explains why each dependency was chosen for fontnome.

## Production Dependencies

### fonttools (>=4.50.0)

**Why chosen:**
- Industry-standard library for font manipulation
- Mature, well-maintained (4.3k+ GitHub stars)
- Complete OpenType/TrueType specification support
- Excellent documentation and community support
- Used by major font tools (Google Fonts, Adobe, etc.)

**What we use:**
- `TTFont`: Loading and saving font files
- `font["name"]`: Accessing name table records
- Name record reading/writing with platform/encoding support

**Alternatives considered:**
- Writing custom binary parser: Too complex, error-prone
- Other font libraries: None as comprehensive or maintained

### fire (>=0.6.0)

**Why chosen:**
- Simplest CLI framework with zero boilerplate
- Automatic help text generation from docstrings
- Built-in support for command aliases
- 27k+ GitHub stars, stable and mature
- Perfect for simple CLI tools

**What we use:**
- `fire.Fire()`: Main CLI entry point
- Automatic argument parsing and type conversion
- Command routing and help text

**Alternatives considered:**
- `click`: More verbose, unnecessary complexity for our use case
- `argparse`: Too much boilerplate, harder to maintain
- `typer`: Good but adds dependency on `rich` which we explicitly don't want

### loguru (>=0.7.0)

**Why chosen:**
- Clean, simple logging API
- Easy to configure with `--verbose` flag
- 20k+ GitHub stars, actively maintained
- Better defaults than stdlib logging
- Colored output support

**What we use:**
- `logger.debug()`, `logger.info()`, `logger.error()`: Logging operations
- `logger.remove()` and `logger.add()`: Custom configuration
- Conditional logging based on verbose flag

**Alternatives considered:**
- `logging` (stdlib): Works but requires more setup code
- `rich.logging`: Not needed since we don't use rich output

## Development Dependencies

### pytest (>=8.0.0)

**Why chosen:**
- Standard Python testing framework
- 12k+ GitHub stars
- Fixtures, parametrization, excellent error messages
- Mature ecosystem of plugins

**What we use:**
- Test discovery and execution
- Fixtures for test fonts and temp directories
- Test organization with classes

### pytest-cov (>=4.1.0)

**Why chosen:**
- De facto standard for Python test coverage
- Integrates seamlessly with pytest
- HTML and terminal coverage reports
- Can enforce minimum coverage thresholds

**What we use:**
- `--cov=fontnome`: Coverage tracking
- `--cov-report=html`: HTML coverage reports
- `--cov-fail-under=80`: Enforce 80% minimum coverage

### mypy (>=1.8.0)

**Why chosen:**
- Standard Python type checker
- Catches bugs at development time
- Enforces consistent typing
- Mature and widely adopted

**What we use:**
- Type checking for all source files
- Strict mode configuration in pyproject.toml

## Explicitly NOT Used

### rich

**Why NOT used:**
- README requirement: Use plain stdout only
- Project emphasizes simplicity
- CLI tool doesn't need fancy formatting
- Adds unnecessary dependency weight

We use plain `print()` for all user output.

## Build Dependencies

### hatchling

**Why chosen:**
- Modern Python build backend
- Simpler than setuptools
- Native support for src-layout

### hatch-vcs

**Why chosen:**
- Automatic version from git tags
- No manual version management
- Follows semantic versioning
- Integrates with hatchling

## Total Dependency Count

**Production:** 3 packages (fonttools, fire, loguru)
**Development:** 3 packages (pytest, pytest-cov, mypy)
**Build:** 2 packages (hatchling, hatch-vcs)

**Total:** 8 packages

This is intentionally minimal. Each dependency is well-justified and widely used.

## Security Considerations

All dependencies:
- Are actively maintained
- Have large user bases (catch security issues quickly)
- Come from trusted sources (PyPI)
- Have permissive open-source licenses
- Are pinned to minimum versions only (flexibility for security patches)

No dependencies have known critical CVEs at time of writing (2025-01-01).

## Maintenance

Dependencies should be reviewed quarterly. Update if:
- Security vulnerabilities are found
- New features we need are added
- Breaking changes require migration

Use `uv` commands for updates:
```bash
uv pip list --outdated
uv pip install --upgrade <package>
```
