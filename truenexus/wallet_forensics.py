"""wallet.dat forensic inspector — full piece-by-piece extract for TrueMkeyCollider.

Parses Bitcoin Core BDB wallet.dat:
  - CompactSize + CMasterKey (mkey)
  - ckey records (pubkey in key, 48-byte AES blob in value)
  - plain key / name / version / pool / hdchain tags
  - SQLite descriptor-wallet detection

Does NOT crack passwords. Export → Send→TrueMkey prefills -mckey/-ckeys/-pubkeys.
"""

from __future__ import annotations

import hashlib
import re
import struct
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExtractedBlob:
    kind: str  # mkey | ckey | key | meta
    enc_hex: str = ""
    pubkey_hex: str = ""
    offset: int = 0
    note: str = ""
    iterations: int = 0
    salt_hex: str = ""
    derivation_method: int = -1
    master_id: int = -1


@dataclass
class WalletReport:
    path: str
    size: int = 0
    sha256: str = ""
    format: str = "unknown"  # bdb | sqlite | unknown
    tags_found: dict[str, int] = field(default_factory=dict)
    mkeys: list[ExtractedBlob] = field(default_factory=list)
    ckeys: list[ExtractedBlob] = field(default_factory=list)
    plain_keys: list[ExtractedBlob] = field(default_factory=list)
    pubkeys: list[str] = field(default_factory=list)
    names: list[str] = field(default_factory=list)
    versions: list[int] = field(default_factory=list)
    hd_notes: list[str] = field(default_factory=list)
    other_notes: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    pieces: list[str] = field(default_factory=list)  # forensic timeline

    def summary_text(self) -> str:
        lines = [
            "=== wallet.dat FORENSIC REPORT (piece-by-piece) ===",
            f"path: {self.path}",
            f"size: {self.size} bytes",
            f"sha256: {self.sha256}",
            f"format: {self.format}",
            f"tags: {self.tags_found}",
            f"mkey: {len(self.mkeys)} | ckey: {len(self.ckeys)} | plain key: {len(self.plain_keys)} | pubs: {len(self.pubkeys)}",
            f"versions: {self.versions}",
            "",
            "--- dissection log ---",
        ]
        lines.extend(self.pieces[:400])
        if len(self.pieces) > 400:
            lines.append(f"... ({len(self.pieces) - 400} more steps)")
        lines.append("")
        if self.mkeys:
            lines.append("--- mkey blobs (96-hex for TrueMkey -mckey) ---")
            for i, b in enumerate(self.mkeys):
                lines.append(f"[{i}] id={b.master_id} @{b.offset}")
                lines.append(f"    enc:  {b.enc_hex}")
                if b.salt_hex:
                    lines.append(f"    salt: {b.salt_hex}")
                if b.iterations:
                    lines.append(f"    iterations: {b.iterations}  method: {b.derivation_method}")
                if b.note:
                    lines.append(f"    note: {b.note}")
            lines.append("")
        if self.ckeys:
            lines.append("--- ckey blobs (ENC96 [PUB] for -ckeys) ---")
            for i, b in enumerate(self.ckeys):
                if b.pubkey_hex:
                    lines.append(f"[{i}] {b.enc_hex} {b.pubkey_hex}")
                else:
                    lines.append(f"[{i}] {b.enc_hex}")
            lines.append("")
        if self.plain_keys:
            lines.append("--- UNENCRYPTED key records (sensitive) ---")
            for i, b in enumerate(self.plain_keys[:50]):
                lines.append(f"[{i}] pub={b.pubkey_hex or '?'} note={b.note}")
            lines.append("")
        if self.pubkeys:
            lines.append(f"--- pubkeys ({len(self.pubkeys)}) ---")
            for p in self.pubkeys[:100]:
                lines.append(p)
            if len(self.pubkeys) > 100:
                lines.append(f"... +{len(self.pubkeys) - 100} more")
            lines.append("")
        if self.names:
            lines.append("--- name / labels ---")
            for n in self.names[:80]:
                lines.append(n)
            lines.append("")
        for n in self.hd_notes:
            lines.append(f"[hd] {n}")
        for n in self.other_notes:
            lines.append(f"[i] {n}")
        for e in self.errors:
            lines.append(f"[!] {e}")
        lines.append("=== end forensic report ===")
        return "\n".join(lines)


def _hex(b: bytes) -> str:
    return b.hex()


