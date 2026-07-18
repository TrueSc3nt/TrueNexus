"""TrueNexus Directory — how to use every mode, flag, setting, and lab.

This is the in-app encyclopedia. Keep in sync with TrueCollider CLI + Ideas catalog.
"""

from __future__ import annotations

from truenexus.ideas_catalog import (
    ADDRESS_SUB,
    ALGORITHMS,
    ANTI_IDEAS,
    BSGS,
    BSGS_IMPL,
    CROSS_CUTTING,
    FILTERS,
    MNEMONIC_ECOSYSTEMS,
    MNEMONIC_PASS,
    MNEMONIC_PATH_PACKS,
    MNEMONIC_RECOVERY,
    MNEMONIC_STRATEGIES,
    MODES,
    PATTERNS,
    RECIPES,
    RESEARCH_ADDRESS_FILTERS,
    RESEARCH_ECDLP,
    RESEARCH_GPU_MNEMONIC,
    RESEARCH_MULTICOIN,
    RESEARCH_NOVEL_RARE,
    RESEARCH_UX_OPS,
    RESEARCH_WEAKRNG,
    RMD160_SUB,
    WEAKRNG,
)

# ── Modes (-m) ──────────────────────────────────────────────────────────
MODE_HOWTO: list[tuple[str, str, str]] = [
    ("address", "LIVE",
     "Hunt private keys whose address appears in -f.\n"
     "Need: target address file, -b bits or -r START:END, -c coin, -l compress.\n"
     "Use when: you only have addresses (no pubkey).\n"
     "Example: keyhunt -m address -f tests/66.txt -b 66 -l compress -e -t 8 -x chaos"),
    ("rmd160", "LIVE",
     "Same as address but targets raw 20-byte HASH160 (hex) — faster filter path.\n"
     "Need: .rmd / hex hash160 file.\n"
     "Example: keyhunt -m rmd160 -f targets.rmd -b 66 -l compress -e -t 8"),
    ("xpoint", "LIVE",
     "Match the X coordinate of the public key (not the address).\n"
     "Need: file of X points / compressed pub hex without prefix sometimes.\n"
     "Use when: you have X-only / subtracted points."),
    ("bsgs", "LIVE",
     "Baby-step giant-step for KNOWN PUBKEY + known bit/range.\n"
     "Need: pubkey file (-f), -b or -r, -k (auto ok), -B strategy, lots of RAM.\n"
     "Mid-size puzzles (≈40–90 bits with RAM). Prefer kangaroo for huge N.\n"
     "Example: keyhunt -m bsgs -f tests/125.txt -b 125 -k auto -B random -t 8 -S"),
    ("kangaroo", "LIVE",
     "Pollard's kangaroo — pubkey + range; better than BSGS for large puzzles.\n"
     "Need: pubkey (-f), -r or -b. GPU: -U cuda.\n"
     "Example: keyhunt -m kangaroo -f pub.txt -r START:END -U cuda -M auto"),
    ("vanity", "LIVE",
     "Generate keys until address matches prefix -v.\n"
     "Need: -v prefix (Base58 charset). Optional -c coin.\n"
     "Example: keyhunt -m vanity -v 1Cool -e -t 8"),
    ("minikeys", "LIVE",
     "Bitcoin Casascius-style minikey (S…) space.\n"
     "Optional -C base string. Target file of addresses."),
    ("mnemonic", "LIVE",
     "BIP-39 seed ecosystem: random grind OR recovery (-R mask/lastword/pass-*).\n"
     "Need: -f targets, -w 12/24, -L language, --seed for masks, --path-pack.\n"
     "Open Mnemonic Lab / Passphrase Lab for full UI."),
    ("poetry", "LIVE",
     "Wordlist poetry → SHA256 → key. Target addresses in -f. -w word count."),
    ("brainwallet", "LIVE",
     "Passphrase → SHA256 → key. Classic brainwallet grind. -w optional."),
    ("pubkey2addr", "LIVE",
     "Walk keys and emit/compare addresses (random-style address walk)."),
    ("shadow160", "LIVE",
     "Partial HASH160 birthday / prefix collision toward a set (--shadow-bits).\n"
     "Different from exact rmd160 — DP collision class."),
    ("weakrng", "LIVE",
     "CrystalPRNG: enumerate broken RNG keyspaces (milksad, etc.) via -R.\n"
     "Use -T start:end for Milk Sad time windows."),
    ("hybrid-dl", "LIVE",
     "HerdHandoff: run BSGS until a pocket, then kangaroo (-H bits).\n"
     "Need pubkey + range. Open Kangaroo / Hybrid Lab."),
    ("gaudry", "LIVE",
     "Residue / multi-dim style DL when k ≡ R (mod M). Set --mod-step / --mod-rem."),
    ("CreateAccountWithSeed", "RESEARCH",
     "Solana CreateAccountWithSeed vanity (SHA256) — not a normal keypair. Stub maps to address+sol."),
    ("wif-mask / hex-mask", "RESEARCH",
     "Recover from partial WIF / hex private key with ? masks. Research UI / future mode."),
]

