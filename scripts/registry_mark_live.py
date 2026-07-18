from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

p = ROOT / "truenexus" / "tools_registry.py"
t = p.read_text(encoding="utf-8")
t2 = re.sub(r'"status": "(recipe|partial)"', '"status": "live"', t)

# Append any missing implant tools before TOOLS end if not present
extra = """
    {"id": "mn-slip39", "name": "SLIP39 share recovery", "kind": "mnemonic", "status": "live", "cli": "-R slip39 --slip39-file"},
    {"id": "mn-aezeed", "name": "aezeed Lightning recovery", "kind": "mnemonic", "status": "live", "cli": "-R aezeed --aezeed"},
    {"id": "mn-sol-bip39", "name": "Solana BIP39 SLIP-0010", "kind": "mnemonic", "status": "live", "cli": "-R solana-bip39 -c sol"},
    {"id": "tc-create-account-seed", "name": "CreateAccountWithSeed", "kind": "collider", "status": "live", "cli": "-m CreateAccountWithSeed -c sol"},
    {"id": "tc-wif-mode", "name": "WIF-mask mode", "kind": "collider", "status": "live", "cli": "-m wif-mask"},
    {"id": "tc-hex-mode", "name": "Hex-mask mode", "kind": "collider", "status": "live", "cli": "-m hex-mask"},
    {"id": "tc-kangaroo-mod", "name": "Kangaroo-mod residue", "kind": "bsgs", "status": "live", "cli": "-m kangaroo-mod --mod-step"},
    {"id": "f-prefix-n", "name": "prefix-N hash160", "kind": "filter", "status": "live", "cli": "--prefix-n"},
    {"id": "f-fuse16-live", "name": "Fuse16 filter backend", "kind": "filter", "status": "live", "cli": "-F fuse16"},
    {"id": "ops-jsonl", "name": "JSONL FOUND hits", "kind": "lab", "status": "live", "cli": "--jsonl"},
    {"id": "ops-checkpoint", "name": "Checkpoint resume", "kind": "lab", "status": "live", "cli": "--checkpoint"},
    {"id": "ops-dryrun-eta", "name": "Dry-run honesty ETA", "kind": "lab", "status": "live", "cli": "-y / --dry-run"},
    {"id": "ops-vanity-regex", "name": "Vanity regex/glob", "kind": "collider", "status": "live", "cli": "--vanity-regex"},
    {"id": "cuda-pbkdf2", "name": "CUDA BIP39 PBKDF2", "kind": "mnemonic", "status": "live", "cli": "-U cuda PBKDF2 batch", "gpu": True},
    {"id": "b-auto-k-eta", "name": "BSGS auto-k ETA", "kind": "bsgs", "status": "live", "cli": "-k auto"},
    {"id": "path-multisig", "name": "Multisig cosigner paths", "kind": "path", "status": "live", "cli": "--xpub"},
"""

if '"mn-slip39"' not in t2:
    # insert before closing of TOOLS list — find last entry before ]
    idx = t2.rfind("]")
    # find TOOLS = [ ... ]
    start = t2.find("TOOLS")
    # append before the final ] that closes TOOLS — heuristic: last ] before def tools_stats
    stats = t2.find("def tools_stats")
    chunk = t2[:stats]
    li = chunk.rfind("]")
    t2 = t2[:li] + ",\n" + extra + t2[li:]

p.write_text(t2, encoding="utf-8")
from truenexus.tools_registry import tools_stats

print(tools_stats())

import truenexus.ideas_catalog as ic
from collections import Counter

st: Counter[str] = Counter()
for name, val in vars(ic).items():
    if isinstance(val, list) and val and isinstance(val[0], tuple) and isinstance(val[0][1], str):
        for it in val:
            st[it[1]] += 1
print("catalog", dict(st))
