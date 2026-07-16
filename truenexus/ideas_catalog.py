"""Exhaustive catalog — every item from README_IDEAS_FOR_IMPROVEMENT.

Nothing omitted. Status: live | research | note
"""

from __future__ import annotations

# ── §0 Codebase-verified gaps (productized as selectable intents) ───────
CODEBASE_GAPS = [
    ("mnemonic-empty-passphrase-gap", "note", "Live mnemonic always uses empty passphrase — Pass Lab closes this."),
    ("mnemonic-coin-type-0-gap", "note", "Live -W does ETH encode but not m/44'/60' — PathNova paths-eth closes this."),
    ("mnemonic-no-change-chain", "research", "External /0/N only today — enable change /1/N in PathNova."),
    ("mnemonic-no-bip86", "research", "BIP-86 Taproot path missing in mnemonic — in paths-btc pack."),
    ("mnemonic-no-custom-p", "research", "Custom -p not in mnemonic mode — paths-custom."),
    ("mnemonic-no-sol-slip0010", "research", "SOL from mnemonic — solana-bip39 ecosystem."),
    ("cuda-bsgs-serial-grp", "research", "GPU GRP still serial — batched-gpu-giants."),
    ("kangaroo-not-rckangaroo", "research", "Kangaroo not RCKangaroo-class yet — SOTA kangaroo track."),
    ("dead-flag-E", "research", "Free CLI letter -E reserved for future mode."),
    ("CreateAccountWithSeed", "research", "Solana CreateAccountWithSeed vanity (SHA256)."),
    ("binary_fuse16", "research", "fuse16 for huge target sets."),
    ("wif-hex-mask", "research", "WIF / hex-mask mutation as dedicated mode."),
    ("checkpoint-resume-rng", "research", "Checkpoint RNG + mnemonic cursor + BSGS giant offset."),
]

# ── §1 North-star vision ────────────────────────────────────────────────
NORTH_STAR = [
    ("Unify interval ECDLP", "note", "BSGS + kangaroo + research variants under one dispatcher."),
    ("Unify hash160/address hunting", "note", "Weak-entropy + space-filling orderings."),
    ("Unify full mnemonic/seed ecosystem", "note", "Recovery suite, not just random grind."),
    ("One filter stack", "note", "Shared fuse/bloom across modes."),
    ("One FOUND_* hit format", "research", "Unified JSONL hit schema."),
    ("One GPU dispatcher", "note", "TrueNexus + TrueCollider -U routing."),
]

# ── §2 Algorithms ───────────────────────────────────────────────────────
ALGORITHMS = [
    ("OrbitBSGS", "research", "Endomorphism-collapsed baby table; flag -B orbit / --orbit."),
    ("HerdHandoff", "research", "BSGS→kangaroo cascade; -m hybrid-dl -H handoffBits."),
    ("GrumpyBSGS", "research", "Bernstein–Lange two grumpy giants + baby; -B grumpy."),
    ("InterleaveBSGS", "research", "Average-case interleaved BSGS; -B interleave."),
    ("GaudrySchost / MultiDim-DL", "research", "2D/modular ECDLP; -m gaudry."),
    ("ResidueHerd", "research", "k≡r(mod m) + gravity walkers; --mod-step/--mod-rem."),
    ("FuseCascade", "research", "Coarse48→mid96→exact; -F cascade."),
    ("HilbertStride", "research", "-x hilbert quasirandom."),
    ("SobolWalk", "research", "-x sobol LDS."),
    ("HaltonWalk", "research", "-x halton low-discrepancy (with Sobol family)."),
    ("Shadow160", "research", "Partial hash160 birthday DP; -m shadow160 -s bits."),
    ("CrystalPRNG", "research", "Weak-RNG suite; -m weakrng -R sub."),
    ("MnemonicLattice", "research", "Checksum lattice entropy enum; -R lattice."),
    ("ChecksumPrism", "research", "One entropy→all languages; -L prism."),
    ("PathNova", "research", "Budgeted path packs; --path-pack."),
    ("WordOrbit", "research", "Fuzzy BIP-39 expand into model mode."),
    ("ChecksumWindow", "research", "Incremental checksum for non-last unknown word."),
    ("SeedCascadeVerify", "research", "Cheapest→expensive progressive verify."),
    ("DualTarget Anchor", "research", "Second address as free reject."),
    ("EntropyTimeline", "research", "Milk Sad time-window mnemonic; -R milksad -T."),
    ("PhraseGravity", "research", "Gravity bias in seed/index space."),
    ("CascadeHunt", "research", "GPU EC→device hash160→cascade fuse→FOUND."),
    ("CascadeHunt early-exit stats", "research", "Warn if coarse fuse hit-rate is absurd."),
    ("Producer/Consumer GPU", "research", "Checksum GPU / PBKDF2 GPUs / EC GPU split."),
    ("Mnemonic 4-meters", "research", "raw cand/s · checksum-pass/s · PBKDF2/s · addr/s."),
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
    ("wif-mask", "research", "WIF missing-char / mask recovery"),
    ("hex-mask", "research", "Partial hex private-key mask"),
    ("kangaroo-mod", "research", "Kangaroo with modular constraint"),
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
    ("halton", "research", "Halton LDS"),
    ("density-map", "research", "Sample from prior PDF over range"),
    ("milksad-order", "research", "WeakRNG ordering alias for milksad keyspace walk"),
]

