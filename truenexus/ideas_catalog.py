"""Exhaustive catalog — every item from README_IDEAS_FOR_IMPROVEMENT.

Nothing omitted. Status: live | research | note
"""

from __future__ import annotations

# ── §0 Codebase-verified gaps (productized as selectable intents) ───────
CODEBASE_GAPS = [
    ("mnemonic-empty-passphrase-gap", "note", "Live mnemonic always uses empty passphrase — Pass Lab closes this."),
    ("mnemonic-coin-type-0-gap", "live", "PathNova paths-eth pack covers m/44'/60' + Ledger Live variants."),
    ("mnemonic-no-change-chain", "live", "Change /1/N enabled in PathNova account-sweep and paths-btc."),
    ("mnemonic-no-bip86", "live", "BIP-86 Taproot path in paths-btc / bip86-taproot pack."),
    ("mnemonic-no-custom-p", "research", "Custom -p not in mnemonic mode — paths-custom."),
    ("mnemonic-no-sol-slip0010", "research", "SOL from mnemonic — solana-bip39 ecosystem."),
    ("cuda-bsgs-serial-grp", "live", "CUDA GRP batched giant cycles (batched-gpu-giants)."),
    ("kangaroo-not-rckangaroo", "research", "Kangaroo not RCKangaroo-class yet — SOTA kangaroo track."),
    ("dead-flag-E", "research", "Free CLI letter -E reserved for future mode."),
    ("CreateAccountWithSeed", "research", "Solana CreateAccountWithSeed vanity (SHA256)."),
    ("binary_fuse16", "research", "fuse16 for huge target sets (header exists; not default filter backend)."),
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
    ("OrbitBSGS", "live", "Endomorphism-collapsed baby table; -B orbit / --orbit."),
    ("HerdHandoff", "live", "BSGS→kangaroo cascade; -m hybrid-dl / -B handoff -H bits."),
    ("GrumpyBSGS", "live", "Grumpy giant starts + baby; -B grumpy."),
    ("InterleaveBSGS", "live", "Interleaved BSGS (both); -B interleave."),
    ("GaudrySchost / MultiDim-DL", "live", "2D/modular ECDLP; -m gaudry."),
    ("ResidueHerd", "live", "k≡r(mod m) + gravity walkers; -B residue / --mod-step/--mod-rem."),
    ("FuseCascade", "live", "Coarse48→mid96→exact; -F cascade."),
    ("HilbertStride", "live", "-x hilbert quasirandom."),
    ("SobolWalk", "live", "-x sobol LDS."),
    ("HaltonWalk", "live", "-x halton low-discrepancy (with Sobol family)."),
    ("Shadow160", "live", "Partial hash160 birthday DP; -m shadow160 -s bits."),
    ("CrystalPRNG", "live", "Weak-RNG suite; -m weakrng -R sub."),
    ("MnemonicLattice", "live", "Checksum lattice entropy enum; -R lattice."),
    ("ChecksumPrism", "live", "One entropy→all languages; -L prism/all."),
    ("PathNova", "live", "Budgeted path packs; --path-pack btc-std/eth/electrum/account-sweep."),
    ("WordOrbit", "live", "Fuzzy BIP-39 expand into model mode."),
    ("ChecksumWindow", "research", "Incremental checksum for non-last unknown word."),
    ("SeedCascadeVerify", "research", "Cheapest→expensive progressive verify."),
    ("DualTarget Anchor", "live", "Second address as free reject; --dual-target."),
    ("EntropyTimeline", "live", "Milk Sad time-window mnemonic; -R milksad -T."),
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
    ("hybrid-dl", "live", "HerdHandoff BSGS→kangaroo"),
    ("gaudry", "live", "Gaudry–Schost multi-dim DL"),
    ("shadow160", "live", "hash160 birthday collider"),
    ("weakrng", "live", "CrystalPRNG weak entropy spaces"),
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
    ("hilbert", "live", "HilbertStride quasirandom"),
    ("sobol", "live", "SobolWalk LDS"),
    ("halton", "live", "Halton LDS"),
    ("density-map", "live", "Sample from prior PDF over range"),
    ("milksad-order", "live", "WeakRNG ordering alias for milksad keyspace walk"),
]

