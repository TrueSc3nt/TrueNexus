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
    recipe_labels,
    rmd160_sub_labels,
    weakrng_labels,
)

MODES_LIVE = [
    "address", "rmd160", "xpoint", "bsgs", "kangaroo", "vanity",
    "minikeys", "mnemonic", "poetry", "brainwallet", "pubkey2addr",
    "shadow160", "weakrng", "hybrid-dl", "gaudry",
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
    "prism",
]
GPU = ["none", "cuda", "opencl", "both"]
VECTOR = ["auto", "none", "sse", "avx", "avx2", "avx512"]
PATH_PACKS = [
    "btc-std", "paths-btc", "eth", "paths-eth", "ledger-eth",
    "electrum", "paths-electrum", "custom", "account-sweep",
    "gap-limit", "multicoin", "all-coins",
]
RECIPES = recipe_labels()

LIVE_PATTERNS = {
    "sequential", "random", "chaos", "gravity", "spiral", "reverse",
    "auto", "rseq", "hilbert", "sobol", "halton", "density-map",
}
LIVE_BSGS = {
    "sequential", "backward", "both", "random", "dance",
    "grumpy", "interleave", "orbit", "residue", "dual-range", "nested",
    "fractal", "async-resolve", "multi-target", "negmap", "handoff",
    "gravity-giant", "chaos-giant", "sobol-giant", "freeze-table", "compact-dp",
}


def _live_token(value: str) -> str:
    return value.split(" (")[0].strip()