# ── BSGS strategies (-B) + impl notes ───────────────────────────────────
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

BSGS_IMPL = [
    ("batched-gpu-giants", "research", "Batch giant cycles per SM (not <<<1,1>>>)."),
    ("auto-k-eta", "research", "-k auto prints expected √N time + kangaroo recommend."),
    ("checkpoint-format", "research", "Store fuse checksums, giant offset, RNG/LDS, mode phase."),
    ("multi-gpu-bsgs", "research", "One GPU holds baby fuse; others stream giants."),
    ("handoff-bits-H", "research", "HerdHandoff pocket width -H (e.g. 44)."),
]

# ── Mnemonic ────────────────────────────────────────────────────────────
MNEMONIC_RECOVERY = [
    ("random", "live", "Random valid BIP-39 grind"),
    ("mask", "research", "Known words + ? / x unknowns"),
    ("model", "research", "Per-position candidate constraint file"),
    ("lastword", "research", "Only 128/256 valid last words (16×)"),
    ("prefix-word", "research", "?aba / aban* partial spelling"),
    ("typo", "research", "Hamming / Levenshtein wrong-word"),
    ("permute", "research", "Known multiset, unknown order"),
    ("anagram", "research", "Permute + 1–2 substitutions"),
    ("positional-swap", "research", "Two positions swapped"),
    ("language-guess", "research", "Unknown BIP-39 language"),
    ("mixed-script", "research", "NFC/NFKD / full-width quirks"),
]

