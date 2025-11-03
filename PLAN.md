# fontnome Implementation Plan

## Project Status

**Current Version:** 0.1.0 (MVP Complete)
**Status:** All core features implemented and tested

## Project Scope

**One-sentence scope:** CLI tool that modifies font family names and PostScript slugs in OpenType/TrueType fonts using exact nameID field manipulation rules.

## Completed Phases

### ✅ Phase 1: Project Setup
- Created complete project structure
- Configured pyproject.toml with hatch-vcs
- Set up development environment
- Downloaded test font fixtures

### ✅ Phase 2: Core Utilities
- Implemented SLUG_RULE function (make_slug)
- Implemented TIME_RULE function (make_timestamp)
- All utility functions tested (95% coverage)

### ✅ Phase 3: Font Name Reading
- Implemented cascading fallback reading (nameID 16→21→1 for family, 25→6 for slug)
- Platform/encoding priority (Windows English → Mac Roman)
- Comprehensive tests (93% coverage)

### ✅ Phase 4: Safe File Operations
- Implemented safe write pattern (temp → backup → move)
- Three output modes (0, 1, 2)
- Explicit path support
- All modes tested

### ✅ Phase 5: CLI Commands
- All 6 commands implemented: view, new, replace, suffix, prefix, timestamp
- All command aliases working (v, n, r, s, p, t)
- Fire-based CLI with auto-generated help
- Error handling and logging

### ✅ Phase 6: Testing
- 26 unit tests covering core functionality
- Integration tests
- Manual CLI testing
- Test coverage: 93-95% on core modules

### ✅ Phase 7: Documentation
- Comprehensive README.md with installation and usage
- DEPENDENCIES.md explaining all packages
- CHANGELOG.md with release notes
- WORK.md tracking implementation progress
- test.sh for automated testing

## Future Enhancement Phases

### Phase 8: Batch Processing (Future)

**Goal:** Process multiple font files in one command

**Implementation:**
- Accept glob patterns or multiple input paths
- Parallel processing for performance
- Progress reporting
- Error handling per file

**Commands:**
```bash
fontnome new *.ttf --new_family="Custom Font"
fontnome suffix fonts/**/*.otf --suffix=" Beta"
```

### Phase 9: Configuration File Support (Future)

**Goal:** Allow default settings via config file

**Implementation:**
- `.fontnomerc` in TOML format
- Project-level and user-level configs
- Override via CLI flags

**Example config:**
```toml
[fontnome]
default_output_mode = "1"  # Always create backups
verbose = false
separator = " tX"
```

### Phase 10: Validation Mode (Future)

**Goal:** Preview changes without modifying files

**Implementation:**
- `--dry-run` flag for all commands
- Show what would change
- Validate font integrity

**Usage:**
```bash
fontnome new font.ttf --new_family="Test" --dry-run
```

### Phase 11: Advanced Features (Future)

**Potential additions:**
- More nameID operations (beyond family names)
- Font format conversion support
- Name table validation and repair
- Integration with font build pipelines

## Technical Architecture (Current)

### Module Structure

```
src/fontnome/
├── __init__.py          # Package initialization
├── __main__.py          # CLI entry point (Fire)
├── core.py              # Font operations
└── utils.py             # Utility functions
```

### Key Design Decisions

1. **Two-phase operations:** Separate family_name and family_slug with independent transformation
2. **Cascading fallback:** Priority-based nameID reading
3. **Safe file writes:** Atomic operations with optional backups
4. **No rich output:** Plain stdout as per requirements
5. **Verbose logging:** Optional debug mode with loguru

### Dependencies

| Package    | Purpose                      |
|-----------|------------------------------|
| fonttools | Font manipulation            |
| fire      | CLI framework                |
| loguru    | Logging                      |
| pytest    | Testing                      |
| pytest-cov| Test coverage               |
| mypy      | Type checking                |

## Success Metrics

**Current Status:** ✅ All metrics met

1. ✅ All 6 CLI commands work
2. ✅ All command aliases work
3. ✅ All 3 output modes work
4. ✅ Core test coverage ≥ 80% (93-95%)
5. ✅ All tests pass
6. ✅ Documentation complete
7. ✅ Installable via uv/pip
8. ✅ Follows development guidelines

## Lessons Learned

**What Worked Well:**
- Clear requirements enabled straightforward implementation
- Test-first approach caught bugs early
- Using established patterns from reference code
- All dependency choices were excellent
- Fire made CLI implementation trivial

**What Could Improve:**
- Could add CLI integration tests
- Could enforce stricter line length limits
- Could create minimal test fonts

**Technical Decisions Validated:**
- Fire for CLI: Excellent choice
- fonttools: Perfect for the job
- NOT using rich: Kept things simple
- Safe file writing: Worked flawlessly
- loguru: Clean and simple
- hatch-vcs: Automatic versioning

## Future Considerations

### Performance
- Current implementation handles typical font files efficiently
- For batch processing, consider parallel execution
- Profile with very large font families

### Compatibility
- Currently supports Python 3.12+
- Consider Python 3.10+ for wider compatibility
- Test with various font formats and structures

### User Experience
- Consider interactive mode for beginners
- Add more detailed error messages
- Provide examples for common use cases

### Maintenance
- Review dependencies quarterly
- Monitor fonttools for API changes
- Keep documentation current

---

**Note:** This plan document is maintained as a reference for potential future development. The v0.1.0 MVP is complete and fully functional.