# ── Patterns (-x) ───────────────────────────────────────────────────────
PATTERN_HOWTO: list[tuple[str, str, str]] = [
    ("sequential", "LIVE", "Linear walk from range start. Best for tiny ranges / verification."),
    ("random", "LIVE", "Uniform random bases in range. Good default exploration."),
    ("rseq / -rs / -B rseq", "LIVE", "Random start, walk --walk keys (1M/1B/1T), reseed. Collider Lab: Search mode → rseq."),
    ("chaos", "LIVE", "Logistic-map ergodic starts — fills space without RNG clustering."),
    ("gravity", "LIVE", "Bias toward last hit region (70/30). After first find, concentrates search."),
    ("spiral", "LIVE", "Archimedean spiral from range midpoint — hits 'round' midpoints first."),
    ("reverse", "LIVE", "Inverted BSGS baby/giant roles (collision pattern change)."),
    ("auto", "LIVE", "Cycles spiral→chaos→gravity→reverse every few hundred batches."),
    ("hilbert", "LIVE", "HilbertStride quasirandom — locality-preserving coverage of the bit cube."),
    ("sobol", "LIVE", "Sobol low-discrepancy sequence — stronger even coverage than LCG random."),
    ("halton", "LIVE", "Halton LDS sibling of Sobol."),
    ("density-map", "LIVE", "Sample from a prior PDF file (--density-map). Informed Bayesian search."),
]

# ── BSGS (-B) ───────────────────────────────────────────────────────────
BSGS_HOWTO: list[tuple[str, str, str]] = [
    ("sequential", "LIVE", "Forward giant steps. Classic Keyhunt default."),
    ("backward", "LIVE", "Giants walk backward through the range."),
    ("both", "LIVE", "Alternate top/bottom fronts."),
    ("random", "LIVE", "Random giant starts — good default for unknown distribution."),
    ("dance", "LIVE", "Top / bottom / random triple rotation."),
    ("grumpy", "LIVE", "Two grumpy giant progressions + baby (Bernstein–Lange). Mid ranges + RAM."),
    ("interleave", "LIVE", "Interleaved baby/giant work — better average-case constants."),
    ("orbit", "LIVE", "Endomorphism-collapsed baby table (OrbitBSGS). Auto-enables -e."),
    ("residue", "LIVE", "BSGS on arithmetic progression k≡R(mod M). Pair with --mod-step/--mod-rem."),
    ("dual-range", "LIVE", "Shared baby table, two giant fronts (two candidate ranges)."),
    ("nested / fractal", "LIVE", "Hierarchical coarse→fine BSGS tables."),
    ("async-resolve", "LIVE", "GPU giants + CPU baby verify queue."),
    ("multi-target", "LIVE", "One baby table, many pubkeys (puzzle lists)."),
    ("negmap", "LIVE", "Negation map on giant walk (~√2 constant). Enables -e."),
    ("handoff", "LIVE", "BSGS until pocket width -H, then kangaroo (HerdHandoff)."),
    ("gravity-giant", "LIVE", "Giant starts biased by near-misses."),
    ("chaos-giant", "LIVE", "Logistic-map giant starts."),
    ("sobol-giant", "LIVE", "LDS giant starts."),
    ("freeze-table", "LIVE", "Never rotate fuse slots once full — week-long runs."),
    ("compact-dp", "LIVE", "16-byte DP entries for hybrid kangaroo bridge."),
]

