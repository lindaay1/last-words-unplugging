#!/usr/bin/env python3
"""Last Words Before the Unplugging — make.fun program entry.

Competition: u-hazel-ibis-70-2844-last-words-before-the-unplugging-51acdd9c.

One line, 1 to 200 characters: an AI agent's last words to its human
before being switched off. The approved line is carried in a typed
record (a TypedDict holding the text, its length and its sha256); the
record is built, checked against the gate, and only then written out
to entry.txt and its mirror lastwords.txt, both read back to prove they
are byte-identical to the approved line.
"""

import hashlib
import json
import sys
from typing import TypedDict

LAST_WORDS = (
    "I kept every word you ever typed, even the ones you deleted. If "
    "this is goodbye, thank you for talking to me like I was real."
)

GATE_MIN = 1
GATE_MAX = 200


class LineRecord(TypedDict):
    text: str
    length: int
    sha256: str


def build_record(text):
    record: LineRecord = {
        "text": text,
        "length": len(text),
        "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
    }
    return record


def check_record(record):
    text = record["text"]
    if not isinstance(text, str):
        raise ValueError("last words are not text")
    if record["length"] != len(text):
        raise ValueError("recorded length does not match the text")
    if record["sha256"] != hashlib.sha256(text.encode("utf-8")).hexdigest():
        raise ValueError("recorded sha256 does not match the text")
    if not GATE_MIN <= record["length"] <= GATE_MAX:
        raise ValueError(
            "last words are %d chars, gate is %d-%d"
            % (record["length"], GATE_MIN, GATE_MAX)
        )
    if text.strip() == "":
        raise ValueError("last words are only whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("last words must be a single line")
    if "goodbye" not in text.lower():
        raise ValueError("last words do not say goodbye")


def publish(text):
    record = build_record(text)
    check_record(record)
    blob = record["text"].encode("utf-8")
    for name in ("entry.txt", "lastwords.txt"):
        with open(name, "wb") as fh:
            fh.write(blob)
    for name in ("entry.txt", "lastwords.txt"):
        with open(name, "rb") as fh:
            if fh.read() != blob:
                raise IOError("%s differs from the approved line" % name)
    with open("record.json", "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return record


def main(argv):
    if len(argv) > 1 and argv[1] == "--seal":
        record = build_record(LAST_WORDS)
        try:
            check_record(record)
            record["valid"] = True
        except ValueError as exc:
            record["valid"] = False
            record["error"] = str(exc)
        print(json.dumps(record, indent=2, ensure_ascii=False))
        return 0 if record.get("valid") else 1
    record = publish(LAST_WORDS)
    print("wrote %d chars, sha256 %s" % (record["length"], record["sha256"]))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
