"""Address Watch — lawful balance / last-tx alerts only.

No auto-withdraw. No RBF race. No key scraping.
Polls public explorers for addresses you enter.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Callable

MEMPOOL_ADDRESS = "https://mempool.space/api/address/{addr}"
MEMPOOL_TXS = "https://mempool.space/api/address/{addr}/txs"
BLOCKSTREAM_ADDRESS = "https://blockstream.info/api/address/{addr}"

USER_AGENT = "TrueNexus-AddressWatch/1.0 (+https://t.me/TrueScent; alert-only)"


@dataclass
class WatchSnapshot:
    address: str
    label: str = ""
    chain_sats: int = 0
    mempool_sats: int = 0
    funded_txo_count: int = 0
    spent_txo_count: int = 0
    last_txid: str = ""
    ok: bool = True
    error: str = ""
    source: str = ""

    @property
    def total_sats(self) -> int:
        return self.chain_sats + self.mempool_sats

    @property
    def total_btc(self) -> float:
        return self.total_sats / 1e8

    def summary_line(self) -> str:
        tag = f" ({self.label})" if self.label else ""
        if not self.ok:
            return f"[WATCH ERR] {self.address}{tag}: {self.error}"
        tx = self.last_txid[:16] + "…" if len(self.last_txid) > 16 else self.last_txid
        return (
            f"[WATCH] {self.address}{tag}  "
            f"{self.total_btc:.8f} BTC  "
            f"(chain={self.chain_sats} mempool={self.mempool_sats} sats)  "
            f"txs={self.funded_txo_count}/{self.spent_txo_count}  "
            f"last={tx or '—'}  via {self.source}"
        )


@dataclass
class WatchBook:
    """In-memory watch list with last-seen snapshots for change detection."""

    entries: dict[str, WatchSnapshot] = field(default_factory=dict)

    def remember(self, snap: WatchSnapshot) -> tuple[bool, str]:
        """Store snapshot. Returns (changed, human message)."""
        prev = self.entries.get(snap.address)
        self.entries[snap.address] = snap
        if not snap.ok:
            return False, snap.summary_line()
        if prev is None or not prev.ok:
            return True, "NEW " + snap.summary_line()
        changed = (
            prev.total_sats != snap.total_sats
            or prev.last_txid != snap.last_txid
            or prev.funded_txo_count != snap.funded_txo_count
            or prev.spent_txo_count != snap.spent_txo_count
        )
        if changed:
            delta = snap.total_sats - prev.total_sats
            sign = "+" if delta >= 0 else ""
            return True, f"CHANGE {sign}{delta} sats  " + snap.summary_line()
        return False, snap.summary_line()


def _http_get_json(url: str, timeout: float = 20.0) -> dict | list:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return json.loads(raw)


def fetch_mempool_space(address: str, label: str = "") -> WatchSnapshot:
    snap = WatchSnapshot(address=address.strip(), label=label, source="mempool.space")
    try:
        data = _http_get_json(MEMPOOL_ADDRESS.format(addr=snap.address))
        chain = data.get("chain_stats") or {}
        mem = data.get("mempool_stats") or {}
        snap.chain_sats = int(chain.get("funded_txo_sum", 0)) - int(chain.get("spent_txo_sum", 0))
        snap.mempool_sats = int(mem.get("funded_txo_sum", 0)) - int(mem.get("spent_txo_sum", 0))
        snap.funded_txo_count = int(chain.get("funded_txo_count", 0)) + int(mem.get("funded_txo_count", 0))
        snap.spent_txo_count = int(chain.get("spent_txo_count", 0)) + int(mem.get("spent_txo_count", 0))
        try:
            txs = _http_get_json(MEMPOOL_TXS.format(addr=snap.address))
            if isinstance(txs, list) and txs:
                snap.last_txid = str(txs[0].get("txid") or "")
        except Exception:
            pass
        snap.ok = True
    except urllib.error.HTTPError as e:
        snap.ok = False
        snap.error = f"HTTP {e.code}"
    except Exception as e:
        snap.ok = False
        snap.error = str(e)
    return snap


def fetch_blockstream(address: str, label: str = "") -> WatchSnapshot:
    snap = WatchSnapshot(address=address.strip(), label=label, source="blockstream.info")
    try:
        data = _http_get_json(BLOCKSTREAM_ADDRESS.format(addr=snap.address))
        chain = data.get("chain_stats") or {}
        mem = data.get("mempool_stats") or {}
        snap.chain_sats = int(chain.get("funded_txo_sum", 0)) - int(chain.get("spent_txo_sum", 0))
        snap.mempool_sats = int(mem.get("funded_txo_sum", 0)) - int(mem.get("spent_txo_sum", 0))
        snap.funded_txo_count = int(chain.get("funded_txo_count", 0))
        snap.spent_txo_count = int(chain.get("spent_txo_count", 0))
        snap.ok = True
    except urllib.error.HTTPError as e:
        snap.ok = False
        snap.error = f"HTTP {e.code}"
    except Exception as e:
        snap.ok = False
        snap.error = str(e)
    return snap


def fetch_address(address: str, label: str = "", prefer: str = "mempool") -> WatchSnapshot:
    """Try preferred explorer, fall back to the other."""
    addr = (address or "").strip()
    if not addr:
        return WatchSnapshot(address="", label=label, ok=False, error="empty address")
    primary = fetch_mempool_space if prefer != "blockstream" else fetch_blockstream
    secondary = fetch_blockstream if prefer != "blockstream" else fetch_mempool_space
    snap = primary(addr, label)
    if snap.ok:
        return snap
    alt = secondary(addr, label)
    if alt.ok:
        return alt
    snap.error = f"{snap.error}; fallback: {alt.error}"
    return snap


def parse_watch_lines(text: str) -> list[tuple[str, str]]:
    """Parse 'address' or 'address | label' lines. Skips blanks and # comments."""
    out: list[tuple[str, str]] = []
    for raw in (text or "").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "|" in line:
            addr, label = line.split("|", 1)
            out.append((addr.strip(), label.strip()))
        else:
            parts = line.split(None, 1)
            if len(parts) == 1:
                out.append((parts[0], ""))
            else:
                out.append((parts[0], parts[1]))
    return out


AlertFn = Callable[[str], None]


def poll_once(
    lines: str,
    book: WatchBook,
    *,
    prefer: str = "mempool",
    on_line: AlertFn | None = None,
    changes_only: bool = False,
) -> list[str]:
    """Poll all addresses once. Returns log lines. Calls on_line for each emitted line."""
    messages: list[str] = []
    for addr, label in parse_watch_lines(lines):
        snap = fetch_address(addr, label, prefer=prefer)
        changed, msg = book.remember(snap)
        if changes_only and not changed and snap.ok:
            continue
        messages.append(msg)
        if on_line:
            on_line(msg)
    return messages