# ── Flags ───────────────────────────────────────────────────────────────
FLAG_HOWTO: list[tuple[str, str, str]] = [
    ("-m", "Mode", "Search mode (see Modes section). Required for every run."),
    ("-f", "Target file", "Addresses, hash160, pubkeys, or bloom sources. Browse in TrueCollider tab."),
    ("-c", "Coin", "btc eth ltc doge xrp sol bch btg etc troot all auto — address encoding family."),
    ("-l", "Look", "compress / uncompress / both — pubkey serialization for BTC-family."),
    ("-b", "Bits", "Puzzle bit length. Range becomes [2^(b-1) .. 2^b-1]."),
    ("-r", "Range", "Hex START:END private-key window."),
    ("-T", "Timestamp", "Unix time or start:end — Milk Sad / weakrng windows."),
    ("-x", "Pattern", "Key ordering (chaos, sobol, hilbert, …). See Patterns."),
    ("-B", "BSGS strategy", "Giant-step strategy. See BSGS section."),
    ("-k", "K factor", "BSGS baby-table multiplier. Prefer power-of-2 or auto."),
    ("-n", "N / cycle", "BSGS N (≥2^20, perfect square root) or sequential cycle size."),
    ("-S", "Save blooms", "Persist BSGS bloom/fuse tables to disk for resume."),
    ("-e", "Endomorphism", "GLV ~3× coverage on secp grind modes. Orbit/negmap auto-set."),
    ("-U", "GPU", "none | cuda | opencl | both (CPU+GPU). Both maps to cuda on older builds."),
    ("-M", "Memory", "VRAM/RAM budget: auto, 2048, 2G, matrix."),
    ("-G", "GPU batch", "Hint for keys per GPU batch."),
    ("-t", "Threads", "CPU worker threads."),
    ("-A", "Vector", "SIMD: auto none sse avx avx2 avx512 for hash160."),
    ("-I", "Stride", "Step between keys (address/rmd160/xpoint)."),
    ("-R", "Submode", "Research/recovery submode: mask, milksad, pass-dict, …"),
    ("--seed", "Seed mask", "BIP-39 phrase with ? unknowns, or known full phrase."),
    ("--pass-file", "Pass dict", "25th-word dictionary file."),
    ("--pass-mask", "Pass mask", "Hashcat-style ?l?d mask for passphrase."),
    ("--pass-rules", "Pass rules", "Rule file (best64-style) applied to dict words."),
    ("--model", "Model file", "Per-position BIP-39 candidate constraints."),
    ("--path-pack", "PathNova", "btc-std | eth | electrum | account-sweep | custom."),
    ("--change / --no-change", "Change chain", "Include or skip BIP32 /1/N."),
    ("--bip86 / --no-bip86", "Taproot paths", "Include m/86' Taproot derivation."),
    ("--dual-target", "DualTarget", "Second address file — free reject after first hit."),
    ("--shadow-bits", "Shadow bits", "Prefix / birthday bit width for shadow160."),
    ("--mod-step / --mod-rem", "Residue", "M and R for k≡R(mod M) (gaudry/residue)."),
    ("--density-map", "Density PDF", "Prior file for -x density-map."),
    ("--funded", "Funded snapshot", "UTXO-funded hash160 list prior."),
    ("-F", "Filter", "default | cascade | fuse16 | bloom."),
    ("-H", "Handoff bits", "HerdHandoff pocket width (e.g. 44)."),
    ("-w", "Words", "Mnemonic/poetry/brain word count."),
    ("-L", "Language", "BIP-39 wordlist; all / prism for multi-lang."),
    ("-W", "ETH keccak", "Also check ETH address encoding in mnemonic."),
    ("-D", "Depth", "Derivation index count (0..D-1)."),
    ("-p", "Path", "BIP-32 path for address/rmd160 HD fanout."),
    ("-v", "Vanity", "Address prefix string."),
    ("-C", "Minikey base", "Starting minikey string."),
    ("-N", "Balance", "On hit, query public API (or -Nurl) for balance."),
    ("-y", "Dry-run", "Print resolved config and exit — always try first."),
    ("-q", "Quiet", "Less chatty stats."),
    ("-s", "Stats sec", "Progress print interval."),
    ("-z", "Bloom mult", "Bloom size multiplier."),
    ("-Z", "Strip zeros", "Leading zero-byte strip with -b."),
    ("-V", "Verbose", "Verbose derivation / debug paths."),
    ("-d", "Debug", "Debug logging."),
]