# ── BSGS strategies (-B) + impl notes ───────────────────────────────────
BSGS = [
    ("sequential", "live", "Forward giants"),
    ("backward", "live", "Backward giants"),
    ("both", "live", "Top/bottom alternate"),
    ("random", "live", "Random giant starts"),
    ("dance", "live", "Top/bottom/random triple"),
    ("grumpy", "live", "Two grumpy giants + baby"),
    ("interleave", "live", "Interleaved average-case BSGS"),
    ("orbit", "live", "OrbitBSGS endomorphism classes"),
    ("residue", "live", "Arithmetic progression BSGS"),
    ("dual-range", "live", "Shared baby table, two giant fronts"),
    ("nested", "live", "Hierarchical / fractal BSGS"),
    ("fractal", "live", "Alias of nested"),
    ("async-resolve", "live", "GPU giants + CPU baby verify queue"),
    ("multi-target", "live", "One baby table, many pubkeys"),
    ("negmap", "live", "Negation map on giant walk"),
    ("handoff", "live", "BSGS→kangaroo HerdHandoff"),
    ("gravity-giant", "live", "Giant starts biased by near-misses"),
    ("chaos-giant", "live", "Logistic-map giant starts"),
    ("sobol-giant", "live", "LDS giant starts"),
    ("freeze-table", "live", "Never rotate fuse slots once full"),
    ("compact-dp", "live", "16-byte DP entries for hybrid"),
    ("rseq", "live", "Random start → sequential walk (--walk 2M|1B|1T) → reseed"),
]

BSGS_IMPL = [
    ("batched-gpu-giants", "live", "Batch giant cycles per SM (CUDA GRP batching)."),
    ("auto-k-eta", "research", "-k auto prints expected √N time + kangaroo recommend."),
    ("checkpoint-format", "research", "Store fuse checksums, giant offset, RNG/LDS, mode phase."),
    ("multi-gpu-bsgs", "research", "One GPU holds baby fuse; others stream giants."),
    ("handoff-bits-H", "live", "HerdHandoff pocket width -H (e.g. 44)."),
]

# ── Mnemonic ────────────────────────────────────────────────────────────
MNEMONIC_RECOVERY = [
    ("random", "live", "Random valid BIP-39 grind"),
    ("mask", "live", "Known words + ? / x unknowns"),
    ("model", "live", "Per-position candidate constraint file"),
    ("lastword", "live", "Only 128/256 valid last words (16×)"),
    ("prefix-word", "live", "?aba / aban* partial spelling"),
    ("typo", "live", "Single-word sub + adjacent swap"),
    ("permute", "live", "Known multiset, unknown order"),
    ("anagram", "live", "Full word-order permutations"),
    ("positional-swap", "live", "Two positions swapped"),
    ("language-guess", "live", "Unknown BIP-39 language (stub only)"),
    ("mixed-script", "research", "NFC/NFKD / full-width quirks (stub only)"),
]

MNEMONIC_PASS = [
    ("pass-dict", "live", "Dictionary 25th-word attack"),
    ("pass-mask", "live", "Hashcat-style ?l?l?d?d mask"),
    ("pass-rules", "live", "Dict × rule file on GPU"),
    ("pass-hybrid", "live", "Dict + mask append/prepend"),
    ("pass-empty-plus", "live", "Empty / spaces / wallet defaults"),
]

MNEMONIC_ECOSYSTEMS = [
    ("electrum-v1", "live", "Old Electrum 1626-word"),
    ("electrum-v2", "live", "Electrum v2 + 4096× prefilter"),
    ("slip39", "research", "Shamir SLIP39 shares"),
    ("aezeed", "research", "LND aezeed"),
    ("bip85", "live", "BIP-85 child mnemonic index search"),
    ("rfc1751", "live", "Ancient 128-bit word encoding"),
    ("solana-bip39", "research", "ed25519 / SLIP-0010 path packs"),
    ("milksad", "live", "MT19937 time-seeded mnemonic (EntropyTimeline)"),
]