def _read_compact_size(data: bytes, off: int) -> tuple[int, int] | tuple[None, int]:
    if off >= len(data):
        return None, off
    ch = data[off]
    if ch < 253:
        return ch, off + 1
    if ch == 253 and off + 3 <= len(data):
        return struct.unpack_from("<H", data, off + 1)[0], off + 3
    if ch == 254 and off + 5 <= len(data):
        return struct.unpack_from("<I", data, off + 1)[0], off + 5
    if ch == 255 and off + 9 <= len(data):
        return struct.unpack_from("<Q", data, off + 1)[0], off + 9
    return None, off


def _read_vector(data: bytes, off: int, max_len: int = 512) -> tuple[bytes | None, int]:
    n, off2 = _read_compact_size(data, off)
    if n is None or n > max_len or off2 + n > len(data):
        return None, off
    return data[off2 : off2 + n], off2 + n


def _parse_cmaster_key(data: bytes, off: int) -> ExtractedBlob | None:
    """Deserialize CMasterKey at offset; return blob if vchCryptedKey looks usable."""
    start = off
    crypted, off = _read_vector(data, off, 128)
    if crypted is None:
        return None
    salt, off = _read_vector(data, off, 64)
    if salt is None or off + 8 > len(data):
        return None
    method, iters = struct.unpack_from("<II", data, off)
    off += 8
    other, off2 = _read_vector(data, off, 64)
    if other is None:
        other = b""
    note = f"CMasterKey parsed (+{off2 - start} bytes)"
    enc = crypted
    # TrueMkey wants 48-byte AES-CBC; take last 48 if longer, or pad-skip if 48
    if len(enc) >= 48:
        enc48 = enc[:48] if len(enc) == 48 else enc[-48:]
        if len(enc) != 48:
            note += f"; truncated/selected 48 of {len(enc)}"
    elif len(enc) == 32:
        # some dumps store raw; still export
        enc48 = enc + bytes(16)
        note += "; 32-byte crypted key padded for export"
    else:
        return None
    return ExtractedBlob(
        kind="mkey",
        enc_hex=_hex(enc48),
        offset=start,
        note=note,
        iterations=iters,
        salt_hex=_hex(salt),
        derivation_method=method,
    )


def _looks_pubkey(b: bytes) -> bool:
    return (len(b) == 33 and b[0] in (2, 3)) or (len(b) == 65 and b[0] == 4)


def _detect_format(data: bytes) -> str:
    if data[:16].startswith(b"SQLite format 3"):
        return "sqlite"
    if b"mkey" in data or b"ckey" in data or b"\x00\x05\x31\x62" in data[:8192]:
        return "bdb"
    return "unknown"


def _tag_counts(data: bytes) -> dict[str, int]:
    tags = (
        b"mkey", b"ckey", b"key", b"wkey", b"name", b"version", b"minversion",
        b"bestblock", b"defaultkey", b"pool", b"hdchain", b"hdpubkey",
        b"purpose", b"destdata", b"watchs", b"cscript", b"tx", b"flags",
    )
    out: dict[str, int] = {}
    for t in tags:
        c = data.count(bytes([len(t)]) + t)
        if not c:
            c = data.count(t)
        if c:
            out[t.decode()] = c
    return out


def _extract_pubkeys(data: bytes) -> list[str]:
    pubs: list[str] = []
    seen: set[str] = set()
    i, n = 0, len(data)
    while i < n - 33:
        b0 = data[i]
        if b0 in (2, 3):
            h = _hex(data[i : i + 33])
            if h not in seen:
                seen.add(h)
                pubs.append(h)
            i += 33
            continue
        if b0 == 4 and i + 65 <= n:
            h = _hex(data[i : i + 65])
            if h not in seen:
                seen.add(h)
                pubs.append(h)
            i += 65
            continue
        i += 1
    return pubs


