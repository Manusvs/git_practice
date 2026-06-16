#!/usr/bin/env python3

import subprocess
import sys
from pathlib import Path

MAX_LINE_LENGTH = 120


def get_staged_sv_files():
    """
    Return a list of staged .sv files.
    """
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only"],
        capture_output=True,
        text=True
    )

    files = []

    for file in result.stdout.splitlines():
        if file.endswith(".sv"):
            files.append(file)

    return files


def check_file(filepath):
    """
    Check a SystemVerilog file for violations.
    """
    errors = []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

    except Exception as e:
        errors.append(f"Cannot read file: {e}")
        return errors

    # Check line length
    for lineno, line in enumerate(lines, start=1):
        if len(line.rstrip("\n")) > MAX_LINE_LENGTH:
            errors.append(
                f"Line {lineno}: exceeds {MAX_LINE_LENGTH} characters"
            )

    # Check deprecated 'reg'
    for lineno, line in enumerate(lines, start=1):
        if "reg" in line.split():
            errors.append(
                f"Line {lineno}: uses deprecated keyword 'reg'"
            )

    # Check header comment in first 5 lines
    first_five = "".join(lines[:5])

    if "Author:" not in first_five:
        errors.append(
            "Missing 'Author:' in first 5 lines"
        )

    if "Date:" not in first_five:
        errors.append(
            "Missing 'Date:' in first 5 lines"
        )

    return errors


def main():
    staged_files = get_staged_sv_files()

    if not staged_files:
        sys.exit(0)

    violations_found = False

    for file in staged_files:
        errors = check_file(file)

        if errors:
            violations_found = True

            print(f"\nERRORS IN {file}")
            print("-" * 50)

            for error in errors:
                print(f"  - {error}")

    if violations_found:
        print("\nCommit blocked by pre-commit hook.")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