MNEMONIC_PATH_PACKS = [
    ("paths-btc", "live", "44/49/84/86 + change 0/1"),
    ("paths-eth", "live", "44'/60' + Ledger Live variants"),
    ("paths-electrum", "live", "m/0/ and m/1/ gap"),
    ("paths-custom", "live", "User multipath file"),
    ("account-sweep", "live", "account 0..A × index 0..G"),
    ("multisig-cosigner", "research", "xpub + seed as cosigner"),
    ("change-chain-1", "live", "Include change /1/N indices"),
    ("bip86-taproot", "live", "Explicit m/86'/0'/0'/0 pack"),
]

MNEMONIC_STRATEGIES = [
    ("checksum-first", "research", "Never PBKDF2 invalid phrases"),
    ("entropy-guided", "research", "Most constrained slots first"),
    ("freq-prior", "research", "Empirical BIP-39 word frequency"),
    ("lattice", "live", "MnemonicLattice via checksum-first mask"),
    ("checkpointed", "research", "Resume combination cursor"),
    ("random-dedup", "research", "Random walk + seen-entropy bloom"),
    ("producer-split", "research", "Multi-GPU producer/consumer split"),
    ("phrase-gravity", "research", "Bias after near-misses"),
    ("word-orbit", "live", "Fuzzy expand into model mode"),
    ("dual-target", "live", "DualTarget Anchor reject; --dual-target"),
    ("seed-cascade", "research", "SeedCascadeVerify pipeline"),
    ("checksum-window", "research", "Incremental non-last-word checksum"),
    ("checksum-prism", "live", "Multi-language same entropy; -L prism/all"),
]

# ── CrystalPRNG ─────────────────────────────────────────────────────────
WEAKRNG = [
    ("milksad", "live", "Libbitcoin Explorer MT19937 CVE-2023-39910"),
    ("randstorm", "research", "BitcoinJS / browser weak entropy"),
    ("android-sr", "research", "Android SecureRandom 2013"),
    ("profanity", "research", "32-bit seed ETH vanity"),
    ("timestamp-key", "research", "Keys from unix time / counter (-T)"),
]

# ── Address / RMD160 ────────────────────────────────────────────────────
ADDRESS_SUB = [
    ("default", "live", "Standard address grind"),
    ("hd-fanout", "live", "BIP-32 -p/-D children"),
    ("hilbert", "live", "Quasirandom hilbert coverage"),
    ("sobol", "live", "Quasirandom sobol coverage"),
    ("density-map", "live", "Prior PDF sampling over range"),
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
    ("shadow160", "live", "Birthday DP toward target set; --shadow-bits"),
    ("funded-only", "research", "UTXO-funded hash160 only"),
    ("script-tags", "research", "p2pkh/p2wpkh/p2tr tagged targets"),
    ("p2pkh-tag", "research", "P2PKH script tag"),
    ("p2wpkh-tag", "research", "P2WPKH script tag"),
    ("p2tr-tag", "research", "P2TR script tag"),
    ("rmd-of-xonly", "research", "Taproot x-only hash pipelines"),
    ("dual-bloom-device", "research", "Fuse in VRAM + device hash160"),
    ("cascade-filter", "live", "FuseCascade for 20-byte keys; -F cascade"),
    ("unsorted-ingest", "research", "Streaming fuse build unsorted dumps"),
]

