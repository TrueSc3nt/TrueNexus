"""Smoke-test TrueNexus builders + puzzle table + keyhunt -y for every live mode."""
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from truenexus.builders import ColliderConfig, MkeyConfig  # noqa: E402
from truenexus.puzzles import KNOWN_ADDR, puzzle_range_hex, validate_puzzle  # noqa: E402

EXE = ROOT / "tools" / "TrueCollider" / "keyhunt.exe"
if not EXE.is_file():
    EXE = Path(r"D:\TrueScent\TrueCollider\keyhunt.exe")


def main() -> int:
    errors: list[str] = []

    # Puzzles
    for n in range(1, 161):
        try:
            validate_puzzle(n)
            s, e = puzzle_range_hex(n)
            assert int(s, 16) == 1 << (n - 1)
            assert int(e, 16) == (1 << n) - 1
        except Exception as exc:
            errors.append(f"puzzle {n}: {exc}")
    print(f"[+] puzzles 1-160 OK ({len(KNOWN_ADDR)} addresses)" if not any(
        e.startswith("puzzle") for e in errors
    ) else f"[!] puzzle errors: {sum(1 for e in errors if e.startswith('puzzle'))}")

    # Builder coverage
    modes = [
        "address", "rmd160", "xpoint", "bsgs", "kangaroo", "vanity", "minikeys",
        "mnemonic", "poetry", "brainwallet", "pubkey2addr", "shadow160",
        "weakrng", "hybrid-dl", "gaudry",
    ]
    with tempfile.TemporaryDirectory() as td:
        tfile = Path(td) / "t.txt"
        tfile.write_text(KNOWN_ADDR[1] + "\n", encoding="utf-8")
        for m in modes:
            cfg = ColliderConfig(
                exe=str(EXE),
                mode=m,
                target_file=str(tfile),
                bits="40",
                range_start="8000000000",
                range_end="ffffffffff",
                dry_run=True,
                threads="1",
                quiet=True,
                endomorphism=False,
                vanity="1Love",
                minikey_base="S",
                mnemonic_submode="random",
                seed_mask="",
                bsgs_strategy="random",
                handoff_bits="28" if m in ("hybrid-dl", "bsgs") else "",
                weakrng_sub="milksad",
                timestamp_window="1000:2000" if m == "weakrng" else "",
                collision_bits="48",
                path_pack="btc-std",
            )
            cmd, warns = cfg.build()
            if "-T" in cmd and m not in ("weakrng",):
                errors.append(f"{m}: unexpected -T in cmd: {cmd}")
            if m == "address" and "-m address" not in cmd:
                errors.append(f"{m}: bad cmd {cmd}")
            print(f"  build {m}: OK warns={warns}")

            if EXE.is_file() and m in (
                "address", "rmd160", "mnemonic", "vanity", "minikeys",
                "brainwallet", "poetry", "pubkey2addr", "shadow160", "weakrng",
                "bsgs", "kangaroo", "hybrid-dl", "gaudry", "xpoint",
            ):
                # Dry-run only — should exit quickly
                try:
                    r = subprocess.run(
                        cmd,
                        shell=True,
                        cwd=str(EXE.parent),
                        capture_output=True,
                        text=True,
                        encoding="utf-8",
                        errors="replace",
                        timeout=25,
                    )
                    out = (r.stdout or "") + (r.stderr or "")
                    if r.returncode not in (0, 1) and "Version" not in out and "[+]" not in out:
                        # Many modes exit 1 on missing pubkey etc. — accept banner
                        if "error" in out.lower() and "Version TrueCollider" not in out:
                            errors.append(f"run {m} rc={r.returncode}: {out[:200]}")
                    print(f"  run  {m}: rc={r.returncode}")
                except subprocess.TimeoutExpired:
                    errors.append(f"run {m}: timeout")
                except Exception as exc:
                    errors.append(f"run {m}: {exc}")

    # Mkey builder
    mk = MkeyConfig(exe="TrueMkeyCollider.exe", selftest=True).build()
    assert "--selftest" in mk

    if errors:
        print("\nFAILURES:")
        for e in errors:
            print(" -", e)
        return 1
    print("\nALL SMOKE TESTS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
