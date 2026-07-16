"""Extract puzzle 1..160 addresses from scraped privatekeys.pw dump."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

SRC = Path(
    r"C:\Users\loulo\.cursor\projects\d-TrueScent-TrueCollider"
    r"\agent-tools\edbd5aeb-4ff7-4672-97e2-e63232f7e780.txt"
)
OUT = Path(__file__).resolve().parents[1] / "truenexus" / "puzzle_addresses.py"

ALPH = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


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


def main() -> None:
    text = SRC.read_text(encoding="utf-8", errors="replace")
    parts = re.split(r"##### Bitcoin Puzzle #(\d+)\s+", text)
    addrs: dict[int, str] = {}
    it = iter(parts[1:])
    for num_s, body in zip(it, it):
        n = int(num_s)
        m = re.search(
            r"Bitcoin Address:\s*\n+\s*C\s+(1[A-HJ-NP-Za-km-z1-9]{25,34})\b",
            body,
        )
        if not m:
            m = re.search(r"\nC\s+(1[A-HJ-NP-Za-km-z1-9]{25,34})\b", body)
        if m and valid_addr(m.group(1)):
            addrs[n] = m.group(1)

    missing = [i for i in range(1, 161) if i not in addrs]
    bad = [(i, a) for i, a in sorted(addrs.items()) if not valid_addr(a)]
    if missing or bad:
        raise SystemExit(f"missing={missing} bad={bad}")

    lines = [
        '"""Official Bitcoin Puzzle Challenge addresses (puzzles 1-160)."""',
        "",
        "from __future__ import annotations",
        "",
        "KNOWN_ADDR: dict[int, str] = {",
    ]
    for i in range(1, 161):
        lines.append(f'    {i}: "{addrs[i]}",')
    lines.append("}")
    lines.append("")
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT} ({len(addrs)} valid addresses)")
    for k in (1, 66, 70, 71, 73, 80, 160):
        print(k, addrs[k])


if __name__ == "__main__":
    main()