FILTERS = [
    ("default fuse", "live", "Binary fuse8 + sorted confirm"),
    ("bloom-classic", "live", "Classic bloom (BSGS tiers)"),
    ("cascade", "live", "FuseCascade multi-resolution"),
    ("fuse16", "research", "binary_fuse16 for huge lists (strategy flag only)"),
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
    "CUDA PBKDF2-HMAC-SHA512 on-device (mask recovery bottleneck)",
    "Checksum-first GPU gate before PBKDF2",
    "SOTA kangaroo CUDA (RCKangaroo-class K≈1.15)",
    "Multi-coin fuse: one EC → BTC/ETH/LTC/DOGE in one kernel",
    "Device-resident hash160 + XOR/fuse GPU prefilter",
    "Mnemonic mask + lastword (CPU live → deepen CUDA)",
    "Mnemonic pass-dict / pass-mask",
    "Custom path packs (BIP-86, ETH Ledger Live, Electrum)",
    "BSGS negmap + better GPU batched giants",
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
    ("address + sobol", "live", "-m address -x sobol — quasirandom grind"),
    ("rmd160 prefix", "research", "-m rmd160 -R prefix-N — partial hash160"),
    ("rmd160 / shadow160", "live", "-m shadow160 — funded hash160 DP birthday"),
    ("bsgs grumpy", "live", "-m bsgs -B grumpy — 2-giant BSGS"),
    ("bsgs orbit", "live", "-m bsgs -B orbit — endomorphism BSGS"),
    ("bsgs handoff", "live", "-m bsgs -B handoff — BSGS→kangaroo"),
    ("kangaroo --mod", "research", "pubkey + residue constrained kangaroo"),
    ("weakrng milksad", "live", "-m weakrng -R milksad — MT19937 keyspace"),
    ("mnemonic mask", "live", "-m mnemonic -R mask — partial BIP-39"),
    ("mnemonic pass-*", "live", "-m mnemonic -R pass-dict/mask — 25th word"),
    ("mnemonic electrum-v2", "live", "-m mnemonic -R electrum-v2"),
    ("mnemonic milksad", "live", "-m mnemonic -R milksad — weak seed RNG"),
    ("mnemonic model", "live", "-m mnemonic -R model — constraint solver"),
    ("CLI: mask 3 missing", "live", "mask + --seed + path-pack + cuda"),
    ("CLI: lastword", "live", "lastword + 11/23 known words"),
    ("CLI: pass-dict", "live", "full seed + --pass-file"),
    ("CLI: electrum-v2", "live", "electrum-v2 seed mask"),
    ("CLI: model file", "live", "--model constraints.json"),
    ("CLI: milksad window", "live", "milksad -T unixStart:unixEnd"),
]

# ── §9 Anti-ideas (explicitly documented so nothing is “left out”) ───────
ANTI_IDEAS = [
    ("NO full-256-bit claims", "anti", "Never claim full 256-bit or blind 12-word search is practical."),
    ("NO AI-finds-keys theater", "anti", "No fake AI without a real constraint model."),
    ("NO half-finished -x spam", "anti", "Don't add 50 RNG reshuffles without substance."),
    ("NO skip-checksum GPU", "anti", "Never skip BIP-39 checksum before PBKDF2."),
    ("NO fuse rotate on long BSGS", "anti", "Use freeze-table — avoid FP death spiral."),
    ("NO key-scraper + auto-withdraw", "anti", "REFUSED: scraping internet keys + auto-sweep to your wallet is theft tooling. Use Address Watch (alert-only) instead."),
    ("NO RBF / mempool race hijack", "anti", "REFUSED: watching foreign spends and RBF-racing them to your receiver is prize sniping. Address Watch alerts only — never auto-spend."),
]

