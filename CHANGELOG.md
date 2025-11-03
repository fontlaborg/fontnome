# Changelog

All notable changes to fontnome are documented here. The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed
- **timestamp command**: Default separator changed from `" "` to `" tX"`
- **timestamp command**: Added `--replace_timestamp` parameter (default: True) to replace old timestamps instead of accumulating them
- **All commands**: Now output in consistent format `path:family_name` after modification (matching `view --long` format)

## [0.1.0] - 2025-11-01

### Added
- Initial release with full CLI functionality
- Six commands: `view`, `new`, `replace`, `suffix`, `prefix`, `timestamp` (with single-letter aliases)
- Font name table reading with cascading fallback (nameID 16→21→1 for family, 25→6 for slug)
- SLUG_RULE: ASCII 33-126 except `[](){}<%>/`, no spaces
- TIME_RULE: Lowercase base-36 Unix timestamps
- Safe file writing: temp file → optional backup → atomic move
- Three output modes: replace (0), backup+replace (1), timestamped output (2)
- Verbose logging with `--verbose` flag
- Comprehensive test suite (93-95% coverage on core modules)
- Complete documentation (README, PLAN, DEPENDENCIES, etc.)

### Technical
- Uses fonttools for font manipulation
- Uses fire for CLI interface
- Uses loguru for logging
- Type hints throughout
- Platform/encoding fallback: Windows English → Mac Roman

---

**Version History:**
- 0.1.0 (2025-11-01): Initial release
