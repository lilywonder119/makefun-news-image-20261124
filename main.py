#!/usr/bin/env python3
"""THE GILDED PAGE - NI24 entry carrier (Final 7, @lilywonder1).

Standard library only. Copies the entry image built in this recorded
session (entry.png, 1024x1024) to the grader output directory.
No network, no Pillow, no other dependencies. The copy is byte-for-byte,
so the gate (1024x1024, at most 1,048,576 bytes) is satisfied by the
built entry.png itself; this carrier adds nothing and changes nothing.
"""
import os
import shutil
import sys


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, "entry.png")
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    dst = os.path.join(outdir, "entry.png")
    shutil.copyfile(src, dst)
    print("copied entry.png -> " + dst)


if __name__ == "__main__":
    sys.exit(main())