def _parse_ckey_records(data: bytes, rep: WalletReport) -> None:
    """Find length-prefixed 'ckey' + pubkey key, then 48-byte value."""
    needle = b"\x04ckey"
    start = 0
    seen: set[str] = set()
    while True:
        idx = data.find(needle, start)
        if idx < 0:
            break
        rep.pieces.append(f"@{idx}: tag ckey")
        off = idx + len(needle)
        # pubkey may be compact-size vector or raw 33/65
        pub: bytes | None = None
        vec, off2 = _read_vector(data, off, 65)
        if vec and _looks_pubkey(vec):
            pub = vec
            off = off2
            rep.pieces.append(f"@{idx}: ckey pubkey (vector) {_hex(pub)[:20]}…")
        elif off + 33 <= len(data) and _looks_pubkey(data[off : off + 33]):
            pub = data[off : off + 33]
            off += 33
            rep.pieces.append(f"@{idx}: ckey pubkey (raw33)")
        elif off + 65 <= len(data) and _looks_pubkey(data[off : off + 65]):
            pub = data[off : off + 65]
            off += 65
            rep.pieces.append(f"@{idx}: ckey pubkey (raw65)")
        # scan nearby for 48-byte ciphertext (value often follows in page)
        region = data[off : off + 200]
        found = False
        for rel in range(0, max(0, len(region) - 48)):
            if region[rel] == 0x30:  # compact size 48
                blob = region[rel + 1 : rel + 49]
                if len(blob) == 48 and len(set(blob)) > 8:
                    hx = _hex(blob)
                    if hx not in seen:
                        seen.add(hx)
                        rep.ckeys.append(
                            ExtractedBlob(
                                kind="ckey",
                                enc_hex=hx,
                                pubkey_hex=_hex(pub) if pub else "",
                                offset=off + rel + 1,
                                note="ckey AES-CBC 48-byte secret",
                            )
                        )
                        rep.pieces.append(f"@{off + rel + 1}: ckey enc48 extracted")
                        found = True
                        break
            blob = region[rel : rel + 48]
            if len(set(blob)) > 12 and rel + 48 <= len(region):
                # weak heuristic fallback
                pass
        if not found and pub is not None:
            # still record pubkey pairing opportunity
            for rel in range(0, max(0, len(region) - 48)):
                blob = region[rel : rel + 48]
                if len(set(blob)) < 10:
                    continue
                hx = _hex(blob)
                if hx in seen:
                    continue
                # prefer high entropy
                if sum(blob) % 256 == 0 and len(set(blob)) < 16:
                    continue
                seen.add(hx)
                rep.ckeys.append(
                    ExtractedBlob(
                        kind="ckey",
                        enc_hex=hx,
                        pubkey_hex=_hex(pub),
                        offset=off + rel,
                        note="ckey candidate (heuristic near pubkey)",
                    )
                )
                rep.pieces.append(f"@{off + rel}: ckey candidate heuristic")
                break
        start = idx + 1


def _parse_mkey_records(data: bytes, rep: WalletReport) -> None:
    needle = b"\x04mkey"
    start = 0
    seen: set[str] = set()
    while True:
        idx = data.find(needle, start)
        if idx < 0:
            break
        rep.pieces.append(f"@{idx}: tag mkey")
        off = idx + len(needle)
        master_id = -1
        if off + 4 <= len(data):
            master_id = struct.unpack_from("<I", data, off)[0]
            if 0 < master_id < 10000:
                off += 4
                rep.pieces.append(f"@{idx}: mkey nID={master_id}")
            else:
                master_id = -1
        # try CMasterKey at several nearby offsets
        parsed = None
        for delta in range(0, 32):
            parsed = _parse_cmaster_key(data, off + delta)
            if parsed:
                parsed.master_id = master_id
                parsed.offset = off + delta
                break
        if parsed and parsed.enc_hex not in seen:
            seen.add(parsed.enc_hex)
            rep.mkeys.append(parsed)
            rep.pieces.append(
                f"@{parsed.offset}: CMasterKey enc48 iters={parsed.iterations} salt={parsed.salt_hex[:16]}…"
            )
        else:
            # fallback 48-byte near tag
            region = data[off : off + 256]
            for rel in range(0, max(0, len(region) - 48)):
                if region[rel] == 0x30:
                    blob = region[rel + 1 : rel + 49]
                    if len(blob) == 48 and len(set(blob)) > 8:
                        hx = _hex(blob)
                        if hx not in seen:
                            seen.add(hx)
                            rep.mkeys.append(
                                ExtractedBlob(
                                    kind="mkey",
                                    enc_hex=hx,
                                    offset=off + rel + 1,
                                    master_id=master_id,
                                    note="mkey 48-byte fallback (no full CMasterKey parse)",
                                )
                            )
                            rep.pieces.append(f"@{off + rel + 1}: mkey enc48 fallback")
                        break
        start = idx + 1


