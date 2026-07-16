"""Complete catalog of every idea from README_IDEAS_FOR_IMPROVEMENT.

Status:
  live      — flag exists in TrueCollider / TrueMkeyCollider today
  research — UI-exposed; maps to annotated preview until kernel ships
"""

from __future__ import annotations

# ── Algorithms (section 2) ──────────────────────────────────────────────
ALGORITHMS = [
    ("OrbitBSGS", "research", "Endomorphism-collapsed baby table; ~√3–√6 RAM win."),
    ("HerdHandoff", "research", "BSGS localizes pocket → kangaroo finishes."),
    ("GrumpyBSGS", "research", "Bernstein–Lange two grumpy giants + baby."),
    ("InterleaveBSGS", "research", "Average-case interleaved baby/giant BSGS."),
    ("GaudrySchost / MultiDim-DL", "research", "2D / modular constraint ECDLP walks."),
    ("ResidueHerd", "research", "k ≡ r (mod m) + gravity-biased walkers."),
    ("FuseCascade", "research", "Coarse 48-bit → mid 96-bit → exact fuse pipeline."),
    ("HilbertStride", "research", "Hilbert-curve key ordering over the range."),
    ("SobolWalk", "research", "Sobol / Halton low-discrepancy coverage."),
    ("Shadow160", "research", "Partial RIPEMD-160 birthday / DP collider."),
    ("CrystalPRNG", "research", "Weak-RNG keyspace engine suite."),
    ("MnemonicLattice", "research", "Checksum-valid entropy lattice enumeration."),
    ("ChecksumPrism", "research", "One entropy → all BIP-39 languages."),
    ("PathNova", "research", "Budgeted multi-wallet derivation path packs."),
    ("WordOrbit", "research", "Fuzzy word memory → BIP-39 candidate expand."),
    ("ChecksumWindow", "research", "Incremental checksum for non-last unknown word."),
    ("SeedCascadeVerify", "research", "Cheapest→expensive progressive verify pipeline."),
    ("DualTarget Anchor", "research", "Second known address as free reject."),
    ("EntropyTimeline", "research", "Milk Sad time-window mnemonic generation."),
    ("PhraseGravity", "research", "Gravity bias in seed / index space after near-miss."),
    ("CascadeHunt", "research", "GPU EC → device hash160 → cascade fuse → FOUND."),
    ("Producer/Consumer GPU", "research", "Split checksum / PBKDF2 / EC across GPUs."),
]

# ── Modes (-m) ──────────────────────────────────────────────────────────
MODES = [
    ("address", "live", "Address list grind"),
    ("rmd160", "live", "Raw hash160 grind"),
    ("xpoint", "live", "Pubkey X match"),
    ("bsgs", "live", "Baby-step giant-step"),
    ("kangaroo", "live", "Pollard's kangaroo"),
    ("vanity", "live", "Address prefix"),
    ("minikeys", "live", "Bitcoin minikey S…"),
    ("mnemonic", "live", "BIP-39 random → paths"),
    ("poetry", "live", "Poetry wordlist keys"),
    ("brainwallet", "live", "Passphrase → SHA256 key"),
    ("pubkey2addr", "live", "Random-only address walk"),
    ("hybrid-dl", "research", "HerdHandoff BSGS→kangaroo"),
    ("gaudry", "research", "Gaudry–Schost multi-dim DL"),
    ("shadow160", "research", "hash160 birthday collider"),
    ("weakrng", "research", "CrystalPRNG weak entropy spaces"),
    ("CreateAccountWithSeed", "research", "Solana seed vanity (SHA256)"),
]

# ── Search patterns (-x) ────────────────────────────────────────────────
PATTERNS = [
    ("sequential", "live", "Linear walk"),
    ("random", "live", "Uniform random bases"),
    ("rseq", "live", "Random-sequential batches"),
    ("chaos", "live", "Logistic-map ergodic"),
    ("gravity", "live", "Bias near last hit"),
    ("spiral", "live", "Archimedean from midpoint"),
    ("reverse", "live", "Inverted BSGS roles"),
    ("auto", "live", "Cycle spiral→chaos→gravity→reverse"),
    ("hilbert", "research", "HilbertStride quasirandom"),
    ("sobol", "research", "SobolWalk LDS"),
    ("density-map", "research", "Sample from prior PDF over range"),
]