# ── §11 Research 2026 wave (forums/GitHub synthesis — GAP/NOVEL) ─────────
# Status: gap = competitors have / we don't yet; novel = rarely shipped open;
#         live = already in TrueCollider/TrueNexus; anti = never implant.
RESEARCH_GPU_MNEMONIC = [
    ("CUDA PBKDF2-HMAC-SHA512 on-device", "gap", "P0 — Full 2048-iter BIP39 stretch on GPU; CPU PBKDF2 is the mask-recovery bottleneck."),
    ("Checksum-first GPU gate", "gap", "P0 — Reject invalid BIP39 before PBKDF2 (≈4096× for 12-word lastword)."),
    ("Multi-GPU stride scheduler", "gap", "Independent device ranges — zero duplicate mnemonic work."),
    ("Checkpointed mnemonic cursor", "gap", "Resume mask/pass enumeration after crash without redoing space."),
    ("GPU XOR / fuse prefilters", "gap", "P0 — XopMC-style device bloom/xor before derive (-xc/-xu pattern)."),
    ("Electrum v1/v2 GPU path", "gap", "Seed version bytes + different stretch fully on CUDA."),
    ("SLIP39 Shamir GPU recovery", "gap", "Threshold share repair/combine — almost nobody has GPU."),
    ("aezeed Lightning recovery", "gap", "LND aezeed + watchtower identity keys."),
    ("BIP85 child mnemonic search", "gap", "Known parent → child index space (CPU live; GPU still gap)."),
    ("Producer/consumer GPU split", "novel", "GPU-A checksum · GPU-B PBKDF2 · GPU-C EC+hash160 pipeline."),
    ("Passphrase lattice (LM prior)", "novel", "25th-word as low-entropy grammar (years/pets/keyboard) scored, not pure charset."),
    ("Mixed-script wordlist detect", "novel", "EN↔ES↔FR substitution collisions auto-detect."),
    ("Phonetic / OCR typo model GPU", "novel", "QWERTY adjacency + OCR confusion before PBKDF2."),
    ("Solana SLIP-0010 mnemonic CUDA", "gap", "ed25519 mnemonic→pubkey on CUDA (address mode exists; full pipeline gap)."),
    ("TON/Cosmos/Near mnemonic pack", "gap", "One -c multi-target pack beyond BTC/ETH/SOL."),
    ("DualTarget verify BTC+ETH", "novel", "One seed must hit hash160 AND keccak — collapses FPs (flag live; deepen)."),
    ("PathNova adaptive fanout", "novel", "Learn historically hot paths (Ledger ETH, Electrum) and weight GPU work."),
    ("Hashcat rules on GPU", "gap", "best64 / toggles passphrase rules fully on device."),
    ("SeedCascadeVerify", "novel", "Cheap bloom → fuse16 → exact host verify (bandwidth-aware)."),
    ("ChecksumPrism multi-lang", "novel", "Same entropy → N BIP39 wordlists simultaneous (partial live)."),
]

RESEARCH_ECDLP = [
    ("SOTA kangaroo CUDA (RCKangaroo-class)", "gap", "P0 — K≈1.15 endo/symmetry as -m kangaroo CUDA backend."),
    ("16-byte compact DP + async resolve", "gap", "PSCKangaroo-style DP density + async BSGS resolve on hit."),
    ("Crash-safe DP checkpoint / ramlimit", "gap", "Month-long #135 runs with resume + -ramlimit."),
    ("HerdHandoff deepen tame preload", "live", "hybrid-dl live — deepen with tame herd preload."),
    ("Multi-GPU kangaroo tame/wild split", "gap", "Tame table GPU0; wild herds GPU1..N."),
    ("NegMap + SOTA shared arena", "novel", "negmap BSGS + kangaroo wilds in one memory arena."),
    ("Orbit-collapsed tame table", "novel", "Endo classes shared across kangaroo + BSGS."),
    ("Known-pubkey puzzle pack recipes", "gap", "135/140/145/150/155/160 one-click kangaroo (partial LIVE in Puzzles)."),
    ("Kangaroo + residue --mod", "novel", "Gaudry–Schost interval split on kangaroo walks."),
    ("DP gravity prior", "novel", "Bias wild jumps toward historically dense DP regions."),
    ("JLP / BitCrack DP import", "gap", "Interoperability for competitor DP file formats."),
    ("PubKey→Address dual-use EC", "novel", "While DL hunting, also emit hash160 into funded bloom."),
]