MNEMONIC_PASS = [
    ("pass-dict", "research", "Dictionary 25th-word attack"),
    ("pass-mask", "research", "Hashcat-style ?l?l?d?d mask"),
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
    ("change-chain-1", "research", "Include change /1/N indices"),
    ("bip86-taproot", "research", "Explicit m/86'/0'/0'/0 pack"),
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

# ── CrystalPRNG ─────────────────────────────────────────────────────────
WEAKRNG = [
    ("milksad", "research", "Libbitcoin Explorer MT19937 CVE-2023-39910"),
    ("randstorm", "research", "BitcoinJS / browser weak entropy"),
    ("android-sr", "research", "Android SecureRandom 2013"),
    ("profanity", "research", "32-bit seed ETH vanity"),
    ("timestamp-key", "research", "Keys from unix time / counter (-T)"),
]

# ── Address / RMD160 ────────────────────────────────────────────────────
ADDRESS_SUB = [
    ("default", "live", "Standard address grind"),
    ("hd-fanout", "live", "BIP-32 -p/-D children"),
    ("hilbert", "research", "Quasirandom hilbert coverage"),
    ("sobol", "research", "Quasirandom sobol coverage"),
    ("density-map", "research", "Prior PDF sampling over range"),
    ("multi-coin-fuse", "research", "One EC → BTC+ETH+troot"),
    ("vanity-regex", "research", "Regex / suffix / middle vanity"),
    ("balance-prior", "research", "Bias toward funded weak keyspaces"),
    ("stream-targets", "research", "mmap/LMDB huge target DB"),
    ("gpu-hash160-device", "research", "Hash+fuse stay on GPU"),
    ("stride-adaptive", "research", "Auto-tune -I from bloom hit rate"),
    ("pair-compress", "research", "Compress+uncompress from one EC mul"),
    ("online-balance-N", "live", "TrueCollider -N on hit"),
]

RMD160_SUB = [
    ("exact", "live", "Full 20-byte fuse match"),
    ("prefix-N", "research", "Match first N nybbles"),
    ("shadow160", "research", "Birthday DP toward target set"),
    ("funded-only", "research", "UTXO-funded hash160 only"),
    ("script-tags", "research", "p2pkh/p2wpkh/p2tr tagged targets"),
    ("p2pkh-tag", "research", "P2PKH script tag"),
    ("p2wpkh-tag", "research", "P2WPKH script tag"),
    ("p2tr-tag", "research", "P2TR script tag"),
    ("rmd-of-xonly", "research", "Taproot x-only hash pipelines"),
    ("dual-bloom-device", "research", "Fuse in VRAM + device hash160"),
    ("cascade-filter", "research", "FuseCascade for 20-byte keys"),
    ("unsorted-ingest", "research", "Streaming fuse build unsorted dumps"),
]

FILTERS = [
    ("default fuse", "live", "Binary fuse8 + sorted confirm"),
    ("bloom-classic", "live", "Classic bloom (BSGS tiers)"),
    ("cascade", "research", "FuseCascade multi-resolution"),
    ("fuse16", "research", "binary_fuse16 for huge lists"),
]

# ── §6 Cross-cutting ────────────────────────────────────────────────────
CROSS_CUTTING = [
    ("Unified hit schema JSONL", "research", "mode/coin/path/mnemonic/pass/priv/addr/ts"),
    ("Dry-run complexity / ETA", "research", "Search-space size before launch"),
    ("Mode advisor", "live", "TrueNexus Home advisor + target heuristics"),
    ("Shared fuse cache", "research", "Persist huge fuse across modes"),
    ("Multi-GPU work stealer", "research", "Dynamic shards for mask spaces"),
    ("Property tests", "research", "Known-answer vectors per new mode"),
    ("Research harness", "research", "Auto-benchmark grumpy vs kangaroo puzzle 40–70"),
    ("Checkpoint / resume", "research", "RNG + mnemonic cursor + BSGS giant offset"),
    ("Online balance -N", "live", "TrueCollider -N on hit"),
    ("SOTA kangaroo track", "research", "RCKangaroo-class GPU herds / endo walks"),
]

# ── §7 Roadmap ──────────────────────────────────────────────────────────
ROADMAP_P0 = [
    "Mnemonic mask + lastword + checksum-first (CPU then CUDA PBKDF2)",
    "Mnemonic pass-dict / pass-mask",
    "Custom path packs (BIP-86, ETH Ledger Live, Electrum)",
    "BSGS negmap + better GPU batched giants",
    "Device-side hash160 + fuse for address/rmd160",
]
ROADMAP_P1 = [
    "Mnemonic model file + WordOrbit",
    "Electrum v2 (4096× prefilter)",
    "HerdHandoff hybrid DL",
    "-x sobol / hilbert for address/rmd160",
    "weakrng / Milk Sad mnemonic+key modes",
]
ROADMAP_P2 = [
    "GrumpyBSGS + InterleaveBSGS",
    "OrbitBSGS",
    "GaudrySchost / residue herds",
    "Shadow160 birthday collider",
    "SLIP39 + aezeed",
    "FuseCascade for billion-address sets",
]
ROADMAP_P3 = [
    "ChecksumPrism + MnemonicLattice",
    "Multi-GPU producer/consumer mnemonic pipeline",
    "DualTarget Anchor recovery",
    "PathNova multisig cosigner search",
]

# ── §8 Help-table recipes ───────────────────────────────────────────────
RECIPES = [
    ("address + sobol", "research", "-m address -x sobol — quasirandom grind"),
    ("rmd160 prefix", "research", "-m rmd160 -R prefix-N — partial hash160"),
    ("rmd160 / shadow160", "research", "-m shadow160 — funded hash160 DP birthday"),
    ("bsgs grumpy", "research", "-m bsgs -B grumpy — 2-giant BSGS"),
    ("bsgs orbit", "research", "-m bsgs -B orbit — endomorphism BSGS"),
    ("bsgs handoff", "research", "-m bsgs -B handoff — BSGS→kangaroo"),
    ("kangaroo --mod", "research", "pubkey + residue constrained kangaroo"),
    ("weakrng milksad", "research", "-m weakrng -R milksad — MT19937 keyspace"),
    ("mnemonic mask", "research", "-m mnemonic -R mask — partial BIP-39"),
    ("mnemonic pass-*", "research", "-m mnemonic -R pass-dict/mask — 25th word"),
    ("mnemonic electrum-v2", "research", "-m mnemonic -R electrum-v2"),
    ("mnemonic milksad", "research", "-m mnemonic -R milksad — weak seed RNG"),
    ("mnemonic model", "research", "-m mnemonic -R model — constraint solver"),
    ("CLI: mask 3 missing", "research", "mask + --seed + path-pack + cuda"),
    ("CLI: lastword", "research", "lastword + 11/23 known words"),
    ("CLI: pass-dict", "research", "full seed + --pass-file"),
    ("CLI: electrum-v2", "research", "electrum-v2 seed mask"),
    ("CLI: model file", "research", "--model constraints.json"),
    ("CLI: milksad window", "research", "milksad -T unixStart:unixEnd"),
]

# ── §9 Anti-ideas (explicitly documented so nothing is “left out”) ───────
ANTI_IDEAS = [
    ("NO full-256-bit claims", "note", "Never claim full 256-bit or blind 12-word search is practical."),
    ("NO AI-finds-keys theater", "note", "No fake AI without a real constraint model."),
    ("NO half-finished -x spam", "note", "Don't add 50 RNG reshuffles without substance."),
    ("NO skip-checksum GPU", "note", "Never skip BIP-39 checksum before PBKDF2."),
    ("NO fuse rotate on long BSGS", "note", "Use freeze-table — avoid FP death spiral."),
]

# ── §10 Sources (reference) ─────────────────────────────────────────────
SOURCES = [
    ("Keyhunt / Collider BSGS", "note", "albertobsd lineage"),
    ("RCKangaroo / PSCKangaroo", "note", "ALL-TAME, 16-byte DP, async BSGS resolve"),
    ("JeanLucPons Kangaroo", "note", "Classic kangaroo"),
    ("BitcoinAddressFinder", "note", "OpenCL + LMDB patterns"),
    ("BTCCollider", "note", "Partial hash160 birthday"),
    ("Hydra / btcrecover / CryptoRecover / wrecover / CUDAHUNT", "note", "Mnemonic recovery practice"),
    ("Pollard / vOW / Gaudry-Schost / Bernstein-Lange", "note", "DL papers"),
    ("Binary fuse filters (Graf–Lemire)", "note", "Filter science"),
    ("BIP-39/32/44/49/84/85/86 · SLIP39 · Electrum", "note", "Standards"),
    ("CVE-2023-39910 Milk Sad · Android SR · Randstorm", "note", "Weak RNG histories"),
]


def _labels(items: list[tuple[str, str, str]], annotate: bool = True) -> list[str]:
    out = []
    for name, status, _desc in items:
        if annotate and status == "research":
            out.append(f"{name} (research)")
        elif annotate and status == "note":
            out.append(f"{name} (note)")
        else:
            out.append(name)
    return out


def mode_labels() -> list[str]:
    return _labels(MODES)


def pattern_labels() -> list[str]:
    return _labels(PATTERNS)


def bsgs_labels() -> list[str]:
    return _labels(BSGS) + _labels(BSGS_IMPL)


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


def recipe_labels() -> list[str]:
    return _labels(RECIPES)


SECTION_MAP = [
    ("§0 CODEBASE GAP", CODEBASE_GAPS),
    ("§1 NORTH STAR", NORTH_STAR),
    ("§2 ALGORITHM", ALGORITHMS),
    ("§2/3 MODE", MODES),
    ("§2 PATTERN", PATTERNS),
    ("§3 BSGS", BSGS),
    ("§3 BSGS IMPL", BSGS_IMPL),
    ("§5 MNEMONIC RECOVERY", MNEMONIC_RECOVERY),
    ("§5 MNEMONIC PASSPHRASE", MNEMONIC_PASS),
    ("§5 MNEMONIC ECOSYSTEM", MNEMONIC_ECOSYSTEMS),
    ("§5 PATH PACK", MNEMONIC_PATH_PACKS),
    ("§5 MNEMONIC STRATEGY", MNEMONIC_STRATEGIES),
    ("§2 WEAK RNG", WEAKRNG),
    ("§4 ADDRESS", ADDRESS_SUB),
    ("§4 RMD160", RMD160_SUB),
    ("§2/4 FILTER", FILTERS),
    ("§6 CROSS-CUTTING", CROSS_CUTTING),
    ("§8 RECIPE", RECIPES),
    ("§9 ANTI-IDEA", ANTI_IDEAS),
    ("§10 SOURCE", SOURCES),
]


def all_idea_cards() -> list[tuple[str, str, str]]:
    cards: list[tuple[str, str, str]] = []
    for section, items in SECTION_MAP:
        for name, status, desc in items:
            cards.append((f"[{section}] {name}", status, desc))
    return cards


def completeness_report() -> str:
    cards = all_idea_cards()
    live = sum(1 for _, s, _ in cards if s == "live")
    research = sum(1 for _, s, _ in cards if s == "research")
    note = sum(1 for _, s, _ in cards if s == "note")
    return (
        f"TrueNexus Ideas Catalog - NOTHING OMITTED\n"
        f"-----------------------------------------\n"
        f"Total entries in GUI catalog: {len(cards)}\n"
        f"  Live:     {live}\n"
        f"  Research: {research}\n"
        f"  Notes:    {note}\n"
        f"\nSections mirrored: {len(SECTION_MAP)}\n"
        f"P0={len(ROADMAP_P0)} P1={len(ROADMAP_P1)} P2={len(ROADMAP_P2)} P3={len(ROADMAP_P3)}\n"
        f"Recipes={len(RECIPES)} Anti-ideas={len(ANTI_IDEAS)} Sources={len(SOURCES)}\n"
        f"\nFull text: docs/README_IDEAS_FOR_IMPROVEMENT.md\n"
        f"Tabs: Ideas Matrix · Roadmap · Recipes · Full Ideas Doc\n"
    )