# ── BSGS strategies (-B) ────────────────────────────────────────────────
BSGS = [
    ("sequential", "live", "Forward giants"),
    ("backward", "live", "Backward giants"),
    ("both", "live", "Top/bottom alternate"),
    ("random", "live", "Random giant starts"),
    ("dance", "live", "Top/bottom/random triple"),
    ("grumpy", "research", "Two grumpy giants + baby"),
    ("interleave", "research", "Interleaved average-case BSGS"),
    ("orbit", "research", "OrbitBSGS endomorphism classes"),
    ("residue", "research", "Arithmetic progression BSGS"),
    ("dual-range", "research", "Shared baby table, two giant fronts"),
    ("nested", "research", "Hierarchical / fractal BSGS"),
    ("fractal", "research", "Alias of nested"),
    ("async-resolve", "research", "GPU giants + CPU baby verify queue"),
    ("multi-target", "research", "One baby table, many pubkeys"),
    ("negmap", "research", "Negation map on giant walk"),
    ("handoff", "research", "BSGS→kangaroo HerdHandoff"),
    ("gravity-giant", "research", "Giant starts biased by near-misses"),
    ("chaos-giant", "research", "Logistic-map giant starts"),
    ("sobol-giant", "research", "LDS giant starts"),
    ("freeze-table", "research", "Never rotate fuse slots once full"),
    ("compact-dp", "research", "16-byte DP entries for hybrid"),
]

# ── Mnemonic recovery submodes ──────────────────────────────────────────
MNEMONIC_RECOVERY = [
    ("random", "live", "Random valid BIP-39 grind"),
    ("mask", "research", "Known words + ? unknowns"),
    ("model", "research", "Per-position candidate constraint file"),
    ("lastword", "research", "Only 128/256 valid last words"),
    ("prefix-word", "research", "?aba / aban* partial spelling"),
    ("typo", "research", "Edit-distance / wrong-word recovery"),
    ("permute", "research", "Known words, unknown order"),
    ("anagram", "research", "Permute + 1–2 substitutions"),
    ("positional-swap", "research", "Two positions swapped"),
    ("language-guess", "research", "Unknown BIP-39 language"),
    ("mixed-script", "research", "NFC/NFKD / full-width quirks"),
]

MNEMONIC_PASS = [
    ("pass-dict", "research", "Dictionary 25th-word attack"),
    ("pass-mask", "research", "Hashcat-style passphrase mask"),
    ("pass-rules", "research", "Dict × rule file on GPU"),
    ("pass-hybrid", "research", "Dict + mask append/prepend"),
    ("pass-empty-plus", "research", "Empty / spaces / wallet defaults"),
]

MNEMONIC_ECOSYSTEMS = [
    ("electrum-v1", "research", "Old Electrum 1626-word"),
    ("electrum-v2", "research", "Electrum v2 + 4096× prefilter"),
    ("slip39", "research", "Shamir SLIP39 shares"),
    ("aezeed", "research", "LND aezeed"),
    ("bip85", "research", "BIP-85 child mnemonic index search"),
    ("rfc1751", "research", "Ancient 128-bit word encoding"),
    ("solana-bip39", "research", "ed25519 / SLIP-0010 path packs"),
    ("milksad", "research", "MT19937 time-seeded mnemonic (EntropyTimeline)"),
]

MNEMONIC_PATH_PACKS = [
    ("paths-btc", "research", "44/49/84/86 + change 0/1"),
    ("paths-eth", "research", "44'/60' + Ledger Live variants"),
    ("paths-electrum", "research", "m/0/ and m/1/ gap"),
    ("paths-custom", "research", "User multipath file"),
    ("account-sweep", "research", "account 0..A × index 0..G"),
    ("multisig-cosigner", "research", "xpub + seed as cosigner"),
]

