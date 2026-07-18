"""wallet.dat forensic inspector — extract mkey/ckey/pubs for TrueMkeyCollider.

Does not crack passwords. Parses Bitcoin Core BDB wallet.dat by scanning
known record tags and 48-byte AES blobs + secp hex for copy/paste or Send→TrueMkey.
"""

from __future__ import annotations

import hashlib
import re
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


TAG_STRINGS = (
    b"mkey",
    b"ckey",
    b"key",
    b"wkey",
    b"name",
    b"version",
    b"minversion",
    b"bestblock",
    b"defaultkey",
    b"pool",
    b"hdchain",
    b"hdpubkey",
    b"purpose",
    b"destdata",
    b"watchs",
    b"cscript",
    b"tx",
)


@dataclass
class ExtractedBlob:
    kind: str  # mkey | ckey | key | other
    enc_hex: str = ""
    pubkey_hex: str = ""
    offset: int = 0
    note: str = ""


@dataclass
class WalletReport:
    path: str
    size: int = 0
    sha256: str = ""
    tags_found: dict[str, int] = field(default_factory=dict)
    mkeys: list[ExtractedBlob] = field(default_factory=list)
    ckeys: list[ExtractedBlob] = field(default_factory=list)
    pubkeys: list[str] = field(default_factory=list)
    names: list[str] = field(default_factory=list)
    versions: list[int] = field(default_factory=list)
    other_notes: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def summary_text(self) -> str:
        lines = [
            f"=== wallet.dat forensic report ===",
            f"path: {self.path}",
            f"size: {self.size} bytes",
            f"sha256: {self.sha256}",
            f"tags: {self.tags_found}",
            f"mkey blobs: {len(self.mkeys)}",
            f"ckey blobs: {len(self.ckeys)}",
            f"pubkeys: {len(self.pubkeys)}",
            f"address labels: {len(self.names)}",
            f"version records: {self.versions}",
            "",
        ]
        if self.mkeys:
            lines.append("--- mkey (96 hex for -mckey) ---")
            for i, b in enumerate(self.mkeys):
                lines.append(f"[{i}] @{b.offset} {b.enc_hex}")
                if b.note:
                    lines.append(f"    note: {b.note}")
            lines.append("")
        if self.ckeys:
            lines.append("--- ckey (ENC96 [PUBHEX]) ---")
            for i, b in enumerate(self.ckeys):
                if b.pubkey_hex:
                    lines.append(f"[{i}] {b.enc_hex} {b.pubkey_hex}")
                else:
                    lines.append(f"[{i}] {b.enc_hex}")
            lines.append("")
        if self.pubkeys:
            lines.append("--- pubkeys ---")
            for p in self.pubkeys[:200]:
                lines.append(p)
            if len(self.pubkeys) > 200:
                lines.append(f"... ({len(self.pubkeys) - 200} more)")
            lines.append("")
        if self.names:
            lines.append("--- name labels (sample) ---")
            for n in self.names[:50]:
                lines.append(n)
            lines.append("")
        for e in self.errors:
            lines.append(f"[!] {e}")
        for n in self.other_notes:
            lines.append(f"[i] {n}")
        lines.append("=== end report ===")
        return "\n".join(lines)


def _hex(b: bytes) -> str:
    return b.hex()


def _looks_pubkey(b: bytes) -> bool:
    if len(b) == 33 and b[0] in (2, 3):
        return True
    if len(b) == 65 and b[0] == 4:
        return True
    return False


def _find_tag_counts(data: bytes) -> dict[str, int]:
    out: dict[str, int] = {}
    for tag in TAG_STRINGS:
        # BDB often stores key with 1-byte length prefix
        pat = bytes([len(tag)]) + tag
        c = data.count(pat)
        if c == 0:
            c = data.count(tag)
        if c:
            out[tag.decode("ascii", errors="ignore")] = c
    return out


def _extract_ascii_names(data: bytes) -> list[str]:
    # name records often contain printable address/label strings
    names: list[str] = []
    for m in re.finditer(rb"name.{0,4}([\x20-\x7e]{6,80})", data):
        s = m.group(1).decode("ascii", errors="ignore").strip()
        if s and s not in names:
            names.append(s)
    return names[:500]


def _extract_pubkeys(data: bytes) -> list[str]:
    pubs: list[str] = []
    seen: set[str] = set()
    i = 0
    n = len(data)
    while i < n - 33:
        b0 = data[i]
        if b0 in (2, 3):
            cand = data[i : i + 33]
            h = _hex(cand)
            if h not in seen:
                seen.add(h)
                pubs.append(h)
            i += 33
            continue
        if b0 == 4 and i + 65 <= n:
            cand = data[i : i + 65]
            h = _hex(cand)
            if h not in seen:
                seen.add(h)
                pubs.append(h)
            i += 65
            continue
        i += 1
    return pubs


def _nearby_pubkey(data: bytes, center: int, window: int = 128) -> str:
    lo = max(0, center - window)
    hi = min(len(data), center + window)
    chunk = data[lo:hi]
    for off in range(0, len(chunk) - 32):
        if _looks_pubkey(chunk[off : off + 33]):
            return _hex(chunk[off : off + 33])
        if off + 65 <= len(chunk) and _looks_pubkey(chunk[off : off + 65]):
            return _hex(chunk[off : off + 65])
    return ""


