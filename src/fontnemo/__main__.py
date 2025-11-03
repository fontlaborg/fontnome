#!/usr/bin/env python3
# this_file: src/fontnome/__main__.py
"""CLI entry point for fontnome using Fire."""

import sys

import fire
from loguru import logger

from fontnome.core import FontNameHandler, save_font_safely
from fontnome.utils import make_slug, make_timestamp


class FontNomeCLI:
    """fontnome CLI - Modify font family names in OpenType/TrueType fonts."""

    def __init__(self, verbose: bool = False) -> None:
        """Initialize CLI with optional verbose logging.

        Args:
            verbose: Enable debug logging
        """
        # Configure loguru
        logger.remove()  # Remove default handler
        if verbose:
            logger.add(sys.stderr, level="DEBUG")
        else:
            logger.add(sys.stderr, level="WARNING")

        self.verbose = verbose

    def view(self, input_path: str, long: bool = False) -> None:
        """Display current font family name.

        Args:
            input_path: Input font file (.ttf, .otf)
            long: If True, show path prefix in output

        Examples:
            fontnome view font.ttf
            fontnome v font.ttf --long
        """
        try:
            handler = FontNameHandler(input_path)
            family_name = handler.read_family_name()
            handler.close()

            if long:
                print(f"{input_path}:{family_name}")
            else:
                print(family_name)

        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)

    def v(self, input_path: str, long: bool = False) -> None:
        """Alias for view command."""
        return self.view(input_path=input_path, long=long)

    def new(
        self,
        input_path: str,
        new_family: str,
        output_path: str = "0",
        long: bool = False,
    ) -> None:
        """Set new font family name.

        Args:
            input_path: Input font file
            new_family: New family name
            output_path: Output mode:
                - "0" (default): Replace input file
                - "1": Backup original, then replace
                - "2": Save with timestamp suffix
                - path string: Save to specific path
            long: If True, show path prefix in output

        Examples:
            fontnome new font.ttf --new_family="My New Font"
            fontnome n font.ttf --new_family="Test" --output_path="output.ttf"
        """
        try:
            handler = FontNameHandler(input_path)

            # Generate slug from new family name
            new_slug = make_slug(new_family)

            logger.info(f"Setting family_name: {new_family!r}")
            logger.info(f"Setting family_slug: {new_slug!r}")

            # Write changes
            handler.write_family_name(new_family)
            handler.write_family_slug(new_slug)

            # Save with appropriate mode
            final_path = save_font_safely(handler, output_path)
            handler.close()

            # Print final result
            result_handler = FontNameHandler(final_path)
            final_family_name = result_handler.read_family_name()
            result_handler.close()

            if long:
                print(f"{final_path}:{final_family_name}")
            else:
                print(final_family_name)

        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)

    def n(
        self,
        input_path: str,
        new_family: str,
        output_path: str = "0",
        long: bool = False,
    ) -> None:
        """Alias for new command."""
        return self.new(
            input_path=input_path,
            new_family=new_family,
            output_path=output_path,
            long=long,
        )

    def replace(
        self,
        input_path: str,
        find: str,
        replace: str,
        output_path: str = "0",
        long: bool = False,
    ) -> None:
        """Find and replace in font family name.

        Args:
            input_path: Input font file
            find: String to find
            replace: String to replace with
            output_path: Output mode (see 'new' command)
            long: If True, show path prefix in output

        Examples:
            fontnome replace font.ttf --find="Old" --replace="New"
            fontnome r font.ttf --find="Test" --replace="Production"
        """
        try:
            handler = FontNameHandler(input_path)

            # Read current names
            family_name = handler.read_family_name()
            family_slug = handler.read_family_slug()

            # Replace in family name
            new_family_name = family_name.replace(find, replace)

            # Replace in slug (convert find/replace to slugs first)
            find_slug = make_slug(find)
            replace_slug = make_slug(replace)
            new_family_slug = family_slug.replace(find_slug, replace_slug)

            logger.info(f"family_name: {family_name!r} → {new_family_name!r}")
            logger.info(f"family_slug: {family_slug!r} → {new_family_slug!r}")

            # Write changes
            handler.write_family_name(new_family_name)
            handler.write_family_slug(new_family_slug)

            # Save
            final_path = save_font_safely(handler, output_path)
            handler.close()

            # Print final result
            result_handler = FontNameHandler(final_path)
            final_family_name = result_handler.read_family_name()
            result_handler.close()

            if long:
                print(f"{final_path}:{final_family_name}")
            else:
                print(final_family_name)

        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)

    def r(
        self,
        input_path: str,
        find: str,
        replace: str,
        output_path: str = "0",
        long: bool = False,
    ) -> None:
        """Alias for replace command."""
        return self.replace(
            input_path=input_path,
            find=find,
            replace=replace,
            output_path=output_path,
            long=long,
        )

    def suffix(
        self,
        input_path: str,
        suffix: str,
        output_path: str = "0",
        long: bool = False,
    ) -> None:
        """Append suffix to font family name.

        Args:
            input_path: Input font file
            suffix: Suffix to append
            output_path: Output mode (see 'new' command)
            long: If True, show path prefix in output

        Examples:
            fontnome suffix font.ttf --suffix=" Beta"
            fontnome s font.ttf --suffix=" v2"
        """
        try:
            handler = FontNameHandler(input_path)

            # Read current names
            family_name = handler.read_family_name()
            family_slug = handler.read_family_slug()

            # Append suffix
            new_family_name = family_name + suffix
            new_family_slug = family_slug + make_slug(suffix)

            logger.info(f"family_name: {family_name!r} → {new_family_name!r}")
            logger.info(f"family_slug: {family_slug!r} → {new_family_slug!r}")

            # Write changes
            handler.write_family_name(new_family_name)
            handler.write_family_slug(new_family_slug)

            # Save
            final_path = save_font_safely(handler, output_path)
            handler.close()

            # Print final result
            result_handler = FontNameHandler(final_path)
            final_family_name = result_handler.read_family_name()
            result_handler.close()

            if long:
                print(f"{final_path}:{final_family_name}")
            else:
                print(final_family_name)

        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)

    def s(
        self,
        input_path: str,
        suffix: str,
        output_path: str = "0",
        long: bool = False,
    ) -> None:
        """Alias for suffix command."""
        return self.suffix(
            input_path=input_path,
            suffix=suffix,
            output_path=output_path,
            long=long,
        )

    def prefix(
        self,
        input_path: str,
        prefix: str,
        output_path: str = "0",
        long: bool = False,
    ) -> None:
        """Prepend prefix to font family name.

        Args:
            input_path: Input font file
            prefix: Prefix to prepend
            output_path: Output mode (see 'new' command)
            long: If True, show path prefix in output

        Examples:
            fontnome prefix font.ttf --prefix="Beta "
            fontnome p font.ttf --prefix="Draft "
        """
        try:
            handler = FontNameHandler(input_path)

            # Read current names
            family_name = handler.read_family_name()
            family_slug = handler.read_family_slug()

            # Prepend prefix
            new_family_name = prefix + family_name
            new_family_slug = make_slug(prefix) + family_slug

            logger.info(f"family_name: {family_name!r} → {new_family_name!r}")
            logger.info(f"family_slug: {family_slug!r} → {new_family_slug!r}")

            # Write changes
            handler.write_family_name(new_family_name)
            handler.write_family_slug(new_family_slug)

            # Save
            final_path = save_font_safely(handler, output_path)
            handler.close()

            # Print final result
            result_handler = FontNameHandler(final_path)
            final_family_name = result_handler.read_family_name()
            result_handler.close()

            if long:
                print(f"{final_path}:{final_family_name}")
            else:
                print(final_family_name)

        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)

    def p(
        self,
        input_path: str,
        prefix: str,
        output_path: str = "0",
        long: bool = False,
    ) -> None:
        """Alias for prefix command."""
        return self.prefix(
            input_path=input_path,
            prefix=prefix,
            output_path=output_path,
            long=long,
        )

    def timestamp(
        self,
        input_path: str,
        separator: str = " tX",
        replace_timestamp: bool = True,
        output_path: str = "0",
        long: bool = False,
    ) -> None:
        """Append timestamp suffix to font family name.

        Args:
            input_path: Input font file
            separator: Separator before timestamp (default: " tX")
            replace_timestamp: Remove old timestamp before adding new (default: True)
            output_path: Output mode (see 'new' command)
            long: If True, show path prefix in output

        Examples:
            fontnome timestamp font.ttf
            fontnome t font.ttf --separator="-"
            fontnome t font.ttf --replace_timestamp=False
        """
        try:
            handler = FontNameHandler(input_path)

            # Read current names
            family_name = handler.read_family_name()
            family_slug = handler.read_family_slug()

            # Remove old timestamp if requested and using default separator
            if replace_timestamp and separator == " tX":
                # Remove " tX" and everything after from family name
                if " tX" in family_name:
                    family_name = family_name.split(" tX")[0]

                # Remove "tX" and everything after from family slug
                if "tX" in family_slug:
                    family_slug = family_slug.split("tX")[0]

            # Generate new timestamp
            timestamp = make_timestamp()
            suffix_str = separator + timestamp

            # Add timestamp suffix
            new_family_name = family_name + suffix_str
            new_family_slug = family_slug + make_slug(suffix_str)

            logger.info(f"family_name: {family_name!r} → {new_family_name!r}")
            logger.info(f"family_slug: {family_slug!r} → {new_family_slug!r}")

            # Write changes
            handler.write_family_name(new_family_name)
            handler.write_family_slug(new_family_slug)

            # Save
            final_path = save_font_safely(handler, output_path)
            handler.close()

            # Print final result
            result_handler = FontNameHandler(final_path)
            final_family_name = result_handler.read_family_name()
            result_handler.close()

            if long:
                print(f"{final_path}:{final_family_name}")
            else:
                print(final_family_name)

        except Exception as e:
            logger.error(f"Error: {e}")
            sys.exit(1)

    def t(
        self,
        input_path: str,
        separator: str = " tX",
        replace_timestamp: bool = True,
        output_path: str = "0",
        long: bool = False,
    ) -> None:
        """Alias for timestamp command."""
        return self.timestamp(
            input_path=input_path,
            separator=separator,
            replace_timestamp=replace_timestamp,
            output_path=output_path,
            long=long,
        )


def main() -> None:
    """Main entry point for CLI."""
    fire.Fire(FontNomeCLI)


if __name__ == "__main__":
    main()
