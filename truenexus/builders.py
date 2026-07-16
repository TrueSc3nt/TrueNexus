"""CLI command builders for TrueCollider and TrueMkeyCollider."""

from __future__ import annotations

from dataclasses import dataclass, field

from truenexus.ideas_catalog import (
    address_sub_labels,
    bsgs_labels,
    filter_labels,
    mode_labels,
    mnemonic_strategy_labels,
    mnemonic_submode_labels,
    pattern_labels,
    rmd160_sub_labels,
    weakrng_labels,
)

MODES_LIVE = [
    "address", "rmd160", "xpoint", "bsgs", "kangaroo", "vanity",
    "minikeys", "mnemonic", "poetry", "brainwallet", "pubkey2addr",
]

MODES_ALL = mode_labels()
SEARCH_PATTERNS = pattern_labels()
BSGS_STRATEGIES = bsgs_labels()
MNEMONIC_SUBMODES = mnemonic_submode_labels()
MNEMONIC_STRATEGIES = mnemonic_strategy_labels()
WEAKRNG_SUBMODES = weakrng_labels()
ADDRESS_SUBMODES = address_sub_labels()
RMD160_SUBMODES = rmd160_sub_labels()
FILTER_STRATS = filter_labels()

COINS = ["btc", "eth", "ltc", "doge", "xrp", "sol", "bch", "btg", "etc", "troot", "all", "auto"]
LOOK = ["compress", "uncompress", "both"]
LANGS = [
    "english", "spanish", "french", "italian", "czech", "portuguese",
    "japanese", "korean", "chinese_simplified", "chinese_traditional", "all",
]
GPU = ["none", "cuda", "opencl"]
VECTOR = ["auto", "none", "sse", "avx", "avx2", "avx512"]
PATH_PACKS = [
    "paths-btc (research)", "paths-eth (research)", "paths-electrum (research)",
    "paths-custom (research)", "account-sweep (research)", "multisig-cosigner (research)",
]


def _live_token(value: str) -> str:
    return value.split(" (")[0].strip()