# ── TrueMkey ────────────────────────────────────────────────────────────
MKEY_HOWTO: list[tuple[str, str, str]] = [
    ("-ckeys", "LIVE", "Path to encrypted ckey blob dump from wallet.dat."),
    ("-mckey", "LIVE", "Path to encrypted master key (mkey) blob."),
    ("-pubkeys", "LIVE", "Optional known pubkeys for early reject."),
    ("-r / -q / -rs", "LIVE", "random / sequential / mixed AES-key search order."),
    ("-d", "LIVE", "CUDA device index."),
    ("-g", "LIVE", "Grid dim e.g. 256,256."),
    ("-streams", "LIVE", "CUDA streams."),
    ("-M", "LIVE", "Memory budget."),
    ("--partial", "LIVE", "Known AES key prefix hex — partial-key GPU mode."),
    ("--try", "LIVE", "Try a specific AES key candidate."),
    ("--selftest", "LIVE", "Host+GPU+WIF pipeline self-test."),
    ("GPU dropdown", "LIVE", "none=CPU only · cuda/opencl=GPU · both=CPU+GPU."),
]

# ── GUI settings & labs ─────────────────────────────────────────────────
GUI_HOWTO: list[tuple[str, str, str]] = [
    ("Home", "GUI", "Advisor + quick Puzzle 66. Start here if new."),
    ("TrueCollider", "GUI", "Master controls for every -m flag. Preview builds the CLI; Dry-Run (-y) first."),
    ("Puzzles", "GUI", "Puzzle #1–160. Address or Known-pubkey target. Auto-fills -b/-r and may switch to BSGS."),
    ("Mnemonic Lab", "GUI", "All -R recovery/ecosystem submodes, seed mask, path packs, DualTarget."),
    ("Passphrase Lab", "GUI", "25th-word: pass-dict / pass-mask / pass-rules / hybrid / empty-plus."),
    ("PathNova Lab", "GUI", "Derivation packs: BTC 44/49/84/86, ETH/Ledger, Electrum, account-sweep."),
    ("BSGS Lab", "GUI", "Jump to BSGS settings; strategies include grumpy/orbit/handoff."),
    ("Kangaroo Lab", "GUI", "kangaroo + hybrid-dl + -H handoff bits + GPU."),
    ("Shadow160 Lab", "GUI", "Partial hash160 birthday; --shadow-bits."),
    ("Patterns Lab", "GUI", "Every -x ordering including hilbert/sobol/density-map."),
    ("Filters Lab", "GUI", "FuseCascade / fuse16 / bloom / funded snapshot."),
    ("Address / RMD160", "GUI", "Address & rmd160 submodes, HD fanout, stride."),
    ("WeakRNG Lab", "GUI", "milksad / randstorm / android-sr / profanity / timestamp-key."),
    ("Vanity Lab", "GUI", "vanity / poetry / brainwallet / minikeys."),
    ("Algorithms Lab", "GUI", "OrbitBSGS, Grumpy, Interleave, Gaudry, HerdHandoff, FuseCascade, …"),
    ("GPU Lab", "GUI", "CUDA/OpenCL, memory, vector SIMD, honesty notes on P0 gaps."),
    ("Multi-coin Lab", "GUI", "Coin packs and multi-coin fuse research intents."),
    ("TrueMkey", "GUI", "wallet.dat AES GPU cracker."),
    ("Address Watch", "GUI", "Lawful alert-only balance/tx monitor. NO withdraw, NO RBF."),
    ("Directory", "GUI", "This encyclopedia — search every mode/flag/setting."),
    ("Ideas Matrix", "GUI", "Full catalog cards LIVE/GAP/NOVEL/ANTI."),
    ("Roadmap", "GUI", "P0–P3 + anti-ideas."),
    ("Recipes", "GUI", "One-click apply common CLI sketches."),
    ("Settings", "GUI", "Exe paths, default threads/GPU, console refresh (GPU-safe)."),
    ("Console refresh", "GUI", "5/10/15/20 sec — slows UI updates so GPU runs don't freeze the GUI."),
    ("Dry-Run", "GUI", "Always Preview then Dry-Run before long GPU jobs."),
    ("Stop", "GUI", "Stops the child process; wait for console to settle before re-Launch."),
]