def _parse_names_versions(data: bytes, rep: WalletReport) -> None:
    for m in re.finditer(rb"name.{0,6}([\x20-\x7e]{4,90})", data):
        s = m.group(1).decode("ascii", errors="ignore").strip()
        if s and s not in rep.names:
            rep.names.append(s)
            rep.pieces.append(f"@{m.start()}: name '{s[:60]}'")
    for m in re.finditer(rb"\x07version", data):
        off = m.end()
        if off + 4 <= len(data):
            v = struct.unpack_from("<I", data, off)[0]
            if 1 <= v <= 200000 and v not in rep.versions:
                rep.versions.append(v)
                rep.pieces.append(f"@{off}: version={v}")
    if b"hdchain" in data:
        rep.hd_notes.append("hdchain record present (HD wallet)")
        rep.pieces.append("hdchain tag present")
    if b"\x04pool" in data or b"pool" in data:
        rep.pieces.append("keypool records present")


def inspect_wallet_dat(path: str | Path) -> WalletReport:
    p = Path(path)
    rep = WalletReport(path=str(p.resolve()))
    if not p.is_file():
        rep.errors.append("file not found")
        return rep
    data = p.read_bytes()
    rep.size = len(data)
    rep.sha256 = hashlib.sha256(data).hexdigest()
    rep.pieces.append(f"loaded {rep.size} bytes sha256={rep.sha256[:16]}…")
    if rep.size < 64:
        rep.errors.append("file too small")
        return rep

    rep.format = _detect_format(data)
    rep.pieces.append(f"format detect → {rep.format}")
    if rep.format == "sqlite":
        rep.other_notes.append(
            "SQLite descriptor wallet — legacy mkey/ckey may be absent. "
            "Use Bitcoin Core `sqlite3` / dumpwallet for descriptors."
        )
    rep.tags_found = _tag_counts(data)
    rep.pieces.append(f"tag census → {rep.tags_found}")

    _parse_mkey_records(data, rep)
    _parse_ckey_records(data, rep)
    _parse_names_versions(data, rep)
    rep.pubkeys = _extract_pubkeys(data)
    for b in rep.ckeys:
        if b.pubkey_hex and b.pubkey_hex not in rep.pubkeys:
            rep.pubkeys.insert(0, b.pubkey_hex)

    # plain "key" records (unencrypted) — flag only, do not dump priv hex into report by default
    kn = data.count(b"\x03key")
    if kn:
        rep.plain_keys.append(
            ExtractedBlob(kind="key", note=f"{kn} length-prefixed 'key' tags (possible unencrypted privs)")
        )
        rep.pieces.append(f"plain key tags ×{kn} (inspect offline; not auto-exported as WIF)")

    if not rep.mkeys and not rep.ckeys:
        rep.other_notes.append("No mkey/ckey AES blobs recovered — empty, unencrypted, or descriptor wallet.")
    if rep.ckeys and not any(c.pubkey_hex for c in rep.ckeys):
        rep.other_notes.append("ckeys without pubs — AES search OK; WIF post-hit needs pubkeys.")
    rep.pieces.append(
        f"done: mkey={len(rep.mkeys)} ckey={len(rep.ckeys)} pubs={len(rep.pubkeys)} names={len(rep.names)}"
    )
    return rep


def export_for_truemkey(report: WalletReport, out_dir: str | Path) -> dict[str, str]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    mkey_path = out / "mkeys_from_wallet.txt"
    ckey_path = out / "ckeys_from_wallet.txt"
    pub_path = out / "pubkeys_from_wallet.txt"
    report_path = out / "wallet_forensic_report.txt"
    meta_path = out / "mkey_meta.txt"

    mkey_path.write_text("\n".join(b.enc_hex for b in report.mkeys) + ("\n" if report.mkeys else ""), encoding="utf-8")
    c_lines = []
    for b in report.ckeys:
        c_lines.append(f"{b.enc_hex} {b.pubkey_hex}".rstrip())
    ckey_path.write_text("\n".join(c_lines) + ("\n" if c_lines else ""), encoding="utf-8")
    pubs = list(dict.fromkeys(report.pubkeys))
    pub_path.write_text("\n".join(pubs) + ("\n" if pubs else ""), encoding="utf-8")
    report_path.write_text(report.summary_text(), encoding="utf-8")
    meta_lines = []
    for b in report.mkeys:
        meta_lines.append(
            f"id={b.master_id} iters={b.iterations} method={b.derivation_method} "
            f"salt={b.salt_hex} enc={b.enc_hex}"
        )
    meta_path.write_text("\n".join(meta_lines) + ("\n" if meta_lines else ""), encoding="utf-8")
    return {
        "mkeys": str(mkey_path),
        "ckeys": str(ckey_path),
        "pubkeys": str(pub_path),
        "report": str(report_path),
        "meta": str(meta_path),
    }
