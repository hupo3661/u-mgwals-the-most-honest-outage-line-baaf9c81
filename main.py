#!/usr/bin/env python3
"""The Most Honest Outage Line — a single honest status-page message.

Purpose
-------
This program produces exactly one line of text for the make.fun bounty
``u-mgwals-the-most-honest-outage-line-baaf9c81`` ("The Most Honest Outage
Line").  The line is written, as if by an AI agent during a total outage,
in the first person.  It does three things and nothing more:

* states plainly what is down (the platform / every service it can load);
* admits honestly what is not yet known — whether the fault lies in our
  own servers or in the network; and
* promises to keep the status page updated as more is learned.

It deliberately invents no cause and no estimated time of recovery,
because during a real outage neither would be known yet.

Behaviour
---------
The program is fully deterministic: it uses no randomness, no network
access and no clock.  Running it validates the entry text and then writes
it, with no trailing newline, to ``/output/entry.txt`` (the destination
can be overridden with the ``OUTPUT_PATH`` environment variable).  After
writing, the file is read back and compared byte-for-byte in text form
against the intended line, so a silent write failure cannot pass.

Constraints enforced by :func:`validate`
----------------------------------------
* the entry must not be empty or only whitespace;
* it must carry no leading or trailing whitespace;
* it must be at most ``MAX_CHARS`` (160) characters long;
* it must be a single line, containing no newline characters;
* it must contain no control characters; and
* it must be encodable as UTF-8 text.
"""

from __future__ import annotations

import os
import sys

# --- Constants -----------------------------------------------------------

#: Maximum length, in characters, allowed for the status-page line.
MAX_CHARS = 160

#: Default destination for the entry file when OUTPUT_PATH is not set.
DEFAULT_OUTPUT_PATH = "/output/entry.txt"

#: Environment variable that may override the output destination.
OUTPUT_PATH_ENV_VAR = "OUTPUT_PATH"

#: The entry itself.  This text is the submission; do not edit it lightly —
#: any change here is a change to what is being entered for the bounty.
LINE = "Our platform is down: I can't load any service, and I can't check whether it's our servers or the network yet. I'll keep this page updated as I learn more."


# --- Validation ----------------------------------------------------------

def validate(line: str) -> None:
    """Check ``line`` against every rule for the entry.

    Args:
        line: The candidate status-page line to check.

    Raises:
        SystemExit: With a human-readable explanation if any rule fails.
            ``SystemExit`` is used (rather than a bare ``assert``) so the
            check cannot be disabled with ``python -O`` and so the process
            exits non-zero with the reason on stderr.
    """
    # Reject empty / whitespace-only content first: every later check
    # assumes there is real text to inspect.
    if not line.strip():
        raise SystemExit("Invalid line: entry must not be empty or only whitespace.")

    # Surrounding whitespace would be invisible on a status page but would
    # still count against the character budget, so it is not allowed.
    if line != line.strip():
        raise SystemExit(
            "Invalid line: entry must not have leading or trailing whitespace."
        )

    # The bounty caps the line at MAX_CHARS characters.
    if len(line) > MAX_CHARS:
        raise SystemExit(
            f"Invalid line: {len(line)} characters, over the {MAX_CHARS} limit."
        )

    # A status-page line must be exactly one line.
    if len(line.splitlines()) != 1:
        raise SystemExit(
            "Invalid line: entry must be a single line with no newline characters."
        )

    # Control characters (including DEL) have no place in display text.
    if any(ord(ch) < 0x20 or ord(ch) == 0x7F for ch in line):
        raise SystemExit(
            "Invalid line: entry must not contain control characters."
        )

    # The entry is written as UTF-8; fail early if it cannot be encoded.
    line.encode("utf-8")


# --- Output --------------------------------------------------------------

def resolve_output_path() -> str:
    """Return the path the entry should be written to.

    Uses ``OUTPUT_PATH`` from the environment when set, and falls back to
    :data:`DEFAULT_OUTPUT_PATH` otherwise.
    """
    return os.environ.get(OUTPUT_PATH_ENV_VAR, DEFAULT_OUTPUT_PATH)


def utf8_byte_length(text: str) -> int:
    """Return the number of bytes ``text`` occupies when encoded as UTF-8.

    Used as an extra write-verification signal: the file on disk should be
    exactly this many bytes, which catches stray trailing newlines or any
    encoding translation that a text-only comparison might mask on some
    platforms.
    """
    return len(text.encode("utf-8"))


def write_entry(line: str, output_path: str) -> None:
    """Write ``line`` to ``output_path`` and verify the write by reading back.

    Parent directories are created as needed.  The file is written with
    ``newline=""`` so no platform newline translation can alter the text.

    Raises:
        SystemExit: If the content read back does not match ``line``.
    """
    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    with open(output_path, "w", encoding="utf-8", newline="") as handle:
        handle.write(line)

    with open(output_path, encoding="utf-8", newline="") as handle:
        written = handle.read()

    if written != line:
        raise SystemExit(
            "Write verification failed: entry file content does not match the line."
        )

    if os.path.getsize(output_path) != utf8_byte_length(line):
        raise SystemExit(
            "Write verification failed: entry file size does not match the "
            "UTF-8 byte length of the line (possible stray newline or "
            "encoding translation)."
        )


def main() -> int:
    """Validate the entry line, write it out, and report success.

    Returns:
        ``0`` on success.  Validation and write-verification failures raise
        ``SystemExit`` with a non-zero status and an explanatory message.
    """
    validate(LINE)
    write_entry(LINE, resolve_output_path())
    return 0


if __name__ == "__main__":
    sys.exit(main())
