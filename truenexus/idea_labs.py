"""Lab tab definitions — every idea group gets a dedicated TrueNexus page."""

from __future__ import annotations

from truenexus.ideas_catalog import (
    ADDRESS_SUB,
    ALGORITHMS,
    BSGS,
    FILTERS,
    MNEMONIC_PASS,
    MNEMONIC_PATH_PACKS,
    PATTERNS,
    RESEARCH_ADDRESS_FILTERS,
    RESEARCH_ECDLP,
    RESEARCH_GPU_MNEMONIC,
    RESEARCH_MULTICOIN,
    RESEARCH_NOVEL_RARE,
    RESEARCH_WEAKRNG,
    WEAKRNG,
)

# (nav_title, section_title, blurb, catalog_items, default_mode_token, apply_kind)
# apply_kind drives _apply_lab_selection in app.py
LAB_SPECS: list[dict] = [
    {
        "nav": "Passphrase Lab",
        "title": "25th-word / passphrase attacks",
        "blurb": (
            "Known mnemonic + dictionary / mask / rules for BIP-39 passphrase.\n"
            "Pipeline: fixed seed → PBKDF2(pass) → PathNova → address filter.\n"
            "Apply sends you to TrueCollider with mode=mnemonic and the chosen -R."
        ),
        "items": MNEMONIC_PASS,
        "default_mode": "mnemonic",
        "kind": "mnemonic_sub",
        "extra_fields": ["seed", "pass_file", "pass_mask", "pass_rules"],
    },
    {
        "nav": "PathNova Lab",
        "title": "Derivation path packs",
        "blurb": (
            "Budgeted HD path explosion per candidate seed.\n"
            "BTC 44/49/84/86 + change · ETH / Ledger Live · Electrum · account-sweep.\n"
            "Use with Mnemonic Lab submodes (mask/pass/random)."
        ),
        "items": MNEMONIC_PATH_PACKS,
        "default_mode": "mnemonic",
        "kind": "path_pack",
        "extra_fields": ["change", "bip86", "depth"],
    },
    {
        "nav": "Kangaroo Lab",
        "title": "Kangaroo + HerdHandoff hybrid DL",
        "blurb": (
            "Use kangaroo when you have a PUBKEY + range (large puzzles).\n"
            "hybrid-dl / -B handoff: BSGS localizes a pocket (-H bits) then kangaroo finishes.\n"
            "Pick a strategy below, set handoff bits, Apply → TrueCollider."
        ),
        "items": [
            ("kangaroo", "live", "Pollard's kangaroo — pubkey + range"),
            ("hybrid-dl", "live", "HerdHandoff BSGS→kangaroo"),
            ("handoff", "live", "BSGS strategy handoff (sets -B handoff)"),
            ("compact-dp", "live", "16-byte DP bridge"),
            ("SOTA kangaroo CUDA", "gap", "RCKangaroo-class — P0 gap"),
            ("Multi-GPU tame/wild", "gap", "Tame GPU0 / wild GPU1..N"),
        ],
        "default_mode": "kangaroo",
        "kind": "kangaroo",
        "extra_fields": ["handoff_bits", "bits", "target"],
    },
    {
        "nav": "Shadow160 Lab",
        "title": "Partial hash160 / birthday collider",
        "blurb": (
            "Shadow160 is NOT exact rmd160 — it hunts prefix collisions with DP herds.\n"
            "Set collision bits (--shadow-bits). Funded snapshot optional."
        ),
        "items": [
            ("shadow160", "live", "Birthday DP toward target set"),
            ("prefix-N", "research", "Match first N nybbles of hash160"),
            ("funded-only", "research", "UTXO-funded hash160 only"),
            ("exact", "live", "Full 20-byte fuse match (use -m rmd160)"),
            ("cascade-filter", "live", "FuseCascade for 20-byte keys"),
            ("rmd-of-xonly", "research", "Taproot x-only hash pipelines"),
        ],
        "default_mode": "shadow160",
        "kind": "shadow160",
        "extra_fields": ["shadow_bits", "funded", "target"],
    },
    {
        "nav": "Patterns Lab",
        "title": "Key ordering (-x) — every pattern",
        "blurb": (
            "How the next private-key base is chosen each batch.\n"
            "hilbert/sobol/halton = quasirandom · density-map needs a PDF file · auto cycles modes."
        ),
        "items": PATTERNS,
        "default_mode": "address",
        "kind": "pattern",
        "extra_fields": ["density_map"],
    },
    {
        "nav": "Filters Lab",
        "title": "Fuse / bloom / cascade filters",
        "blurb": (
            "How targets are queried: binary fuse, bloom, FuseCascade (48→96→exact).\n"
            "freeze-table BSGS tip: don't rotate slots on month-long runs."
        ),
        "items": FILTERS + [
            ("XorFilter / Ribbon", "gap", "Smaller static filters — research"),
            ("GPU XOR prefilter", "gap", "P0 — device prefilter before derive"),
        ],
        "default_mode": "address",
        "kind": "filter",
        "extra_fields": ["funded"],
    },
    {
        "nav": "Vanity Lab",
        "title": "Vanity · poetry · brainwallet · minikeys",
        "blurb": (
            "vanity: -v prefix · poetry/brainwallet: wordlist→SHA256→key · minikeys: Casascius S…\n"
            "Set vanity prefix or word count, Apply, then Launch from TrueCollider."
        ),
        "items": [
            ("vanity", "live", "Address prefix grind (-v)"),
            ("poetry", "live", "Poetry wordlist keys"),
            ("brainwallet", "live", "Passphrase → SHA256 key"),
            ("minikeys", "live", "Bitcoin minikey space"),
            ("vanity-regex", "research", "Regex / middle / suffix vanity"),
        ],
        "default_mode": "vanity",
        "kind": "vanity",
        "extra_fields": ["vanity", "words"],
    },
    {
        "nav": "Algorithms Lab",
        "title": "Named TrueCollider algorithms",
        "blurb": (
            "OrbitBSGS · GrumpyBSGS · Interleave · HerdHandoff · GaudrySchost · FuseCascade ·\n"
            "Hilbert/Sobol · Shadow160 · CrystalPRNG · MnemonicLattice · PathNova · …\n"
            "Selecting an algorithm maps to the closest live -m / -B / -x / -R."
        ),
        "items": ALGORITHMS,
        "default_mode": "bsgs",
        "kind": "algorithm",
        "extra_fields": [],
    },
    {
        "nav": "GPU Lab",
        "title": "GPU · SIMD · memory · P0 gaps",
        "blurb": (
            "-U none/cuda/opencl/both · -M memory · -A vector SIMD · -t CPU threads.\n"
            "P0 gaps (catalogued, not full kernels yet): CUDA PBKDF2, checksum-first GPU,\n"
            "SOTA kangaroo, device hash160+fuse, multi-coin fuse kernel."
        ),
        "items": RESEARCH_GPU_MNEMONIC[:8] + RESEARCH_ECDLP[:5] + RESEARCH_ADDRESS_FILTERS[:3],
        "default_mode": "address",
        "kind": "gpu",
        "extra_fields": ["gpu", "memory", "vector", "threads"],
    },
    {
        "nav": "Multi-coin Lab",
        "title": "Coins & cross-curve intents",
        "blurb": (
            "Pick -c coin family. Multi-coin fuse / cross-curve are research P0.\n"
            "SOL is ed25519 — not mixed into -c all."
        ),
        "items": [
            ("btc", "live", "Bitcoin P2PKH/P2WPKH/P2TR encodings"),
            ("eth", "live", "ETH keccak"),
            ("ltc", "live", "Litecoin"),
            ("doge", "live", "Dogecoin"),
            ("sol", "live", "Solana ed25519"),
            ("troot", "live", "Taproot x-only"),
            ("all", "live", "Multi secp encode (not SOL)"),
            ("auto", "live", "Detect from target file"),
        ] + list(RESEARCH_MULTICOIN),
        "default_mode": "address",
        "kind": "coin",
        "extra_fields": ["coin"],
    },
    {
        "nav": "BSGS Strategies",
        "title": "Every -B strategy (full list)",
        "blurb": (
            "Sets TrueCollider mode=bsgs and -B to your choice.\n"
            "RAM guide: 8G→k512 · 16G→k1024 · 32G→k2048. Prefer kangaroo when N is huge."
        ),
        "items": BSGS,
        "default_mode": "bsgs",
        "kind": "bsgs_strat",
        "extra_fields": ["k_factor", "handoff_bits", "target"],
    },
    {
        "nav": "Address Subs",
        "title": "Address mode expansions",
        "blurb": "Submodes / orderings for -m address (HD fanout, LDS, multi-coin fuse, …).",
        "items": ADDRESS_SUB,
        "default_mode": "address",
        "kind": "address_sub",
        "extra_fields": ["target", "stride"],
    },
    {
        "nav": "WeakRNG Full",
        "title": "CrystalPRNG + Research weak RNG",
        "blurb": "Historical broken RNG keyspaces. Milk Sad needs -T unixStart:unixEnd.",
        "items": WEAKRNG + list(RESEARCH_WEAKRNG),
        "default_mode": "weakrng",
        "kind": "weakrng",
        "extra_fields": ["timestamp"],
    },
    {
        "nav": "Research 2026",
        "title": "GAP / NOVEL wave — full list",
        "blurb": (
            "Everything from the Research 2026 synthesis.\n"
            "GAP = competitors have · NOVEL = rare · Apply maps to nearest live mode when possible.\n"
            "ANTI items are listed in Directory / Roadmap only — never as Launch recipes."
        ),
        "items": (
            RESEARCH_GPU_MNEMONIC
            + RESEARCH_ECDLP
            + RESEARCH_ADDRESS_FILTERS
            + RESEARCH_WEAKRNG
            + RESEARCH_MULTICOIN
            + RESEARCH_NOVEL_RARE
        ),
        "default_mode": "address",
        "kind": "research",
        "extra_fields": [],
    },
]


def lab_nav_names() -> list[str]:
    return [s["nav"] for s in LAB_SPECS]


def lab_labels(items: list[tuple[str, str, str]]) -> list[str]:
    out = []
    for name, status, _ in items:
        if status == "live":
            out.append(name)
        else:
            out.append(f"{name} ({status})")
    return out or ["(empty)"]