def is_research(value: str) -> bool:
    """Legacy helper — most former research flags are now live in TrueCollider."""
    v = _live_token(value).lower()
    stub_only = {
        "electrum-v1", "slip39", "aezeed", "bip85", "rfc1751", "multisig",
        "CreateAccountWithSeed", "producer-split",
    }
    return v in stub_only or "(stub)" in value.lower()


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
    balance_check: bool = False
    balance_url: str = ""
    handoff_bits: str = ""
    vanity: str = ""
    mnemonic_words: str = "12"
    mnemonic_lang: str = "english"
    mnemonic_eth: bool = False
    derivation_path: str = ""
    derivation_depth: str = "1"
    mnemonic_submode: str = "random"
    mnemonic_strategy: str = "checksum-first"
    seed_mask: str = ""
    passphrase_file: str = ""
    passphrase_mask: str = ""
    passphrase_rules: str = ""
    model_file: str = ""
    path_pack: str = "btc-std"
    include_change: bool = True
    include_bip86: bool = True
    weakrng_sub: str = "milksad"
    address_sub: str = "default"
    rmd160_sub: str = "exact"
    filter_strategy: str = "default"
    vector: str = "auto"
    stride: str = ""
    minikey_base: str = ""
    timestamp_window: str = ""
    residue_mr: str = ""
    collision_bits: str = "48"
    dual_target_file: str = ""
    density_map_file: str = ""
    funded_file: str = ""
    extra_args: str = ""
    research_notes: list[str] = field(default_factory=list)

    def build(self) -> tuple[str, list[str]]:
        warns: list[str] = []
        mode_raw = self.mode
        mode = _live_token(mode_raw)

        # Modes the binary understands directly
        if mode == "CreateAccountWithSeed":
            warns.append("CreateAccountWithSeed not in binary yet — using address+sol.")
            live_mode = "address"
        elif mode in MODES_LIVE:
            live_mode = mode
        else:
            live_mode = "address"
            warns.append(f"Unknown mode '{mode_raw}' — using address.")

        parts = [f'"{self.exe}"', "-m", live_mode]

        if self.target_file:
            parts += ["-f", f'"{self.target_file}"']
        if live_mode in ("address", "rmd160", "vanity", "pubkey2addr", "shadow160", "weakrng"):
            parts += ["-c", self.coin, "-l", self.look]
        if self.bits:
            parts += ["-b", self.bits]
        if self.range_start:
            rng = self.range_start
            if self.range_end:
                rng = f"{self.range_start}:{self.range_end}"
            parts += ["-r", rng]

        # -T only for weakrng or mnemonic milksad (never pollute other modes)
        if self.timestamp_window:
            msub = _live_token(self.mnemonic_submode)
            wsub = _live_token(self.weakrng_sub)
            if live_mode == "weakrng" or (live_mode == "mnemonic" and msub == "milksad") or wsub == "milksad" and live_mode == "weakrng":
                tw = self.timestamp_window.strip()
                if ":" in tw:
                    parts += ["-T", tw]
                else:
                    ts = tw.split()[0]
                    if ts.isdigit():
                        parts += ["-T", ts]

        pattern = _live_token(self.search_pattern)
        if pattern == "density-map":
            pattern = "density-map"
        if pattern not in LIVE_PATTERNS:
            warns.append(f"Pattern '{self.search_pattern}' unknown — using chaos.")
            pattern = "chaos"
        if pattern and pattern != "sequential":
            if pattern == "rseq":
                parts.append("-rs")
            else:
                parts += ["-x", pattern]

        if live_mode in ("bsgs", "hybrid-dl"):
            bstrat = _live_token(self.bsgs_strategy)
            if live_mode == "hybrid-dl" and bstrat in ("sequential", "random", "dance"):
                bstrat = "handoff"
            if bstrat not in LIVE_BSGS:
                warns.append(f"BSGS strategy '{self.bsgs_strategy}' unknown — using random.")
                bstrat = "random"
            parts += ["-B", bstrat]
            if self.k_factor:
                parts += ["-k", self.k_factor]
            if self.n_table:
                parts += ["-n", self.n_table]
            if self.save_bloom:
                parts.append("-S")
            if self.residue_mr and ":" in self.residue_mr:
                m, rem = self.residue_mr.split(":", 1)
                parts += ["--mod-step", m.strip(), "--mod-rem", rem.strip()]
            # -H added once below (bsgs / hybrid-dl / kangaroo)

        if live_mode == "gaudry" and self.residue_mr and ":" in self.residue_mr:
            m, rem = self.residue_mr.split(":", 1)
            parts += ["--mod-step", m.strip(), "--mod-rem", rem.strip()]

        if live_mode == "vanity" and self.vanity:
            parts += ["-v", self.vanity]
        if live_mode == "minikeys" and self.minikey_base:
            parts += ["-C", self.minikey_base]

        if live_mode == "mnemonic":
            sub = _live_token(self.mnemonic_submode)
            if sub and sub != "random":
                parts += ["-R", sub]
            if self.mnemonic_words:
                parts += ["-w", self.mnemonic_words]
            lang = _live_token(self.mnemonic_lang)
            if lang:
                parts += ["-L", lang]
            if self.mnemonic_eth:
                parts.append("-W")
            if self.derivation_depth:
                parts += ["-D", self.derivation_depth]
            if self.seed_mask:
                parts += ["--seed", f'"{self.seed_mask}"']
            if self.passphrase_file:
                parts += ["--pass-file", f'"{self.passphrase_file}"']
            if self.passphrase_mask:
                parts += ["--pass-mask", f'"{self.passphrase_mask}"']
            if self.passphrase_rules:
                parts += ["--pass-rules", f'"{self.passphrase_rules}"']
            if self.model_file:
                parts += ["--model", f'"{self.model_file}"']
            pack = _live_token(self.path_pack)
            if pack:
                parts += ["--path-pack", pack]
            if self.include_change:
                parts.append("--change")
            else:
                parts.append("--no-change")
            if self.include_bip86:
                parts.append("--bip86")
            else:
                parts.append("--no-bip86")
            if self.dual_target_file:
                parts += ["--dual-target", f'"{self.dual_target_file}"']
            strat = _live_token(self.mnemonic_strategy)
            if strat in ("checksum-prism", "prism"):
                parts.append("--prism")

        if self.derivation_path and live_mode in ("address", "rmd160", "weakrng"):
            parts += ["-p", f'"{self.derivation_path}"']
            if self.derivation_depth:
                parts += ["-D", self.derivation_depth]

        if live_mode in ("rmd160", "shadow160"):
            rsub = _live_token(self.rmd160_sub)
            if rsub == "shadow160" or live_mode == "shadow160" or rsub.startswith("prefix"):
                bits = self.collision_bits or "48"
                parts += ["--shadow-bits", bits]
            elif rsub not in ("exact", "default", ""):
                warns.append(f"RMD160 submode '{self.rmd160_sub}' partially supported.")

        if live_mode == "weakrng":
            wsub = _live_token(self.weakrng_sub)
            if wsub:
                parts += ["-R", wsub]

        fstrat = _live_token(self.filter_strategy)
        if fstrat and fstrat not in ("default fuse", "default", "bloom-classic", ""):
            parts += ["-F", fstrat]

        if self.endomorphism and live_mode in ("address", "rmd160", "vanity", "shadow160", "weakrng"):
            parts.append("-e")
        if self.threads:
            parts += ["-t", self.threads]
        if self.gpu and self.gpu != "none":
            # "both" = CPU threads (-t) + CUDA. Current shipping builds only accept
            # none/cuda/opencl; map both→cuda so Preview/Launch works until rebuild.
            backend = "cuda" if self.gpu.strip().lower() == "both" else self.gpu
            parts += ["-U", backend]
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
        if self.balance_check:
            if self.balance_url.strip():
                parts.append(f"-N{self.balance_url.strip()}")
            else:
                parts.append("-N")
        if self.handoff_bits and live_mode in ("bsgs", "hybrid-dl", "kangaroo"):
            parts += ["-H", self.handoff_bits]

        if self.density_map_file and pattern == "density-map":
            parts += ["--density-map", f'"{self.density_map_file}"']
        if self.funded_file:
            parts += ["--funded", f'"{self.funded_file}"']

        if self.extra_args.strip():
            parts.append(self.extra_args.strip())

        # Guardrails
        if live_mode in ("address", "rmd160", "xpoint", "bsgs", "kangaroo", "shadow160") and not self.target_file:
            warns.append("No target file (-f). Browse a .txt / .rmd / pubkey file before a real run.")
        if live_mode in ("bsgs", "kangaroo", "hybrid-dl") and not (self.bits or self.range_start):
            warns.append("BSGS/kangaroo need -b bits or -r START:END.")

        cmd = " ".join(parts)
        return cmd, warns


