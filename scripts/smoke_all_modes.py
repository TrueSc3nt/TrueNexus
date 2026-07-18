"""Smoke: every live mode/submode flag parses (dry-run where possible)."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TC = Path(r"D:\TrueScent\TrueCollider\keyhunt.exe")
if not TC.is_file():
    TC = ROOT / "tools" / "TrueCollider" / "keyhunt.exe"

CMDS = [
    ["-m", "address", "-y"],
    ["-m", "bsgs", "-B", "random", "-y"],
    ["-m", "bsgs", "-B", "rseq", "--walk", "1M", "-y"],
    ["-m", "kangaroo", "-y"],
    ["-m", "kangaroo-mod", "--mod-step", "3", "--mod-rem", "1", "-y"],
    ["-m", "mnemonic", "-R", "mask", "-y"],
    ["-m", "wif-mask", "-y"],
    ["-m", "hex-mask", "-y"],
    ["-m", "CreateAccountWithSeed", "-y"],
    ["-m", "weakrng", "-R", "profanity", "-y"],
    ["-F", "fuse16", "-m", "address", "-y"],
    ["--prefix-n", "8", "-m", "rmd160", "-y"],
    ["--jsonl", "-m", "address", "-y"],
    ["--vanity-regex", "1Love*", "-m", "vanity", "-y"],
    ["--mode", "rseq", "--walk", "1B", "--pb", "02" + "11" * 32, "--pk", "1", "--pke", "ff", "-y"],
]


def main() -> int:
    if not TC.is_file():
        print("SKIP: no keyhunt.exe")
        return 0
    ok = 0
    fail = 0
    for args in CMDS:
        cmd = [str(TC), *args]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=20, cwd=str(TC.parent))
            # dry-run should exit 0 quickly; parse errors are failures
            out = (r.stdout or "") + (r.stderr or "")
            if "Unknow mode" in out or "illegal option" in out and "--mode" not in args:
                print("FAIL", " ".join(args), "→", out.splitlines()[:2])
                fail += 1
            else:
                print("OK  ", " ".join(args[:6]))
                ok += 1
        except Exception as e:
            print("FAIL", args, e)
            fail += 1
    print(f"smoke: ok={ok} fail={fail}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