RESEARCH_ADDRESS_FILTERS = [
    ("Device-resident hash160 + fuse", "gap", "P0 — Minimize PCIe; hash+fuse stay on GPU."),
    ("XorFilter / Ribbon ingest", "gap", "Smaller than bloom for static target sets."),
    ("Shadow160 CUDA birthday", "novel", "Partial hash160 DP with CUDA sort/hash (UI live)."),
    ("Funded-only UTXO snapshot filter", "novel", "Exclude dust/empty — funded hash160 primary."),
    ("P2TR x-only match completeness", "gap", "Taproot internal/output key paths complete."),
    ("Multi-coin fuse one kernel", "novel", "P0 — One EC → BTC/ETH/LTC/DOGE encodings in one pass."),
    ("Script-template collide", "novel", "P2SH redeem templates, not only P2PKH."),
    ("Vanity regex on GPU", "gap", "Charset / regex / middle match constraints."),
]

RESEARCH_WEAKRNG = [
    ("MilkSad harden time windows", "live", "Libbitcoin Explorer MT19937 — harden -T UX."),
    ("Profanity 32-bit ETH vanity", "gap", "Known 32-bit seed vanity kernel."),
    ("Android SecureRandom 2013", "gap", "Reduced-entropy Android keyspaces."),
    ("Blockchain.info / JS Math.random", "gap", "Early browser wallet weak RNG eras."),
    ("Wallet.dat ckey + TrueMkey unified", "novel", "IV oracle workflow with TrueMkeyCollider."),
    ("EntropyTimeline UI year→submode", "novel", "Pick year/firmware → auto weakrng + bit budget."),
]

RESEARCH_MULTICOIN = [
    ("ETH keccak in same CUDA EC batch", "gap", "BTC+ETH from one EC batch."),
    ("TRX / BCH / BTG cashaddr packs", "gap", "Cashaddr + TRON packs."),
    ("Solana base58 grind completeness", "gap", "Full ed25519 vanity/grind path."),
    ("Cross-curve secp+ed25519 batch", "novel", "Dual kernels sharing mnemonic entropy."),
    ("EVM chain-id vanity displays", "novel", "Same key, different checksum address displays."),
    ("Lightning aezeed + watchtower", "gap", "Node identity recovery."),
    ("Ordinals-aware funded scoring", "novel", "Metadata prior for funded filter — not key search."),
]

RESEARCH_UX_OPS = [
    ("Address Watch tab (alert-only)", "live", "Lawful substitute for scraper/RBF — balance/tx alerts only."),
    ("Recipes always dry-run first", "gap", "Every recipe emits --dry-run before Launch."),
    ("Job queue / multi-GPU farm dashboard", "gap", "Queue + farm status across devices."),
    ("Competitor CLI → recipe translator", "gap", "RCKangaroo flags → TrueCollider recipe."),
    ("Honesty meter ETA", "novel", "Estimate time-to-exhaust vs hardware before Launch."),
    ("Rebuild/sync -U both button", "gap", "Map rebuild → Sync Tools + -U both."),
]

RESEARCH_NOVEL_RARE = [
    ("Semantic brainwallets (offline LM)", "novel", "LLM-ranked passphrase candidates → GPU verify (offline model only)."),
    ("HD gap-limit first-class mode", "novel", "Scan receive+change 0..N with early abort."),
    ("Descriptor wallet recovery", "novel", "Output Script Descriptors → constrained path packs."),
    ("Miniscript / multisig partial key", "novel", "Known one key of 2-of-3 search."),
    ("PSBT-assisted path inference", "novel", "Unsigned PSBT metadata → paths/coins."),
    ("Mempool prior as density-map only", "novel", "Research density for ranges you already search — never steal hook."),
    ("ZK-friendly hit batch verify", "novel", "Prove a hit without leaking full key to untrusted worker."),
    ("Work certificates for mnemonic farms", "novel", "Anti-cheat without sharing seed."),
    ("Synthetic BIP39 LM prior", "novel", "Word co-occurrence priors from synthetic data only."),
    ("HSM/wallet chip RNG fingerprint", "novel", "Constrained nonce spaces — academic."),
    ("Taproot internal vs output dual match", "novel", "Both keys in one pass."),
]