@dataclass
class MkeyConfig:
    exe: str = "TrueMkeyCollider.exe"
    ckeys: str = ""
    mkeys: str = ""
    pubkeys: str = ""
    mode: str = "random"
    start_key: str = ""
    gpu: str = "cuda"  # none=CPU; cuda/opencl=GPU; both=CPU+GPU
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
        g = (self.gpu or "cuda").strip().lower()
        use_gpu = g not in ("none", "cpu", "")
        if use_gpu:
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
        "-m": "Search mode: address, rmd160, xpoint, bsgs, kangaroo, vanity, minikeys, mnemonic, poetry, brainwallet, pubkey2addr, shadow160, weakrng, hybrid-dl, gaudry.",
        "-R": "Research/recovery submode (mask, lastword, pass-dict, milksad, electrum-v2, lattice, …).",
        "--seed": "BIP-39 seed mask or known phrase (use ? for unknowns).",
        "--pass-file": "Passphrase dictionary for 25th-word search.",
        "--pass-mask": "Hashcat-style passphrase mask (?l?d).",
        "--pass-rules": "Rule file applied to passphrase dictionary lines.",
        "--model": "Per-position BIP-39 candidate constraint file.",
        "--path-pack": "PathNova derivation pack (btc-std, eth, electrum, account-sweep, custom).",
        "--change": "Include BIP32 change chain /1/N.",
        "--no-change": "Skip change chain.",
        "--bip86": "Include BIP-86 Taproot paths.",
        "--no-bip86": "Skip Taproot paths.",
        "--dual-target": "Second address file — free reject after first path hit.",
        "--shadow-bits": "Shadow160 / prefix-N bit width.",
        "--mod-step": "Residue modulus M for k≡R(mod M).",
        "--mod-rem": "Residue remainder R for Gaudry/ResidueHerd.",
        "--density-map": "Prior PDF file for -x density-map.",
        "--funded": "Funded UTXO/hash160 snapshot prior.",
        "--prism": "ChecksumPrism — multi-language same entropy.",
        "-F": "Filter strategy (cascade, fuse16, bloom, default).",
        "-H": "HerdHandoff pocket bit width for hybrid BSGS→kangaroo.",
        "-f": "Target file (addresses, hash160, pubkeys).",
        "-c": "Coin / address encoding family (btc eth ltc doge xrp sol bch btg etc troot all auto).",
        "-b": "Bit length of the puzzle / key range.",
        "-r": "Hex range START:END.",
        "-x": "Key ordering (chaos/gravity/spiral/hilbert/sobol/halton/density-map/auto/…).",
        "-B": "BSGS giant-step strategy (incl. grumpy/orbit/handoff/negmap/freeze-table).",
        "-k": "BSGS K factor (baby table multiplier). Use auto if unsure.",
        "-n": "BSGS N (≥2^20) or sequential cycle size.",
        "-S": "Save/load BSGS bloom/fuse tables to disk.",
        "-e": "GLV endomorphism (~3× coverage on secp256k1 grind modes).",
        "-U": "Compute: none (CPU), cuda, opencl, or both (CPU+GPU).",
        "-M": "Memory / VRAM budget (auto, 2048, 2G).",
        "-G": "GPU batch size hint.",
        "-t": "CPU threads.",
        "-A": "SIMD vector: auto / none / sse / avx / avx2 / avx512.",
        "-I": "Stride between keys.",
        "-l": "compress / uncompress / both.",
        "-w": "Mnemonic or brainwallet/poetry word count.",
        "-L": "BIP-39 language (all / prism).",
        "-W": "ETH keccak address checks in mnemonic mode.",
        "-D": "Derivation index depth.",
        "-p": "BIP-32 derivation path (address/rmd160).",
        "-v": "Vanity prefix.",
        "-C": "Minikey base string.",
        "-T": "Unix timestamp, or start:end for MilkSad windows.",
        "-N": "Online balance check on hit (public API or RPC URL).",
        "-y": "Dry-run config dump — always try before long runs.",
        "-q": "Quiet stats.",
        "-s": "Stats interval seconds.",
        "-z": "Bloom size multiplier.",
        "-Z": "Strip leading zero bytes (with -b).",
        "-V": "Verbose derivation.",
        "-d": "Debug.",
        "-ckeys": "TrueMkeyCollider encrypted ckey file.",
        "-mckey": "TrueMkeyCollider encrypted mkey file.",
        "--partial": "Known AES key prefix (partial-key GPU mode).",
        "--selftest": "TrueMkeyCollider PoC host+GPU+WIF pipeline.",
    }
    return docs.get(flag, "See Directory tab or tool -h for details.")
