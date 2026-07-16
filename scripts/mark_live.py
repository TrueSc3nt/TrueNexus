import re
from collections import Counter
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "truenexus" / "ideas_catalog.py"
t = p.read_text(encoding="utf-8")
names = [
    "pass-rules",
    "language-guess",
    "rfc1751",
    "bip85",
    "electrum-v1",
    "paths-custom",
]
for name in names:
    pat = rf'(\(\s*"{re.escape(name)}"\s*,\s*")research(")'
    t, n = re.subn(pat, r"\1live\2", t)
    print(f"{name}: {n}")
p.write_text(t, encoding="utf-8")

import sys
sys.path.insert(0, str(p.parents[1]))
from truenexus.ideas_catalog import all_idea_cards

print(Counter(s for _, s, _ in all_idea_cards()))
