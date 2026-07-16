"""Bitcoin Puzzle Challenge ranges (puzzles 1–160).

Range for puzzle N is [2^(N-1) .. 2^N - 1].
"""

from __future__ import annotations

# Public challenge addresses (subset commonly used in TrueCollider fixtures / docs)
KNOWN_ADDR: dict[int, str] = {
    66: "13zb1hQbWVsc2S7ZTZnP2G4indNNwkSoBV",
    67: "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9",
    68: "1MVDYgVaSN6iKKEsbzRUAYFrYJadLYZvzC",
    69: "19vkiEajfhuZ8bs8Zu2jgmC6oqZbWqhxhG",
    70: "1PWo3JeB9jrGwfHDNpdGK54CRasEfsXJh",
    71: "1JTK7s9YVYywfm5XUH7RNhHJH1LshCaRFR",
    72: "1PWCx5fovoEaoBowAvF5k91m2Xat9bMgwb",
    73: "1Be2UFHXrye6tqRqpwQZcAvZ4wig3Yq",
    74: "1ARWEXG4gHMz9Y1P7ZsLvsfgbvxJyQq",
    75: "1PrcMVRex5PHyMFBtcA91DWmfqrmrNY",
    80: "1HduPEXZRdG26SUT5YkgnvjXrKzihnDq",
    130: "1Fo65aKq8s8iquMt6weF1rku1moWVEd5Ua",
    135: "16RGFo6hjq9ym6Pj7N5H7L1NR1rVPJyw2v",
    140: "1QKBaU6WAeycb3DbKbLBkX7vJiaS8r42Xo",
    145: "19GpszRNUej5yYqxXoLnbZWKew3KdVLkXg",
    150: "1MUJSJYtGPVGkBCTqGspnxyHahpt5Te8jy",
    155: "1AoeP37TmHdFh8uN72fu9AqgtLrUwcv2wJ",
    160: "1NBC8uXJy1GiJ6drkiZa1WuKn51ps7EPTv",
}


def puzzle_range_hex(n: int) -> tuple[str, str]:
    if n < 1 or n > 160:
        raise ValueError("Puzzle must be 1..160")
    start = 1 << (n - 1)
    end = (1 << n) - 1
    return format(start, "x"), format(end, "x")


def puzzle_label(n: int) -> str:
    start, end = puzzle_range_hex(n)
    addr = KNOWN_ADDR.get(n)
    if addr:
        return f"Puzzle #{n:03d}  |  {n}-bit  |  {addr}"
    return f"Puzzle #{n:03d}  |  {n}-bit  |  0x{start} … 0x{end}"


def all_puzzle_labels() -> list[str]:
    return [puzzle_label(i) for i in range(1, 161)]


def parse_puzzle_number(label: str) -> int:
    part = label.split("|")[0].strip()
    return int(part.replace("Puzzle #", "").strip())


def recommend_mode(n: int) -> str:
    if n <= 40:
        return "address + sequential/chaos — tiny range, great for learning"
    if n <= 70:
        return "address / rmd160 + CUDA — classic mid-puzzle grind"
    if n <= 90:
        return "bsgs (pubkey) or address — more RAM = bigger -k"
    if n <= 125:
        return "bsgs or kangaroo — pubkey required for discrete-log modes"
    return "kangaroo or HerdHandoff hybrid — large-interval ECDLP"


def write_puzzle_target_file(n: int, path: str, kind: str = "address") -> str:
    """Write a one-line target file for a puzzle. Returns path."""
    start, end = puzzle_range_hex(n)
    addr = KNOWN_ADDR.get(n)
    with open(path, "w", encoding="utf-8") as f:
        if kind == "address" and addr:
            f.write(addr + "\n")
        else:
            f.write(f"# Puzzle {n} range 0x{start}:0x{end}\n")
            if addr:
                f.write(addr + "\n")
    return path
