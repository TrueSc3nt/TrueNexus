"""Sync puzzle 1..160 addresses + hex ranges from privatekeys.pw scrape."""
from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

ALPH = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
ROOT = Path(__file__).resolve().parents[1]
SRC_CANDIDATES = list(
    Path(r"C:\Users\loulo\.cursor\projects\d-TrueScent-TrueCollider\agent-tools").glob(
        "*.txt"
    )
)


def b58decode(s: str) -> bytes:
    n = 0
    for c in s:
        n = n * 58 + ALPH.index(c)
    pad = 0
    for c in s:
        if c == "1":
            pad += 1
        else:
            break
    full = n.to_bytes((n.bit_length() + 7) // 8 or 1, "big")
    h = b"\x00" * pad + full
    if len(h) < 25:
        h = h.rjust(25, b"\x00")
    if len(h) > 25:
        h = h[-25:]
    return h


def valid_addr(addr: str) -> bool:
    try:
        h = b58decode(addr)
        chk = hashlib.sha256(hashlib.sha256(h[:-4]).digest()).digest()[:4]
        return chk == h[-4:]
    except Exception:
        return False


def pick_src() -> Path:
    local = ROOT / "scripts" / "_privatekeys_scrape.txt"
    if local.is_file():
        return local
    # Prefer newest scrape that mentions Puzzle #160 and Bitcoin Address
    best = None
    best_mtime = -1.0
    for p in SRC_CANDIDATES:
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        if "Bitcoin Puzzle #160" in t and "Bitcoin Address:" in t:
            m = p.stat().st_mtime
            if m > best_mtime:
                best, best_mtime = p, m
    if not best:
        raise SystemExit("No privatekeys.pw scrape found")
    return best


def parse(text: str) -> dict[int, dict]:
    parts = re.split(r"##### Bitcoin Puzzle #(\d+)\s+", text)
    out: dict[int, dict] = {}
    it = iter(parts[1:])
    for num_s, body in zip(it, it):
        n = int(num_s)
        m_addr = re.search(
            r"Bitcoin Address:\s*\n+\s*C\s+(1[A-HJ-NP-Za-km-z1-9]{25,34})\b", body
        )
        m_hex = re.search(
            r"Key Range \(HEX\):\s*\n+\s*([0-9a-fA-F]+):([0-9a-fA-F]+)", body
        )
        m_bits = re.search(
            r"Key Range \(Bits\):\s*\n+\s*2\^?(\d+)\.?\.+\.?2\^?(\d+)", body
        )
        # Also accept "265...266" style (site uses 2^n without caret in markdown)
        if not m_bits:
            m_bits = re.search(
                r"Key Range \(Bits\):\s*\n+\s*2(\d+)\.\.\.2(\d+)", body
            )
        addr = m_addr.group(1) if m_addr else None
        if addr and not valid_addr(addr):
            addr = None
        start = m_hex.group(1).lower() if m_hex else None
        end = m_hex.group(2).lower() if m_hex else None
        head = body.lstrip()[:32].upper()
        if head.startswith("UNSOLVED"):
            status = "UNSOLVED"
        elif head.startswith("SOLVED"):
            status = "SOLVED"
        else:
            status = "?"
        out[n] = {
            "addr": addr,
            "start": start,
            "end": end,
            "bits_lo": int(m_bits.group(1)) if m_bits else None,
            "bits_hi": int(m_bits.group(2)) if m_bits else None,
            "status": status,
        }
    return out


def expected_range(n: int) -> tuple[str, str]:
    return format(1 << (n - 1), "x"), format((1 << n) - 1, "x")


def main() -> int:
    src = pick_src()
    print(f"source: {src}")
    data = parse(src.read_text(encoding="utf-8", errors="replace"))
    missing = [i for i in range(1, 161) if i not in data or not data[i]["addr"]]
    print(f"parsed with address: {160 - len(missing)}/160  missing={missing[:20]}")

    # Compare ranges
    range_mismatch = []
    for n in range(1, 161):
        exp_s, exp_e = expected_range(n)
        got = data.get(n, {})
        if got.get("start") and got.get("end"):
            if got["start"].lstrip("0") != exp_s.lstrip("0") and got["start"] != exp_s:
                # normalize
                if int(got["start"], 16) != int(exp_s, 16) or int(got["end"], 16) != int(
                    exp_e, 16
                ):
                    range_mismatch.append((n, got["start"], got["end"], exp_s, exp_e))
        else:
            # fill from formula
            got["start"], got["end"] = exp_s, exp_e

    print(f"range mismatches vs 2^(n-1)..2^n-1: {len(range_mismatch)}")
    for row in range_mismatch[:10]:
        print(" ", row)

    # Load current
    sys.path.insert(0, str(ROOT))
    from truenexus.puzzle_addresses import KNOWN_ADDR

    addr_diff = []
    for n in range(1, 161):
        new_a = data[n]["addr"] if n in data else None
        old_a = KNOWN_ADDR.get(n)
        if new_a and old_a != new_a:
            addr_diff.append((n, old_a, new_a))
    print(f"address diffs vs current catalog: {len(addr_diff)}")
    for n, old, new in addr_diff[:25]:
        print(f"  #{n}: {old} -> {new}")

    if missing:
        print("ERROR: cannot write incomplete table")
        return 1

    # Write puzzle_addresses.py
    out = ROOT / "truenexus" / "puzzle_addresses.py"
    lines = [
        '"""Official Bitcoin Puzzle Challenge addresses (puzzles 1-160).',
        "",
        "Source: https://privatekeys.pw/puzzles/bitcoin-puzzle-tx",
        "Range for puzzle N is always [2^(N-1) .. 2^N - 1].",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "KNOWN_ADDR: dict[int, str] = {",
    ]
    for i in range(1, 161):
        lines.append(f'    {i}: "{data[i]["addr"]}",')
    lines.append("}")
    lines.append("")
    lines.append("# Optional metadata from privatekeys.pw (status at scrape time)")
    lines.append("PUZZLE_STATUS: dict[int, str] = {")
    for i in range(1, 161):
        lines.append(f'    {i}: "{data[i]["status"]}",')
    lines.append("}")
    lines.append("")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}")

    # Spot checks
    for n in (1, 66, 70, 71, 75, 80, 130, 135, 160):
        s, e = expected_range(n)
        print(f"#{n} {data[n]['status']:8} {data[n]['addr']}  range {s}:{e}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