# ── §10 Sources (reference) ─────────────────────────────────────────────
SOURCES = [
    ("Keyhunt / Collider BSGS", "note", "albertobsd lineage"),
    ("RCKangaroo / PSCKangaroo", "note", "ALL-TAME, 16-byte DP, async BSGS resolve"),
    ("JeanLucPons Kangaroo", "note", "Classic kangaroo"),
    ("BitcoinAddressFinder", "note", "OpenCL + LMDB patterns"),
    ("BTCCollider", "note", "Partial hash160 birthday"),
    ("Hydra / btcrecover / CryptoRecover / wrecover / CUDAHUNT", "note", "Mnemonic recovery practice"),
    ("XopMC / OpenCL BIP39 / multi-coin CUDA mnemonic", "note", "2024–2026 GPU mnemonic ecosystem"),
    ("Pollard / vOW / Gaudry-Schost / Bernstein-Lange", "note", "DL papers"),
    ("Binary fuse filters (Graf–Lemire)", "note", "Filter science"),
    ("BIP-39/32/44/49/84/85/86 · SLIP39 · Electrum", "note", "Standards"),
    ("CVE-2023-39910 Milk Sad · Android SR · Randstorm", "note", "Weak RNG histories"),
]


def _labels(items: list[tuple[str, str, str]], annotate: bool = True) -> list[str]:
    out = []
    for name, status, _desc in items:
        if not annotate or status == "live":
            out.append(name)
        elif status in ("research", "gap", "novel", "note", "anti"):
            out.append(f"{name} ({status})")
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
    ("§11A GPU MNEMONIC", RESEARCH_GPU_MNEMONIC),
    ("§11B ECDLP", RESEARCH_ECDLP),
    ("§11C ADDR/FILTER", RESEARCH_ADDRESS_FILTERS),
    ("§11D WEAKRNG+", RESEARCH_WEAKRNG),
    ("§11E MULTICOIN", RESEARCH_MULTICOIN),
    ("§11F UX/OPS", RESEARCH_UX_OPS),
    ("§11G NOVEL RARE", RESEARCH_NOVEL_RARE),
]


def all_idea_cards() -> list[tuple[str, str, str]]:
    cards: list[tuple[str, str, str]] = []
    for section, items in SECTION_MAP:
        for name, status, desc in items:
            cards.append((f"[{section}] {name}", status, desc))
    return cards


def completeness_report() -> str:
    cards = all_idea_cards()
    counts: dict[str, int] = {}
    for _, s, _ in cards:
        counts[s] = counts.get(s, 0) + 1
    lines = [
        "TrueNexus Ideas Catalog — NOTHING OMITTED",
        "-----------------------------------------",
        f"Total entries in GUI catalog: {len(cards)}",
    ]
    for key in ("live", "gap", "novel", "research", "note", "anti"):
        if key in counts:
            lines.append(f"  {key.capitalize():10} {counts[key]}")
    extra = {k: v for k, v in counts.items() if k not in ("live", "gap", "novel", "research", "note", "anti")}
    for k, v in sorted(extra.items()):
        lines.append(f"  {k:10} {v}")
    lines += [
        "",
        f"Sections mirrored: {len(SECTION_MAP)}",
        f"P0={len(ROADMAP_P0)} P1={len(ROADMAP_P1)} P2={len(ROADMAP_P2)} P3={len(ROADMAP_P3)}",
        f"Recipes={len(RECIPES)} Anti-ideas={len(ANTI_IDEAS)} Sources={len(SOURCES)}",
        f"Research-2026 wave: GPU={len(RESEARCH_GPU_MNEMONIC)} ECDLP={len(RESEARCH_ECDLP)} "
        f"Filter={len(RESEARCH_ADDRESS_FILTERS)} Multi={len(RESEARCH_MULTICOIN)} Novel={len(RESEARCH_NOVEL_RARE)}",
        "",
        "Full text: docs/README_IDEAS_FOR_IMPROVEMENT.md · docs/RESEARCH_2026.md",
        "Tabs: Ideas Matrix · Address Watch · Roadmap · Recipes · Full Ideas Doc",
    ]
    return "\n".join(lines) + "\n"
