"""Chain RPC catalog — implanted from chain-dev-download-rpc.py (chainid.network).

Downloads public EVM/chain RPC endpoints into tools/chains/ for node balance checks
and multi-coin research. Lawful: public endpoints only, no private-key scraping.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from pathlib import Path

CHAINS_JSON_URL = "https://chainid.network/chains.json"
USER_AGENT = "TrueNexus-ChainRPC/1.0 (+https://t.me/TrueScent)"

# Main coins we always surface first (name substrings / chainIds)
MAIN_CHAIN_IDS = {
    1: "ethereum",
    56: "bnb_smart_chain",
    137: "polygon",
    42161: "arbitrum_one",
    10: "optimism",
    43114: "avalanche_c",
    250: "fantom",
    8453: "base",
    100: "gnosis",
    324: "zksync_era",
    59144: "linea",
    534352: "scroll",
    25: "cronos",
    1284: "moonbeam",
    42220: "celo",
    66: "okx_okt",
    321: "kcc",
    128: "heco",
    1088: "metis",
    1101: "polygon_zkevm",
    81457: "blast",
    5000: "mantle",
    204: "opbnb",
    592: "astar",
    288: "boba",
    1313161554: "aurora",
    2222: "kava_evm",
    42262: "oasis_emerald",
    8217: "klaytn",
    57: "syscoin",
    61: "ethereum_classic",
    3: "ropsten_legacy",
    5: "goerli_legacy",
    11155111: "sepolia",
}


def default_chains_dir(root: Path | None = None) -> Path:
    base = root or Path(__file__).resolve().parents[1]
    return base / "tools" / "chains"


def fetch_chains(timeout: float = 60.0) -> list[dict]:
    req = urllib.request.Request(CHAINS_JSON_URL, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    data = json.loads(raw.decode("utf-8"))
    if not isinstance(data, list):
        raise ValueError("unexpected chains.json shape")
    return data


def save_rpcs_to_files(chains: list[dict], out_dir: Path | None = None) -> dict[str, int]:
    """Write one .txt per chain with RPC URLs. Returns {filename: rpc_count}."""
    out = out_dir or default_chains_dir()
    out.mkdir(parents=True, exist_ok=True)
    written: dict[str, int] = {}
    index: list[dict] = []
    for chain in chains:
        name = str(chain.get("name") or "unknown").lower().replace(" ", "_")
        name = "".join(c if c.isalnum() or c in "-_" else "_" for c in name)[:80]
        chain_id = chain.get("chainId")
        rpcs = [r for r in (chain.get("rpc") or []) if isinstance(r, str) and r.startswith("http")]
        # strip template vars that need keys
        rpcs = [r for r in rpcs if "${" not in r]
        if not rpcs:
            continue
        fname = f"{name}.txt"
        if chain_id is not None:
            fname = f"{chain_id}_{name}.txt"
        path = out / fname
        path.write_text("\n".join(rpcs) + "\n", encoding="utf-8")
        written[fname] = len(rpcs)
        index.append(
            {
                "file": fname,
                "name": chain.get("name"),
                "chainId": chain_id,
                "shortName": chain.get("shortName"),
                "nativeCurrency": chain.get("nativeCurrency"),
                "rpc_count": len(rpcs),
                "explorers": chain.get("explorers"),
            }
        )
    (out / "index.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    # convenience: main coins bundle
    mains = []
    for cid, label in MAIN_CHAIN_IDS.items():
        for row in index:
            if row.get("chainId") == cid:
                mains.append(row)
                break
    (out / "main_coins.json").write_text(json.dumps(mains, indent=2), encoding="utf-8")
    return written


def sync_chain_rpcs(out_dir: Path | None = None) -> str:
    chains = fetch_chains()
    written = save_rpcs_to_files(chains, out_dir)
    out = out_dir or default_chains_dir()
    return f"Synced {len(written)} chain RPC files → {out} ({sum(written.values())} endpoints)"


def list_main_rpcs(out_dir: Path | None = None) -> list[dict]:
    out = out_dir or default_chains_dir()
    p = out / "main_coins.json"
    if not p.exists():
        return []
    return json.loads(p.read_text(encoding="utf-8"))
