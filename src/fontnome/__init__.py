#!/usr/bin/env python3
# this_file: src/fontnome/__init__.py
"""fontnome - CLI tool for modifying font family names."""

try:
    from fontnome._version import __version__
except ImportError:
    __version__ = "0.0.0+unknown"

__all__ = ["__version__"]