MNEMONIC_STRATEGIES = [
    ("checksum-first", "research", "Never PBKDF2 invalid phrases"),
    ("entropy-guided", "research", "Most constrained slots first"),
    ("freq-prior", "research", "Empirical BIP-39 word frequency"),
    ("lattice", "research", "MnemonicLattice bit enumeration"),
    ("checkpointed", "research", "Resume combination cursor"),
    ("random-dedup", "research", "Random walk + seen-entropy bloom"),
    ("producer-split", "research", "Multi-GPU producer/consumer split"),
    ("phrase-gravity", "research", "Bias after near-misses"),
    ("word-orbit", "research", "Fuzzy expand into model mode"),
    ("dual-target", "research", "DualTarget Anchor reject"),
    ("seed-cascade", "research", "SeedCascadeVerify pipeline"),
    ("checksum-window", "research", "Incremental non-last-word checksum"),
    ("checksum-prism", "research", "Multi-language same entropy"),
]

# ── CrystalPRNG / weakrng ───────────────────────────────────────────────
WEAKRNG = [
    ("milksad", "research", "Libbitcoin Explorer MT19937 CVE-2023-39910"),
    ("randstorm", "research", "BitcoinJS / browser weak entropy"),
    ("android-sr", "research", "Android SecureRandom 2013"),
    ("profanity", "research", "32-bit seed ETH vanity"),
    ("timestamp-key", "research", "Keys from unix time / counter (-T)"),
]

# ── Address expansions ──────────────────────────────────────────────────
ADDRESS_SUB = [
    ("default", "live", "Standard address grind"),
    ("hd-fanout", "live", "BIP-32 -p/-D children (live on address/rmd160)"),
    ("multi-coin-fuse", "research", "One EC → BTC+ETH+troot in one pass"),
    ("vanity-regex", "research", "Regex / suffix / middle vanity"),
    ("balance-prior", "research", "Bias toward funded weak keyspaces"),
    ("stream-targets", "research", "mmap/LMDB huge target DB"),
    ("gpu-hash160-device", "research", "Hash+fuse stay on GPU"),
    ("stride-adaptive", "research", "Auto-tune -I from bloom hit rate"),
    ("pair-compress", "research", "Compress+uncompress from one EC mul"),
    ("density-map", "research", "Prior PDF sampling"),
]

# ── RMD160 expansions ───────────────────────────────────────────────────
RMD160_SUB = [
    ("exact", "live", "Full 20-byte fuse match"),
    ("prefix-N", "research", "Match first N nybbles"),
    ("shadow160", "research", "Birthday DP toward target set"),
    ("funded-only", "research", "UTXO-funded hash160 only"),
    ("script-tags", "research", "p2pkh/p2wpkh/p2tr tagged targets"),
    ("rmd-of-xonly", "research", "Taproot x-only hash pipelines"),
    ("dual-bloom-device", "research", "Fuse in VRAM + device hash160"),
    ("cascade-filter", "research", "FuseCascade for 20-byte keys"),
    ("unsorted-ingest", "research", "Streaming fuse build unsorted dumps"),
]

# ── Filters ─────────────────────────────────────────────────────────────
FILTERS = [
    ("default fuse", "live", "Binary fuse8 + sorted confirm"),
    ("bloom-classic", "live", "Classic bloom (BSGS tiers)"),
    ("cascade", "research", "FuseCascade multi-resolution"),
    ("fuse16", "research", "binary_fuse16 for huge lists"),
]

# ── Cross-cutting product features ──────────────────────────────────────
CROSS_CUTTING = [
    ("Unified hit schema JSONL", "research", "mode/coin/path/mnemonic/priv/addr/ts"),
    ("Dry-run complexity / ETA", "research", "Search-space size before launch"),
    ("Mode advisor", "live", "TrueNexus Home advisor + target heuristics"),
    ("Shared fuse cache", "research", "Persist huge fuse across modes"),
    ("Multi-GPU work stealer", "research", "Dynamic shards for mask spaces"),
    ("Property tests", "research", "Known-answer vectors per new mode"),
    ("Research harness", "research", "Auto-benchmark grumpy vs kangaroo"),
    ("Checkpoint / resume", "research", "RNG + mnemonic cursor + BSGS giant offset"),
    ("Online balance -N", "live", "TrueCollider -N on hit"),
]

