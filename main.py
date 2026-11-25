#!/usr/bin/env python3
"""THE VELVET LEDGER - NI24 carrier (stdlib only).

Opens entry.png in the same directory, verifies the gate
(1024x1024 PNG, at most 1 MiB), and emits its bytes exactly:
to MAKEFUN_OUTPUT_DIR/entry.png when that variable is set,
otherwise to stdout as raw bytes.
"""
import os
import struct
import sys

MAX_BYTES = 1024 * 1024


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "entry.png")
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) > MAX_BYTES:
        sys.exit("entry.png exceeds 1 MiB gate")
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        sys.exit("entry.png is not a PNG")
    width, height = struct.unpack(">II", data[16:24])
    if (width, height) != (1024, 1024):
        sys.exit("entry.png is not 1024x1024")
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "entry.png"), "wb") as fh:
            fh.write(data)
    else:
        sys.stdout.buffer.write(data)
    return 0


if __name__ == "__main__":
    sys.exit(main())
