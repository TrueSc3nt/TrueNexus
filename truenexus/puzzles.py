"""Bitcoin Puzzle Challenge ranges (puzzles 1–160).

Range for puzzle N is [2^(N-1) .. 2^N - 1] (N-bit keyspace).
"""

from __future__ import annotations

from truenexus.puzzle_addresses import KNOWN_ADDR

__all__ = [
    "KNOWN_ADDR",
    "puzzle_range_hex",
    "puzzle_range_display",
    "puzzle_label",
    "puzzle_short_label",
    "all_puzzle_labels",
    "all_puzzle_short_labels",
    "parse_puzzle_number",
    "recommend_mode",
    "write_puzzle_target_file",
    "validate_puzzle",
]


def puzzle_range_hex(n: int) -> tuple[str, str]:
    """Return (start_hex, end_hex) without 0x prefix for puzzle N."""
    if n < 1 or n > 160:
        raise ValueError("Puzzle must be 1..160")
    start = 1 << (n - 1)
    end = (1 << n) - 1
    return format(start, "x"), format(end, "x")


def puzzle_range_display(n: int) -> str:
    start, end = puzzle_range_hex(n)
    return f"0x{start} .. 0x{end}"


def puzzle_label(n: int) -> str:
    start, end = puzzle_range_hex(n)
    addr = KNOWN_ADDR.get(n)
    if addr:
        return f"#{n:03d}  |  {n}-bit  |  {addr}"
    return f"#{n:03d}  |  {n}-bit  |  {puzzle_range_display(n)}"


def puzzle_short_label(n: int) -> str:
    return f"{n}"


def all_puzzle_labels() -> list[str]:
    return [puzzle_label(i) for i in range(1, 161)]


def all_puzzle_short_labels() -> list[str]:
    return [puzzle_short_label(i) for i in range(1, 161)]


def parse_puzzle_number(label: str) -> int:
    """Parse puzzle number from UI label, plain int, or '#066 …' forms."""
    s = (label or "").strip()
    if not s:
        raise ValueError("Empty puzzle label")
    # Plain number
    if s.isdigit():
        n = int(s)
        if 1 <= n <= 160:
            return n
        raise ValueError(f"Puzzle out of range: {n}")
    # "#066 | ..." or "Puzzle #066 | ..."
    for token in s.replace("Puzzle", " ").replace("#", " ").split():
        token = token.strip(".|")
        if token.isdigit():
            n = int(token)
            if 1 <= n <= 160:
                return n
    raise ValueError(f"Cannot parse puzzle number from: {label!r}")


def validate_puzzle(n: int) -> None:
    start, end = puzzle_range_hex(n)
    assert int(start, 16) == (1 << (n - 1))
    assert int(end, 16) == (1 << n) - 1
    assert n in KNOWN_ADDR
    addr = KNOWN_ADDR[n]
    assert 26 <= len(addr) <= 35
    assert addr[0] == "1"


def recommend_mode(n: int) -> str:
    if n <= 40:
        return "address + sequential — tiny range, great for learning"
    if n <= 70:
        return "address / rmd160 + CUDA — classic mid-puzzle grind"
    if n <= 90:
        return "bsgs (needs pubkey) or address grind"
    if n <= 125:
        return "bsgs or kangaroo — pubkey required for DL modes"
    return "kangaroo or hybrid-dl (HerdHandoff) — large-interval ECDLP"


def write_puzzle_target_file(n: int, path: str, kind: str = "address") -> str:
    """Write a one-line target file for a puzzle. Returns path."""
    start, end = puzzle_range_hex(n)
    addr = KNOWN_ADDR.get(n)
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Puzzle {n} | {n}-bit | range 0x{start}:0x{end}\n")
        if kind == "address" and addr:
            f.write(addr + "\n")
        elif addr:
            f.write(addr + "\n")
    return path
