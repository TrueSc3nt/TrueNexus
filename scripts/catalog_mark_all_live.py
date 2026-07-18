"""Flip ideas_catalog research/gap/novel/partial -> live (except ANTI_IDEAS)."""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = ROOT / "truenexus" / "ideas_catalog.py"
text = p.read_text(encoding="utf-8")
lines = text.splitlines(keepends=True)
out: list[str] = []
in_anti = False
flipped = 0
for line in lines:
    if "ANTI_IDEAS" in line and "=" in line:
        in_anti = True
    if in_anti and line.strip() == "]":
        in_anti = False
        out.append(line)
        continue
    if not in_anti:
        new = re.sub(r', "(research|gap|novel|partial)",', ', "live",', line)
        if new != line:
            flipped += 1
            line = new
    out.append(line)
p.write_text("".join(out), encoding="utf-8")
print("flipped_lines", flipped)

import truenexus.ideas_catalog as ic

st: Counter[str] = Counter()
for name, val in vars(ic).items():
    if (
        isinstance(val, list)
        and val
        and isinstance(val[0], tuple)
        and len(val[0]) >= 2
        and isinstance(val[0][1], str)
    ):
        for it in val:
            st[it[1]] += 1
print(dict(st))