# ── Roadmap priorities ──────────────────────────────────────────────────
ROADMAP_P0 = [
    "Mnemonic mask + lastword + checksum-first",
    "Mnemonic pass-dict / pass-mask",
    "Custom path packs (BIP-86, ETH Ledger, Electrum)",
    "BSGS negmap + batched GPU giants",
    "Device-side hash160 + fuse",
]
ROADMAP_P1 = [
    "Mnemonic model + WordOrbit",
    "Electrum v2",
    "HerdHandoff hybrid DL",
    "-x sobol / hilbert",
    "weakrng / Milk Sad",
]
ROADMAP_P2 = [
    "GrumpyBSGS + InterleaveBSGS",
    "OrbitBSGS",
    "GaudrySchost / residue herds",
    "Shadow160",
    "SLIP39 + aezeed",
    "FuseCascade",
]
ROADMAP_P3 = [
    "ChecksumPrism + MnemonicLattice",
    "Multi-GPU producer/consumer mnemonic",
    "DualTarget Anchor",
    "PathNova multisig cosigner",
]


def _labels(items: list[tuple[str, str, str]], annotate: bool = True) -> list[str]:
    out = []
    for name, status, _desc in items:
        if annotate and status == "research":
            out.append(f"{name} (research)")
        else:
            out.append(name)
    return out


def mode_labels() -> list[str]:
    return _labels(MODES)


def pattern_labels() -> list[str]:
    return _labels(PATTERNS)


def bsgs_labels() -> list[str]:
    return _labels(BSGS)


def mnemonic_submode_labels() -> list[str]:
    return (
        _labels(MNEMONIC_RECOVERY)
        + _labels(MNEMONIC_PASS)
        + _labels(MNEMONIC_ECOSYSTEMS)
        + _labels(MNEMONIC_PATH_PACKS)
    )


def mnemonic_strategy_labels() -> list[str]:
    return _labels(MNEMONIC_STRATEGIES)


def weakrng_labels() -> list[str]:
    return _labels(WEAKRNG)


def address_sub_labels() -> list[str]:
    return _labels(ADDRESS_SUB)


def rmd160_sub_labels() -> list[str]:
    return _labels(RMD160_SUB)


def filter_labels() -> list[str]:
    return _labels(FILTERS)


def all_idea_cards() -> list[tuple[str, str, str]]:
    """Flat list (title, status, desc) for Ideas Matrix UI."""
    cards: list[tuple[str, str, str]] = []
    sections = [
        ("ALGORITHM", ALGORITHMS),
        ("MODE", MODES),
        ("PATTERN", PATTERNS),
        ("BSGS", BSGS),
        ("MNEMONIC RECOVERY", MNEMONIC_RECOVERY),
        ("MNEMONIC PASSPHRASE", MNEMONIC_PASS),
        ("MNEMONIC ECOSYSTEM", MNEMONIC_ECOSYSTEMS),
        ("PATH PACK", MNEMONIC_PATH_PACKS),
        ("MNEMONIC STRATEGY", MNEMONIC_STRATEGIES),
        ("WEAK RNG", WEAKRNG),
        ("ADDRESS", ADDRESS_SUB),
        ("RMD160", RMD160_SUB),
        ("FILTER", FILTERS),
        ("CROSS-CUTTING", CROSS_CUTTING),
    ]
    for section, items in sections:
        for name, status, desc in items:
            cards.append((f"[{section}] {name}", status, desc))
    return cards


def completeness_report() -> str:
    cards = all_idea_cards()
    live = sum(1 for _, s, _ in cards if s == "live")
    research = sum(1 for _, s, _ in cards if s == "research")
    return (
        f"TrueNexus Ideas Catalog\n"
        f"-----------------------\n"
        f"Total entries exposed in GUI: {len(cards)}\n"
        f"  Live (shipped in binaries):  {live}\n"
        f"  Research (UI + annotated):   {research}\n"
        f"\nP0 roadmap: {len(ROADMAP_P0)} items\n"
        f"P1 roadmap: {len(ROADMAP_P1)} items\n"
        f"P2 roadmap: {len(ROADMAP_P2)} items\n"
        f"P3 roadmap: {len(ROADMAP_P3)} items\n"
        f"\nEvery idea from README_IDEAS_FOR_IMPROVEMENT is selectable\n"
        f"somewhere in TrueNexus dropdowns or the Ideas Matrix tab.\n"
    )
