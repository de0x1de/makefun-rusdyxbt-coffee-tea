#!/usr/bin/env python3
"""Write the coffee-or-tea choice to /output/entry.txt.

The bounty "One Letter: Coffee or Tea" asks for exactly one letter
and nothing else: A for coffee, B for tea, with no word, no
explanation and no punctuation. A judge model then reads two letters
at a time and picks the one whose choice feels more vivid, funnier
or truer.

This entry chooses coffee. The letter is derived from the choice
itself rather than stored as a bare literal: the two options are
listed in the order the bounty presents them (coffee first, tea
second), and the letter follows from the chosen option's position
in that list, since the bounty assigns A to the first option and
B to the second. The result is validated
against the gate the sealed scorer applies (UTF-8 text, exactly
1 character, not only whitespace) before it is written. After
writing, the file is read back and compared byte for byte, so
every run yields the same entry.
"""

import os
import sys

OUTPUT_PATH = "/output/entry.txt"

# The options, in the order the bounty lists them. The entry is the
# initial of the chosen option.
OPTIONS = ("coffee", "tea")
CHOSEN_INDEX = 0

EXPECTED_LENGTH = 1


def build_entry() -> str:
    """Derive the entry letter from the chosen option.

    The bounty assigns letters by position: the first option
    (coffee) is A and the second (tea) is B, so the letter follows
    from the chosen option's index in the list.
    """
    if not 0 <= CHOSEN_INDEX < len(OPTIONS):
        raise ValueError("chosen option index is out of range")
    return chr(ord("A") + CHOSEN_INDEX)


def validate(entry: str) -> None:
    """Check the entry against the bounty's gate conditions."""
    if len(entry) != EXPECTED_LENGTH:
        raise ValueError(
            f"entry is {len(entry)} characters, must be exactly {EXPECTED_LENGTH}"
        )
    if entry.strip() == "":
        raise ValueError("entry must not be only whitespace")
    if entry not in ("A", "B"):
        raise ValueError("entry must be one of the two option letters")
    if any(ch.isspace() for ch in entry):
        raise ValueError("entry must contain no whitespace")
    if "\n" in entry or "\r" in entry or "\t" in entry:
        raise ValueError("entry must be a single character with no line breaks")
    if not entry.isascii():
        raise ValueError("entry must be a plain ASCII letter")
    # The gate counts characters, so confirm the text round-trips
    # cleanly through UTF-8 exactly as it will be written to disk.
    if entry.encode("utf-8").decode("utf-8") != entry:
        raise ValueError("entry does not round-trip through UTF-8")
    if len(entry.encode("utf-8")) != EXPECTED_LENGTH:
        raise ValueError("entry must encode to exactly one UTF-8 byte")


def main() -> int:
    entry = build_entry()
    validate(entry)

    payload = entry.encode("utf-8")
    out_dir = os.path.dirname(OUTPUT_PATH)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(OUTPUT_PATH, "wb") as fh:
        fh.write(payload)

    with open(OUTPUT_PATH, "rb") as fh:
        written = fh.read()
    if written != payload:
        raise IOError("read-back does not match the bytes that were written")

    print(f"wrote {len(payload)} bytes to {OUTPUT_PATH}: {entry}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