def is_research(value: str) -> bool:
    v = value.lower()
    return "(research)" in v or _live_token(value) not in MODES_LIVE and value in (
        "hybrid-dl", "gaudry", "shadow160", "weakrng", "CreateAccountWithSeed",
    ) or _live_token(value) not in MODES_LIVE and any(
        _live_token(value) == m for m in [
            "hybrid-dl", "gaudry", "shadow160", "weakrng", "CreateAccountWithSeed",
            "hilbert", "sobol", "density-map", "grumpy", "interleave", "orbit",
            "residue", "dual-range", "nested", "fractal", "async-resolve",
            "multi-target", "negmap", "handoff", "gravity-giant", "chaos-giant",
            "sobol-giant", "freeze-table", "compact-dp", "mask", "model",
            "lastword", "milksad", "electrum-v2", "cascade", "fuse16",
        ]
    )


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
    mnemonic_submode: str = "random"
    mnemonic_strategy: str = "checksum-first (research)"
    seed_mask: str = ""
    passphrase_file: str = ""
    model_file: str = ""
    path_pack: str = "paths-btc (research)"
    weakrng_sub: str = "milksad (research)"
    address_sub: str = "default"
    rmd160_sub: str = "exact"
    filter_strategy: str = "default fuse"
    vector: str = "auto"
    stride: str = ""
    minikey_base: str = ""
    timestamp_window: str = ""
    residue_mr: str = ""
    collision_bits: str = "48"
    dual_target_file: str = ""
    extra_args: str = ""
    research_notes: list[str] = field(default_factory=list)

    def build(self) -> tuple[str, list[str]]:
        warns: list[str] = []
        mode_raw = self.mode
        mode = _live_token(mode_raw)

        live_fallback = {
            "hybrid-dl": "bsgs",
            "gaudry": "kangaroo",
            "shadow160": "rmd160",
            "weakrng": "address",
            "CreateAccountWithSeed": "address",
        }
        if mode not in MODES_LIVE:
            fb = live_fallback.get(mode, "address")
            warns.append(
                f"Mode '{mode_raw}' is research. Launch uses live mode '{fb}'. "
                "Preview keeps your research intent annotated."
            )
            live_mode = fb
        else:
            live_mode = mode

        parts = [f'"{self.exe}"', "-m", live_mode]

        if self.target_file:
            parts += ["-f", f'"{self.target_file}"']
        if live_mode in ("address", "rmd160", "vanity", "pubkey2addr"):
            parts += ["-c", self.coin, "-l", self.look]
        if self.bits:
            parts += ["-b", self.bits]
        if self.range_start:
            rng = self.range_start
            if self.range_end:
                rng = f"{self.range_start}:{self.range_end}"
            parts += ["-r", rng]
        if self.timestamp_window:
            # -T is unix timestamp in TrueCollider; accept start or start:end note
            ts = self.timestamp_window.split(":")[0].strip()
            if ts.isdigit():
                parts += ["-T", ts]
                warns.append("Timestamp window end bound is research UI; live -T uses center timestamp.")

        pattern = _live_token(self.search_pattern)
        live_patterns = {"sequential", "random", "chaos", "gravity", "spiral", "reverse", "auto", "rseq"}
        if pattern not in live_patterns:
            warns.append(f"Pattern '{self.search_pattern}' is research — using 'chaos'.")
            pattern = "chaos"
        if pattern and pattern != "sequential":
            if pattern == "rseq":
                parts.append("-rs")
            else:
                parts += ["-x", pattern]

        if live_mode == "bsgs":
            bstrat = _live_token(self.bsgs_strategy)
            live_b = {"sequential", "backward", "both", "random", "dance"}
            if bstrat not in live_b:
                warns.append(f"BSGS strategy '{self.bsgs_strategy}' is research — using 'random'.")
                bstrat = "random"
            parts += ["-B", bstrat]
            if self.k_factor:
                parts += ["-k", self.k_factor]
            if self.n_table:
                parts += ["-n", self.n_table]
            if self.save_bloom:
                parts.append("-S")
            if self.residue_mr:
                warns.append(f"Residue M:R '{self.residue_mr}' is research (Gaudry/ResidueHerd).")

        if live_mode == "vanity" and self.vanity:
            parts += ["-v", self.vanity]
        if live_mode == "minikeys" and self.minikey_base:
            parts += ["-C", self.minikey_base]

        if live_mode == "mnemonic":
            sub = _live_token(self.mnemonic_submode)
            if sub != "random":
                warns.append(
                    f"Mnemonic submode '{self.mnemonic_submode}' + strategy "
                    f"'{self.mnemonic_strategy}' are research. Live binary runs random BIP-39; "
                    "mask/pass/model fields are preserved in the annotation."
                )
            if self.mnemonic_words:
                parts += ["-w", self.mnemonic_words]
            if self.mnemonic_lang:
                parts += ["-L", self.mnemonic_lang]
            if self.mnemonic_eth:
                parts.append("-W")
            if self.derivation_depth:
                parts += ["-D", self.derivation_depth]
            if self.seed_mask:
                warns.append(f"Seed mask stored for future kernel: {self.seed_mask[:80]}")
            if self.passphrase_file:
                warns.append(f"Passphrase file queued: {self.passphrase_file}")
            if self.model_file:
                warns.append(f"Model constraints queued: {self.model_file}")
            if self.path_pack:
                warns.append(f"Path pack intent: {self.path_pack}")
            if self.dual_target_file:
                warns.append(f"DualTarget anchor file: {self.dual_target_file}")

        if self.derivation_path and live_mode in ("address", "rmd160"):
            parts += ["-p", f'"{self.derivation_path}"']
            if self.derivation_depth:
                parts += ["-D", self.derivation_depth]

        if live_mode == "rmd160":
            rsub = _live_token(self.rmd160_sub)
            if rsub != "exact":
                warns.append(f"RMD160 submode '{self.rmd160_sub}' is research.")
            if rsub == "shadow160" or mode == "shadow160":
                warns.append(f"Shadow160 collision bits intent: {self.collision_bits}")

        if mode == "weakrng" or live_mode == "address" and "weakrng" in mode_raw:
            warns.append(f"CrystalPRNG / weakrng submode: {self.weakrng_sub}")

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

        fstrat = _live_token(self.filter_strategy)
        if fstrat not in ("default fuse", "default", "bloom-classic"):
            warns.append(f"Filter strategy '{self.filter_strategy}' is research — binary uses default fuse.")
        if self.address_sub and _live_token(self.address_sub) not in ("default", "hd-fanout"):
            warns.append(f"Address submode '{self.address_sub}' is research.")

        if self.extra_args.strip():
            parts.append(self.extra_args.strip())

        cmd = " ".join(parts)
        intent = (
            f" REM research-intent: mode={mode_raw} pattern={self.search_pattern} "
            f"bsgs={self.bsgs_strategy} mnemonic={self.mnemonic_submode}/{self.mnemonic_strategy} "
            f"weakrng={self.weakrng_sub} addr={self.address_sub} rmd={self.rmd160_sub} "
            f"filter={self.filter_strategy} pathpack={self.path_pack}"
        )
        if warns:
            cmd += intent
        return cmd, warns


@dataclass
class MkeyConfig:
    exe: str = "TrueMkeyCollider.exe"
    ckeys: str = ""
    mkeys: str = ""
    pubkeys: str = ""
    mode: str = "random"
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
        "-T": "Unix timestamp window center for timestamp-key hunts.",
        "-y": "Dry-run config dump.",
        "-q": "Quiet stats.",
        "-ckeys": "TrueMkeyCollider encrypted ckey file.",
        "-mckey": "TrueMkeyCollider encrypted mkey file.",
        "--partial": "Known AES key prefix (partial-key GPU mode).",
        "--selftest": "TrueMkeyCollider PoC host+GPU+WIF pipeline.",
    }
    return docs.get(flag, "See README / tool -h for details.")
