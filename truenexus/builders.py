"""CLI command builders for TrueCollider and TrueMkeyCollider."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


# ── TrueCollider option catalogs (shipped + research ideas) ──────────────

MODES_LIVE = [
    "address", "rmd160", "xpoint", "bsgs", "kangaroo", "vanity",
    "minikeys", "mnemonic", "poetry", "brainwallet", "pubkey2addr",
]

MODES_RESEARCH = [
    "hybrid-dl (HerdHandoff)", "gaudry (MultiDim-DL)", "shadow160",
    "weakrng", "CreateAccountWithSeed",
]

SEARCH_PATTERNS = [
    "sequential", "random", "chaos", "gravity", "spiral", "reverse", "auto",
    "hilbert (research)", "sobol (research)", "rseq",
]

BSGS_STRATEGIES = [
    "sequential", "backward", "both", "random", "dance",
    "grumpy (research)", "interleave (research)", "orbit (research)",
    "residue (research)", "handoff (research)", "negmap (research)",
    "nested (research)", "async-resolve (research)", "multi-target (research)",
    "gravity-giant (research)", "chaos-giant (research)", "sobol-giant (research)",
]

MNEMONIC_SUBMODES = [
    "random (live)", "mask (research)", "model (research)", "lastword (research)",
    "prefix-word (research)", "typo (research)", "permute (research)",
    "pass-dict (research)", "pass-mask (research)", "pass-rules (research)",
    "electrum-v1 (research)", "electrum-v2 (research)", "slip39 (research)",
    "aezeed (research)", "bip85 (research)", "milksad (research)",
    "lattice (research)", "checksum-prism (research)",
]

COINS = ["btc", "eth", "ltc", "doge", "xrp", "sol", "bch", "btg", "etc", "troot", "all", "auto"]
LOOK = ["compress", "uncompress", "both"]
LANGS = [
    "english", "spanish", "french", "italian", "czech", "portuguese",
    "japanese", "korean", "chinese_simplified", "chinese_traditional", "all",
]
GPU = ["none", "cuda", "opencl"]
VECTOR = ["auto", "none", "sse", "avx", "avx2", "avx512"]
FILTER_STRATS = ["default fuse", "cascade (research)", "bloom-classic", "fuse16 (research)"]


def _live_token(value: str) -> str:
    """Strip research annotations for CLI emission."""
    return value.split(" (")[0].strip()


def is_research(value: str) -> bool:
    return "(research)" in value.lower() or value in MODES_RESEARCH


@dataclass
class ColliderConfig:
    exe: str = "keyhunt.exe"
    mode: str = "address"
    target_file: str = ""
    coin: str = "btc"
    look: str = "compress"
    bits: str = ""
    range_start: str = ""
    range_end: str = ""
    search_pattern: str = "chaos"
    bsgs_strategy: str = "random"
    threads: str = "8"
    endomorphism: bool = True
    gpu: str = "none"
    memory: str = "auto"
    k_factor: str = "auto"
    n_table: str = ""
    save_bloom: bool = False
    quiet: bool = True
    stats: str = "10"
    dry_run: bool = False
    vanity: str = ""
    mnemonic_words: str = "12"
    mnemonic_lang: str = "english"
    mnemonic_eth: bool = False
    derivation_path: str = ""
    derivation_depth: str = "1"
    mnemonic_submode: str = "random (live)"
    seed_mask: str = ""
    passphrase_file: str = ""
    filter_strategy: str = "default fuse"
    vector: str = "auto"
    stride: str = ""
    minikey_base: str = ""
    extra_args: str = ""
    research_notes: list[str] = field(default_factory=list)

    def build(self) -> tuple[str, list[str]]:
        """Return (command_string, research_warnings)."""
        warns: list[str] = []
        mode = _live_token(self.mode)
        if is_research(self.mode) or mode not in MODES_LIVE:
            warns.append(
                f"Mode '{self.mode}' is a research/planned mode. "
                "Falling back to nearest live mode 'address' for launch — "
                "command preview keeps your selection annotated."
            )
            live_mode = "address"
        else:
            live_mode = mode

        parts = [f'"{self.exe}"', "-m", live_mode]

        if self.target_file:
            parts += ["-f", f'"{self.target_file}"']
        if live_mode in ("address", "rmd160", "vanity", "pubkey2addr"):
            parts += ["-c", self.coin]
            parts += ["-l", self.look]
        if self.bits:
            parts += ["-b", self.bits]
        if self.range_start:
            rng = self.range_start
            if self.range_end:
                rng = f"{self.range_start}:{self.range_end}"
            parts += ["-r", rng]

        pattern = _live_token(self.search_pattern)
        if is_research(self.search_pattern):
            warns.append(f"Search pattern '{self.search_pattern}' is research — using 'chaos'.")
            pattern = "chaos"
        if pattern and pattern != "sequential":
            parts += ["-x", pattern]

        if live_mode == "bsgs":
            bstrat = _live_token(self.bsgs_strategy)
            if is_research(self.bsgs_strategy):
                warns.append(f"BSGS strategy '{self.bsgs_strategy}' is research — using 'random'.")
                bstrat = "random"
            parts += ["-B", bstrat]
            if self.k_factor:
                parts += ["-k", self.k_factor]
            if self.n_table:
                parts += ["-n", self.n_table]
            if self.save_bloom:
                parts.append("-S")

        if live_mode == "vanity" and self.vanity:
            parts += ["-v", self.vanity]
        if live_mode == "minikeys" and self.minikey_base:
            parts += ["-C", self.minikey_base]

        if live_mode == "mnemonic":
            sub = self.mnemonic_submode
            if is_research(sub) or not sub.startswith("random"):
                warns.append(
                    f"Mnemonic submode '{sub}' is planned research UI. "
                    "Live binary currently runs random BIP-39; mask/pass fields are saved for future kernels."
                )
            if self.mnemonic_words:
                parts += ["-w", self.mnemonic_words]
            if self.mnemonic_lang:
                parts += ["-L", self.mnemonic_lang]
            if self.mnemonic_eth:
                parts.append("-W")
            if self.derivation_depth:
                parts += ["-D", self.derivation_depth]

        if self.derivation_path and live_mode in ("address", "rmd160"):
            parts += ["-p", f'"{self.derivation_path}"']
            if self.derivation_depth:
                parts += ["-D", self.derivation_depth]

        if self.endomorphism and live_mode in ("address", "rmd160", "vanity"):
            parts.append("-e")
        if self.threads:
            parts += ["-t", self.threads]
        if self.gpu and self.gpu != "none":
            parts += ["-U", self.gpu]
        if self.memory:
            parts += ["-M", self.memory]
        if self.vector and self.vector != "auto":
            parts += ["-A", self.vector]
        if self.stride:
            parts += ["-I", self.stride]
        if self.quiet:
            parts.append("-q")
        if self.stats:
            parts += ["-s", self.stats]
        if self.dry_run:
            parts.append("-y")
        if is_research(self.filter_strategy):
            warns.append(f"Filter strategy '{self.filter_strategy}' is research — binary uses default fuse.")
        if self.extra_args.strip():
            parts.append(self.extra_args.strip())

        # Annotate research intent in comment form for copy/paste notebooks
        cmd = " ".join(parts)
        if self.mode != live_mode or is_research(self.mnemonic_submode):
            cmd += f"  REM research-intent: mode={self.mode} mnemonic={self.mnemonic_submode}"
        return cmd, warns


@dataclass
class MkeyConfig:
    exe: str = "TrueMkeyCollider.exe"
    ckeys: str = ""
    mkeys: str = ""
    pubkeys: str = ""
    mode: str = "random"  # random / sequential / mixed
    start_key: str = ""
    device: str = "0"
    grid: str = "256,256"
    streams: str = "4"
    memory: str = "auto"
    limit: str = ""
    partial: str = ""
    try_key: str = ""
    out_file: str = "key_found.txt"
    found_file: str = "FOUND_WALLET.txt"
    selftest: bool = False
    extra_args: str = ""

    def build(self) -> str:
        if self.selftest:
            return f'"{self.exe}" --selftest'
        parts = [f'"{self.exe}"']
        if self.ckeys:
            parts += ["-ckeys", f'"{self.ckeys}"']
        if self.mkeys:
            parts += ["-mckey", f'"{self.mkeys}"']
        if self.pubkeys:
            parts += ["-pubkeys", f'"{self.pubkeys}"']
        if self.mode == "random":
            parts.append("-r")
        elif self.mode == "sequential":
            parts.append("-q")
        elif self.mode == "mixed":
            parts.append("-rs")
        if self.start_key:
            parts += ["-s", self.start_key]
        if self.device:
            parts += ["-d", self.device]
        if self.grid:
            parts += ["-g", self.grid]
        if self.streams:
            parts += ["-streams", self.streams]
        if self.memory:
            parts += ["-M", self.memory]
        if self.limit:
            parts += ["-n", self.limit]
        if self.partial:
            parts += ["--partial", self.partial]
        if self.try_key:
            parts += ["--try", self.try_key]
        if self.out_file:
            parts += ["-o", f'"{self.out_file}"']
        if self.found_file:
            parts += ["--found", f'"{self.found_file}"']
        if self.extra_args.strip():
            parts.append(self.extra_args.strip())
        return " ".join(parts)


def explain_flag(flag: str) -> str:
    docs = {
        "-m": "Search mode: address, rmd160, bsgs, kangaroo, mnemonic, …",
        "-f": "Target file (addresses, hash160, pubkeys).",
        "-c": "Coin / address encoding family.",
        "-b": "Bit length of the puzzle / key range.",
        "-r": "Hex range START:END.",
        "-x": "Key ordering pattern (chaos/gravity/spiral/auto/…).",
        "-B": "BSGS giant-step strategy.",
        "-k": "BSGS K factor (baby table multiplier). Use auto if unsure.",
        "-S": "Save/load BSGS bloom/fuse tables to disk.",
        "-e": "GLV endomorphism (~3× coverage on secp256k1 grind modes).",
        "-U": "GPU backend: cuda or opencl.",
        "-M": "Memory / VRAM budget.",
        "-t": "CPU threads.",
        "-w": "Mnemonic or brainwallet word count.",
        "-L": "BIP-39 language (or all).",
        "-W": "ETH keccak address checks in mnemonic mode.",
        "-D": "Derivation index depth.",
        "-p": "BIP-32 derivation path (address/rmd160).",
        "-v": "Vanity prefix.",
        "-y": "Dry-run config dump.",
        "-q": "Quiet stats.",
        "-ckeys": "TrueMkeyCollider encrypted ckey file.",
        "-mckey": "TrueMkeyCollider encrypted mkey file.",
        "--partial": "Known AES key prefix (partial-key GPU mode).",
        "--selftest": "TrueMkeyCollider PoC host+GPU+WIF pipeline.",
    }
    return docs.get(flag, "See README / tool -h for details.")
