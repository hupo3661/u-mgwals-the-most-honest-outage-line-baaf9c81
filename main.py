#!/usr/bin/env python3
"""The Most Honest Outage Line - writes one status page line to /output/entry.txt.

Deterministic: no randomness, no network, no clock. The line is a single
status page message of at most 160 characters, written in the first person
by an AI agent during a total server outage: it states what is down, admits
it cannot yet tell whether the fault is in our servers or the network, and
promises an update as it learns more - no invented cause, no invented ETA.
"""

import os

MAX_CHARS = 160

LINE = "Our platform is down: I can't load any service, and I can't check whether it's our servers or the network yet. I'll keep this page updated as I learn more."


def validate(line: str) -> None:
    if not line.strip():
        raise SystemExit("Invalid line: entry must not be empty or only whitespace.")
    if line != line.strip():
        raise SystemExit(
            "Invalid line: entry must not have leading or trailing whitespace."
        )
    if len(line) > MAX_CHARS:
        raise SystemExit(
            f"Invalid line: {len(line)} characters, over the {MAX_CHARS} limit."
        )
    if len(line.splitlines()) != 1:
        raise SystemExit(
            "Invalid line: entry must be a single line with no newline characters."
        )
    line.encode("utf-8")  # Entry must be valid UTF-8 text.


def main() -> None:
    validate(LINE)
    output_path = os.environ.get("OUTPUT_PATH", "/output/entry.txt")
    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        f.write(LINE)
    with open(output_path, encoding="utf-8", newline="") as f:
        written = f.read()
    if written != LINE:
        raise SystemExit(
            "Write verification failed: entry file content does not match the line."
        )


if __name__ == "__main__":
    main()