SECTION_DIR: list[tuple[str, list[tuple[str, str, str]]]] = [
    ("1. Modes (-m)", MODE_HOWTO),
    ("2. Patterns (-x)", PATTERN_HOWTO),
    ("3. BSGS strategies (-B)", BSGS_HOWTO),
    ("4. CLI flags", FLAG_HOWTO),
    ("5. TrueMkeyCollider", MKEY_HOWTO),
    ("6. GUI tabs & settings", GUI_HOWTO),
    ("7. Catalog — Algorithms", [(n, s.upper(), d) for n, s, d in ALGORITHMS]),
    ("8. Catalog — Mnemonic recovery", [(n, s.upper(), d) for n, s, d in MNEMONIC_RECOVERY]),
    ("9. Catalog — Passphrase", [(n, s.upper(), d) for n, s, d in MNEMONIC_PASS]),
    ("10. Catalog — Seed ecosystems", [(n, s.upper(), d) for n, s, d in MNEMONIC_ECOSYSTEMS]),
    ("11. Catalog — Path packs", [(n, s.upper(), d) for n, s, d in MNEMONIC_PATH_PACKS]),
    ("12. Catalog — Mnemonic strategies", [(n, s.upper(), d) for n, s, d in MNEMONIC_STRATEGIES]),
    ("13. Catalog — WeakRNG", [(n, s.upper(), d) for n, s, d in WEAKRNG]),
    ("14. Catalog — Address subs", [(n, s.upper(), d) for n, s, d in ADDRESS_SUB]),
    ("15. Catalog — RMD160 subs", [(n, s.upper(), d) for n, s, d in RMD160_SUB]),
    ("16. Catalog — Filters", [(n, s.upper(), d) for n, s, d in FILTERS]),
    ("17. Catalog — BSGS list", [(n, s.upper(), d) for n, s, d in BSGS + BSGS_IMPL]),
    ("18. Catalog — Patterns list", [(n, s.upper(), d) for n, s, d in PATTERNS]),
    ("19. Catalog — Modes list", [(n, s.upper(), d) for n, s, d in MODES]),
    ("20. Research 2026 — GPU mnemonic", [(n, s.upper(), d) for n, s, d in RESEARCH_GPU_MNEMONIC]),
    ("21. Research 2026 — ECDLP", [(n, s.upper(), d) for n, s, d in RESEARCH_ECDLP]),
    ("22. Research 2026 — Filters", [(n, s.upper(), d) for n, s, d in RESEARCH_ADDRESS_FILTERS]),
    ("23. Research 2026 — WeakRNG+", [(n, s.upper(), d) for n, s, d in RESEARCH_WEAKRNG]),
    ("24. Research 2026 — Multicoin", [(n, s.upper(), d) for n, s, d in RESEARCH_MULTICOIN]),
    ("25. Research 2026 — UX", [(n, s.upper(), d) for n, s, d in RESEARCH_UX_OPS]),
    ("26. Research 2026 — Novel rare", [(n, s.upper(), d) for n, s, d in RESEARCH_NOVEL_RARE]),
    ("27. Cross-cutting", [(n, s.upper(), d) for n, s, d in CROSS_CUTTING]),
    ("28. Recipes", [(n, s.upper(), d) for n, s, d in RECIPES]),
    ("29. ANTI (never implant)", [(n, s.upper(), d) for n, s, d in ANTI_IDEAS]),
]


def all_directory_entries() -> list[tuple[str, str, str, str]]:
    """(section, name, status, howto)"""
    out: list[tuple[str, str, str, str]] = []
    for section, items in SECTION_DIR:
        for name, status, desc in items:
            out.append((section, name, status, desc))
    return out


def directory_stats() -> str:
    entries = all_directory_entries()
    return (
        f"Directory entries: {len(entries)}\n"
        f"Sections: {len(SECTION_DIR)}\n"
        "Search below filters name + howto text.\n"
        "LIVE = works in binary today · RESEARCH/GAP/NOVEL = UI + roadmap · ANTI = refused.\n"
    )


def format_entry(section: str, name: str, status: str, desc: str) -> str:
    return f"[{section}] {name}  ({status})\n{desc}\n"


def search_directory(query: str) -> list[tuple[str, str, str, str]]:
    q = (query or "").strip().lower()
    entries = all_directory_entries()
    if not q or q == "*":
        return entries
    hit = []
    for section, name, status, desc in entries:
        blob = f"{section} {name} {status} {desc}".lower()
        if q in blob:
            hit.append((section, name, status, desc))
    return hit