def _scan_encrypted_near_tags(data: bytes) -> tuple[list[ExtractedBlob], list[ExtractedBlob]]:
    """Find 48-byte blobs near mkey/ckey tags (TrueMkey 96-hex format)."""
    mkeys: list[ExtractedBlob] = []
    ckeys: list[ExtractedBlob] = []
    seen_enc: set[str] = set()

    def consider(kind: str, off: int, blob: bytes) -> None:
        if len(blob) != 48:
            return
        hx = _hex(blob)
        if hx in seen_enc:
            return
        # skip low-entropy filler
        if len(set(blob)) < 8:
            return
        seen_enc.add(hx)
        pub = _nearby_pubkey(data, off) if kind == "ckey" else ""
        rec = ExtractedBlob(kind=kind, enc_hex=hx, pubkey_hex=pub, offset=off)
        if kind == "mkey":
            mkeys.append(rec)
        else:
            ckeys.append(rec)

    for tag, kind in ((b"mkey", "mkey"), (b"ckey", "ckey")):
        start = 0
        while True:
            idx = data.find(tag, start)
            if idx < 0:
                break
            # search forward for a 48-byte candidate in following 256 bytes
            region = data[idx : idx + 300]
            for rel in range(0, max(0, len(region) - 48)):
                # prefer length prefix 0x30 (48)
                if region[rel] == 0x30 and rel + 1 + 48 <= len(region):
                    consider(kind, idx + rel + 1, region[rel + 1 : rel + 1 + 48])
                consider(kind, idx + rel, region[rel : rel + 48])
            start = idx + 1

    return mkeys, ckeys


def inspect_wallet_dat(path: str | Path) -> WalletReport:
    p = Path(path)
    rep = WalletReport(path=str(p.resolve()))
    if not p.is_file():
        rep.errors.append("file not found")
        return rep
    data = p.read_bytes()
    rep.size = len(data)
    rep.sha256 = hashlib.sha256(data).hexdigest()
    if rep.size < 64:
        rep.errors.append("file too small to be wallet.dat")
        return rep

    # Bitcoin Core BDB magic-ish / page markers
    if b"\x00\x05\x31\x62" in data[:8192] or b"wallet.dat" in data[:4096] or b"mkey" in data or b"ckey" in data:
        rep.other_notes.append("Looks like a Bitcoin Core-style wallet.dat (BDB records detected).")
    else:
        rep.other_notes.append("No strong wallet.dat signature — still scanned for blobs.")

    rep.tags_found = _find_tag_counts(data)
    rep.names = _extract_ascii_names(data)
    rep.pubkeys = _extract_pubkeys(data)
    rep.mkeys, rep.ckeys = _scan_encrypted_near_tags(data)

    # version ints near "version" tag
    for m in re.finditer(rb"version", data):
        off = m.end()
        chunk = data[off : off + 16]
        if len(chunk) >= 4:
            # little-endian int common in BDB values
            v = struct.unpack_from("<I", chunk, 0)[0]
            if 1 <= v <= 100000 and v not in rep.versions:
                rep.versions.append(v)

    if not rep.mkeys and not rep.ckeys:
        rep.other_notes.append(
            "No 48-byte mkey/ckey blobs found near tags. "
            "Wallet may be unencrypted, descriptor wallet (SQLite), or already empty."
        )
    if rep.ckeys and not any(c.pubkey_hex for c in rep.ckeys):
        rep.other_notes.append(
            "ckeys lack paired pubkeys — TrueMkey can still search AES, "
            "but WIF post-hit needs pubkeys file."
        )
    return rep


def export_for_truemkey(report: WalletReport, out_dir: str | Path) -> dict[str, str]:
    """Write mkeys.txt / ckeys.txt / pubkeys.txt for TrueMkeyCollider. Returns paths."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths: dict[str, str] = {}

    mkey_path = out / "mkeys_from_wallet.txt"
    ckey_path = out / "ckeys_from_wallet.txt"
    pub_path = out / "pubkeys_from_wallet.txt"
    report_path = out / "wallet_forensic_report.txt"

    mkey_path.write_text("\n".join(b.enc_hex for b in report.mkeys) + ("\n" if report.mkeys else ""), encoding="utf-8")
    c_lines = []
    for b in report.ckeys:
        if b.pubkey_hex:
            c_lines.append(f"{b.enc_hex} {b.pubkey_hex}")
        else:
            c_lines.append(b.enc_hex)
    ckey_path.write_text("\n".join(c_lines) + ("\n" if c_lines else ""), encoding="utf-8")

    pubs = list(report.pubkeys)
    for b in report.ckeys:
        if b.pubkey_hex and b.pubkey_hex not in pubs:
            pubs.insert(0, b.pubkey_hex)
    pub_path.write_text("\n".join(pubs) + ("\n" if pubs else ""), encoding="utf-8")
    report_path.write_text(report.summary_text(), encoding="utf-8")

    paths["mkeys"] = str(mkey_path)
    paths["ckeys"] = str(ckey_path)
    paths["pubkeys"] = str(pub_path)
    paths["report"] = str(report_path)
    return paths
