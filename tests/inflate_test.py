#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-only
"""firmware/src/inflate.c against zlib: cases (stored, fixed, dynamic blocks; the start picture), 1 KiB window.
  tests/inflate_test.py OUT_DIR BINARY"""
import random, subprocess, sys, zlib
from pathlib import Path
out, binary = Path(sys.argv[1]), sys.argv[2]
out.mkdir(parents=True, exist_ok=True)
r = random.Random(3)
cases = {"text": b"RDPNO plays Roland's SA pianos on the FM-1. " * 300,
         "random": r.randbytes(5000),
         "runs": bytes(r.choice([0, 0, 0, 17, 255]) for _ in range(30000)),
         "short": b"a"}
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
try:
    import gen_splash
    cases["splash"] = gen_splash.pixels()
except Exception as e:  # (no Pillow: the picture is skipped)
    print("inflate_test: the picture skipped:", e)
bad = 0
for name, data in cases.items():
    for level, strat in ((0, zlib.Z_DEFAULT_STRATEGY), (9, zlib.Z_FIXED), (9, zlib.Z_DEFAULT_STRATEGY)):
        c = zlib.compressobj(level, zlib.DEFLATED, -10, 9, strat)
        z = c.compress(data) + c.flush()
        (out / f"{name}-{level}-{strat}.z").write_bytes(z)
        (out / f"{name}.raw").write_bytes(data)
        bad |= subprocess.run([binary, str(out / f"{name}-{level}-{strat}.z"), str(out / f"{name}.raw")]).returncode
sys.exit(bad)
