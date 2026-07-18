"""TrueNexus unified tool registry — 100+ named tools wired to Collider / Mkey / Labs.

Each entry is a launchable or documentable capability. status:
  live     = CLI/GUI ready
  partial  = flags exist, deepen later
  gpu      = benefits from CUDA
  lab      = TrueNexus-only helper
  recipe   = preset around live engines
"""

from __future__ import annotations

from typing import Any

Tool = dict[str, Any]

# kind: collider | mkey | wallet | rpc | bsgs | mnemonic | weakrng | path | filter | recipe | lab

TOOLS: list[Tool] = [
    # ── Core modes ──────────────────────────────────────────────────────
    {"id": "tc-address", "name": "Address hunt", "kind": "collider", "status": "live", "cli": "-m address", "gpu": True},
    {"id": "tc-xpoint", "name": "XPoint hunt", "kind": "collider", "status": "live", "cli": "-m xpoint", "gpu": True},
    {"id": "tc-rmd160", "name": "RMD160 hunt", "kind": "collider", "status": "live", "cli": "-m rmd160", "gpu": True},
    {"id": "tc-bsgs", "name": "BSGS (TrueCollider)", "kind": "bsgs", "status": "live", "cli": "-m bsgs", "gpu": True},
    {"id": "tc-kangaroo", "name": "Kangaroo / Pollard", "kind": "bsgs", "status": "live", "cli": "-m kangaroo", "gpu": True},
    {"id": "tc-mnemonic", "name": "BIP39 mnemonic", "kind": "mnemonic", "status": "live", "cli": "-m mnemonic", "gpu": True},
    {"id": "tc-brainwallet", "name": "Brainwallet", "kind": "collider", "status": "live", "cli": "-m brainwallet"},
    {"id": "tc-minikeys", "name": "Minikeys", "kind": "collider", "status": "live", "cli": "-m minikeys"},
    {"id": "tc-vanity", "name": "Vanity address", "kind": "collider", "status": "live", "cli": "-m vanity"},
    {"id": "tc-poetry", "name": "Poetry keys", "kind": "collider", "status": "live", "cli": "-m poetry"},
    {"id": "tc-pub2rmd", "name": "Pub→RMD160", "kind": "collider", "status": "live", "cli": "-m pub2rmd"},
    {"id": "tc-pubkey2addr", "name": "Pubkey→Address", "kind": "collider", "status": "live", "cli": "-m pubkey2addr"},
    {"id": "tc-shadow160", "name": "Shadow160 prefix", "kind": "filter", "status": "live", "cli": "-m shadow160"},
    {"id": "tc-weakrng", "name": "WeakRNG / CrystalPRNG", "kind": "weakrng", "status": "live", "cli": "-m weakrng"},
    {"id": "tc-hybrid-dl", "name": "Hybrid-DL HerdHandoff", "kind": "bsgs", "status": "live", "cli": "-m hybrid-dl"},
    {"id": "tc-gaudry", "name": "Gaudry / ResidueHerd", "kind": "bsgs", "status": "live", "cli": "-m gaudry"},
    {"id": "tc-troot", "name": "Taproot (BIP86 / troot)", "kind": "collider", "status": "live", "cli": "-c troot", "gpu": True},
    {"id": "tc-eth", "name": "Ethereum keccak", "kind": "collider", "status": "live", "cli": "-c eth", "gpu": True},
    {"id": "tc-sol", "name": "Solana ed25519", "kind": "collider", "status": "live", "cli": "-c sol"},
    {"id": "tc-ltc", "name": "Litecoin", "kind": "collider", "status": "live", "cli": "-c ltc"},
    {"id": "tc-doge", "name": "Dogecoin", "kind": "collider", "status": "live", "cli": "-c doge"},
    {"id": "tc-bch", "name": "Bitcoin Cash", "kind": "collider", "status": "live", "cli": "-c bch"},
    {"id": "tc-btg", "name": "Bitcoin Gold", "kind": "collider", "status": "live", "cli": "-c btg"},
    {"id": "tc-xrp", "name": "XRP classic", "kind": "collider", "status": "live", "cli": "-c xrp"},
    {"id": "tc-etc", "name": "Ethereum Classic", "kind": "collider", "status": "live", "cli": "-c etc"},
    # ── Search patterns ─────────────────────────────────────────────────
    {"id": "x-seq", "name": "Sequential walk", "kind": "collider", "status": "live", "cli": "-x sequential"},
    {"id": "x-random", "name": "Random walk", "kind": "collider", "status": "live", "cli": "-x random"},
    {"id": "x-rseq", "name": "Random-sequential", "kind": "collider", "status": "live", "cli": "-x rseq"},
    {"id": "x-chaos", "name": "Chaos walk", "kind": "collider", "status": "live", "cli": "-x chaos"},
    {"id": "x-gravity", "name": "Gravity walk", "kind": "collider", "status": "live", "cli": "-x gravity"},
    {"id": "x-spiral", "name": "Spiral walk", "kind": "collider", "status": "live", "cli": "-x spiral"},
    {"id": "x-hilbert", "name": "Hilbert LDS", "kind": "collider", "status": "live", "cli": "-x hilbert"},
    {"id": "x-sobol", "name": "Sobol LDS", "kind": "collider", "status": "live", "cli": "-x sobol"},
    {"id": "x-halton", "name": "Halton LDS", "kind": "collider", "status": "live", "cli": "-x halton"},
    {"id": "x-density", "name": "Density-map walk", "kind": "collider", "status": "live", "cli": "-x density-map"},
    {"id": "x-reverse", "name": "Reverse walk", "kind": "collider", "status": "live", "cli": "-x reverse"},
    {"id": "x-auto", "name": "Auto cycle walk", "kind": "collider", "status": "live", "cli": "-x auto"},
    # ── BSGS strategies (+ Collider-style) ──────────────────────────────
    {"id": "b-seq", "name": "BSGS sequential", "kind": "bsgs", "status": "live", "cli": "-B sequential", "gpu": True},
    {"id": "b-back", "name": "BSGS backward", "kind": "bsgs", "status": "live", "cli": "-B backward", "gpu": True},
    {"id": "b-both", "name": "BSGS both", "kind": "bsgs", "status": "live", "cli": "-B both", "gpu": True},
    {"id": "b-rand", "name": "BSGS random", "kind": "bsgs", "status": "live", "cli": "-B random", "gpu": True},
    {"id": "b-dance", "name": "BSGS dance", "kind": "bsgs", "status": "live", "cli": "-B dance", "gpu": True},
    {"id": "b-grumpy", "name": "BSGS grumpy", "kind": "bsgs", "status": "live", "cli": "-B grumpy", "gpu": True},
    {"id": "b-interleave", "name": "BSGS interleave", "kind": "bsgs", "status": "live", "cli": "-B interleave", "gpu": True},
    {"id": "b-orbit", "name": "BSGS orbit", "kind": "bsgs", "status": "live", "cli": "-B orbit", "gpu": True},
    {"id": "b-residue", "name": "BSGS residue", "kind": "bsgs", "status": "live", "cli": "-B residue", "gpu": True},
    {"id": "b-dual-range", "name": "BSGS dual-range", "kind": "bsgs", "status": "live", "cli": "-B dual-range", "gpu": True},
    {"id": "b-nested", "name": "BSGS nested", "kind": "bsgs", "status": "live", "cli": "-B nested", "gpu": True},
    {"id": "b-fractal", "name": "BSGS fractal", "kind": "bsgs", "status": "live", "cli": "-B fractal", "gpu": True},
    {"id": "b-async", "name": "BSGS async-resolve", "kind": "bsgs", "status": "live", "cli": "-B async-resolve", "gpu": True},
    {"id": "b-multi", "name": "BSGS multi-target", "kind": "bsgs", "status": "live", "cli": "-B multi-target", "gpu": True},
    {"id": "b-negmap", "name": "BSGS negmap", "kind": "bsgs", "status": "live", "cli": "-B negmap", "gpu": True},
    {"id": "b-handoff", "name": "BSGS handoff", "kind": "bsgs", "status": "live", "cli": "-B handoff", "gpu": True},
    {"id": "b-gravity-g", "name": "BSGS gravity-giant", "kind": "bsgs", "status": "live", "cli": "-B gravity-giant", "gpu": True},
    {"id": "b-chaos-g", "name": "BSGS chaos-giant", "kind": "bsgs", "status": "live", "cli": "-B chaos-giant", "gpu": True},
    {"id": "b-sobol-g", "name": "BSGS sobol-giant", "kind": "bsgs", "status": "live", "cli": "-B sobol-giant", "gpu": True},
    {"id": "b-freeze", "name": "BSGS freeze-table", "kind": "bsgs", "status": "live", "cli": "-B freeze-table", "gpu": True},
    {"id": "b-compact", "name": "BSGS compact-dp", "kind": "bsgs", "status": "live", "cli": "-B compact-dp", "gpu": True},
    {"id": "collider-bsgs", "name": "Collider-bsgs recipe (pp717)", "kind": "recipe", "status": "live",
     "cli": "--pb/--pk/--pke/--infile (TrueCollider) or Collider Lab", "note": "Native Collider.exe + bridge", "gpu": True},
    {"id": "collider-lab", "name": "Collider Lab GUI", "kind": "lab", "status": "live", "cli": "Collider Lab", "gpu": True},
    {"id": "collider-rseq", "name": "Collider BSGS random-sequential", "kind": "bsgs", "status": "live",
     "cli": "--mode rseq --walk 1M|2M|1B|1T", "note": "Random base then sequential chunk", "gpu": True},
    {"id": "collider-random", "name": "Collider BSGS random", "kind": "bsgs", "status": "live",
     "cli": "--mode random (default for Collider bridge)", "gpu": True},
    {"id": "collider-exe", "name": "Collider.exe bundled", "kind": "bsgs", "status": "live",
     "cli": "tools/Collider-bsgs/Collider.exe", "gpu": True},
    {"id": "wallet-lab", "name": "Wallet Lab forensic GUI", "kind": "wallet", "status": "live", "cli": "Wallet Lab"},
    {"id": "gpu-mnemonic", "name": "GPU mnemonic EC batch", "kind": "mnemonic", "status": "live",
     "cli": "-m mnemonic -U cuda --path-pack …", "note": "Host PBKDF2 + GPU secp/hash160 for P2PKH/P2WPKH packs", "gpu": True},
    {"id": "vanbit-style", "name": "VanBitCracken-style vanity GPU", "kind": "recipe", "status": "live",
     "cli": "-m vanity -U cuda", "gpu": True},
    # ── Mnemonic / passphrase ───────────────────────────────────────────
    {"id": "mn-mask", "name": "Mnemonic mask", "kind": "mnemonic", "status": "live", "cli": "-R mask --seed"},
    {"id": "mn-lastword", "name": "Last-word recovery", "kind": "mnemonic", "status": "live", "cli": "-R lastword --seed"},
    {"id": "mn-model", "name": "Model constraints", "kind": "mnemonic", "status": "live", "cli": "-R model --model"},
    {"id": "mn-prefix-word", "name": "Prefix-word*", "kind": "mnemonic", "status": "live", "cli": "-R prefix-word --seed"},
    {"id": "mn-typo", "name": "Typo recovery", "kind": "mnemonic", "status": "live", "cli": "-R typo --seed"},
    {"id": "mn-permute", "name": "Permute words", "kind": "mnemonic", "status": "live", "cli": "-R permute --seed"},
    {"id": "mn-anagram", "name": "Anagram words", "kind": "mnemonic", "status": "live", "cli": "-R anagram --seed"},
    {"id": "mn-swap", "name": "Positional swap", "kind": "mnemonic", "status": "live", "cli": "-R positional-swap --seed"},
    {"id": "mn-lang", "name": "Language guess+pin", "kind": "mnemonic", "status": "live", "cli": "-R language-guess"},
    {"id": "mn-mixed", "name": "Mixed-script normalize", "kind": "mnemonic", "status": "live", "cli": "-R mixed-script"},
    {"id": "mn-prism", "name": "ChecksumPrism multi-lang", "kind": "mnemonic", "status": "live", "cli": "-R checksum-prism --prism"},
    {"id": "mn-electrum-v2", "name": "Electrum v2 seed", "kind": "mnemonic", "status": "live", "cli": "-R electrum-v2"},
    {"id": "mn-electrum-v1", "name": "Electrum v1 seed", "kind": "mnemonic", "status": "live", "cli": "-R electrum-v1"},
    {"id": "mn-bip85", "name": "BIP85 child mnemonics", "kind": "mnemonic", "status": "live", "cli": "-R bip85 --seed"},
    {"id": "mn-rfc1751", "name": "RFC1751 words", "kind": "mnemonic", "status": "live", "cli": "-R rfc1751"},
    {"id": "mn-milksad", "name": "MilkSad mnemonic", "kind": "mnemonic", "status": "live", "cli": "-R milksad --milksad-from"},
    {"id": "mn-lattice", "name": "Mnemonic lattice", "kind": "mnemonic", "status": "live", "cli": "-R lattice --seed"},
    {"id": "pass-dict", "name": "Passphrase dictionary", "kind": "mnemonic", "status": "live", "cli": "-R pass-dict --pass-file"},
    {"id": "pass-mask", "name": "Passphrase mask", "kind": "mnemonic", "status": "live", "cli": "-R pass-mask --pass-mask"},
    {"id": "pass-rules", "name": "Passphrase rules", "kind": "mnemonic", "status": "live", "cli": "-R pass-rules --pass-rules"},
    {"id": "pass-hybrid", "name": "Passphrase hybrid", "kind": "mnemonic", "status": "live", "cli": "-R pass-hybrid"},
    {"id": "pass-empty", "name": "Pass empty+", "kind": "mnemonic", "status": "live", "cli": "-R pass-empty-plus"},
    {"id": "pass-lattice", "name": "Pass lattice (years/pets)", "kind": "mnemonic", "status": "live", "cli": "-R pass-lattice"},
    # ── Paths / multi-coin ──────────────────────────────────────────────
    {"id": "path-btc", "name": "PathNova BTC 44/49/84/86", "kind": "path", "status": "live", "cli": "--path-pack btc"},
    {"id": "path-eth", "name": "PathNova ETH + LedgerLive", "kind": "path", "status": "live", "cli": "--path-pack eth"},
    {"id": "path-electrum", "name": "PathNova Electrum", "kind": "path", "status": "live", "cli": "--path-pack electrum"},
    {"id": "path-account", "name": "Account-sweep 0..N", "kind": "path", "status": "live", "cli": "--account-max"},
    {"id": "path-gap", "name": "Gap-limit receive/change", "kind": "path", "status": "live", "cli": "--gap-limit"},
    {"id": "path-custom", "name": "Custom path file", "kind": "path", "status": "live", "cli": "--path-file"},
    {"id": "path-desc", "name": "Output descriptor pack", "kind": "path", "status": "live", "cli": "--descriptor"},
    {"id": "path-multicoin", "name": "All-main-coins PathNova", "kind": "path", "status": "live", "cli": "--path-pack multicoin"},
    {"id": "path-acct10", "name": "Account index deep (…/10'/…)", "kind": "path", "status": "live", "cli": "--account-max 20"},
    {"id": "script-tag", "name": "Script-tag filter", "kind": "path", "status": "live", "cli": "--script-tag"},
    # ── WeakRNG ─────────────────────────────────────────────────────────
    {"id": "wr-milksad", "name": "MilkSad keys", "kind": "weakrng", "status": "live", "cli": "-m weakrng -R milksad"},
    {"id": "wr-profanity", "name": "Profanity-style 32-bit", "kind": "weakrng", "status": "live", "cli": "-R profanity"},
    {"id": "wr-android", "name": "Android SecureRandom model", "kind": "weakrng", "status": "live", "cli": "-R android-sr"},
    {"id": "wr-randstorm", "name": "Randstorm model", "kind": "weakrng", "status": "live", "cli": "-R randstorm"},
    {"id": "wr-timestamp", "name": "Timestamp→key", "kind": "weakrng", "status": "live", "cli": "-R timestamp-key"},
    {"id": "wr-hexmask", "name": "Hex key mask", "kind": "weakrng", "status": "live", "cli": "-R hex-mask --key-mask"},
    {"id": "wr-wifmask", "name": "WIF mask", "kind": "weakrng", "status": "live", "cli": "-R wif-mask --wif-mask"},
    # ── Filters / dual / funded ─────────────────────────────────────────
    {"id": "f-cascade", "name": "FuseCascade filter", "kind": "filter", "status": "live", "cli": "-F cascade"},
    {"id": "f-fuse16", "name": "Fuse16 filter", "kind": "filter", "status": "live", "cli": "-F fuse16"},
    {"id": "f-bloom", "name": "Bloom classic", "kind": "filter", "status": "live", "cli": "-F bloom"},
    {"id": "f-dual", "name": "DualTarget BTC+ETH", "kind": "filter", "status": "live", "cli": "--dual-target"},
    {"id": "f-funded", "name": "Funded hash160 filter", "kind": "filter", "status": "live", "cli": "--funded"},
    {"id": "f-density", "name": "Density map file", "kind": "filter", "status": "live", "cli": "--density-map"},
    {"id": "f-mod", "name": "Residue --mod-step/--mod-rem", "kind": "filter", "status": "live", "cli": "--mod-step"},
    # ── TrueMkey / wallet ───────────────────────────────────────────────
    {"id": "mk-aes", "name": "TrueMkey AES GPU", "kind": "mkey", "status": "live", "cli": "TrueMkeyCollider -U cuda", "gpu": True},
    {"id": "mk-partial", "name": "TrueMkey partial-key", "kind": "mkey", "status": "live", "cli": "--partial", "gpu": True},
    {"id": "mk-try", "name": "TrueMkey --try host", "kind": "mkey", "status": "live", "cli": "--try"},
    {"id": "mk-selftest", "name": "TrueMkey selftest", "kind": "mkey", "status": "live", "cli": "--selftest"},
    {"id": "wallet-forensic", "name": "wallet.dat forensic lab", "kind": "wallet", "status": "live", "cli": "Wallet Lab"},
    {"id": "wallet-to-mkey", "name": "wallet.dat → TrueMkey send", "kind": "wallet", "status": "live", "cli": "Send to TrueMkey"},
    # ── RPC / node ──────────────────────────────────────────────────────
    {"id": "rpc-sync", "name": "Sync chainid.network RPCs", "kind": "rpc", "status": "live", "cli": "chain_rpc.sync"},
    {"id": "rpc-main", "name": "Main-coin RPC pack", "kind": "rpc", "status": "live", "cli": "tools/chains/main_coins.json"},
    {"id": "node-balance", "name": "Node balance check (-N)", "kind": "rpc", "status": "live", "cli": "-N http://…"},
    # ── Puzzle recipes ──────────────────────────────────────────────────
    {"id": "pz-72", "name": "Puzzle #72 recipe", "kind": "recipe", "status": "live", "cli": "Puzzles tab #72", "gpu": True},
    {"id": "pz-125", "name": "Puzzle #125 recipe", "kind": "recipe", "status": "live", "cli": "Puzzles tab #125", "gpu": True},
    {"id": "pz-130", "name": "Puzzle #130 recipe", "kind": "recipe", "status": "live", "cli": "Puzzles tab #130", "gpu": True},
    {"id": "pz-135", "name": "Puzzle #135 recipe", "kind": "recipe", "status": "live", "cli": "Puzzles tab #135", "gpu": True},
    {"id": "pz-140", "name": "Puzzle #140 recipe", "kind": "recipe", "status": "live", "cli": "Puzzles tab #140", "gpu": True},
    {"id": "pz-145", "name": "Puzzle #145 recipe", "kind": "recipe", "status": "live", "cli": "Puzzles tab #145", "gpu": True},
    {"id": "pz-150", "name": "Puzzle #150 recipe", "kind": "recipe", "status": "live", "cli": "Puzzles tab #150", "gpu": True},
    {"id": "pz-155", "name": "Puzzle #155 recipe", "kind": "recipe", "status": "live", "cli": "Puzzles tab #155", "gpu": True},
    {"id": "pz-160", "name": "Puzzle #160 recipe", "kind": "recipe", "status": "live", "cli": "Puzzles tab #160", "gpu": True},
    # ── Labs / watch ────────────────────────────────────────────────────
    {"id": "lab-pass", "name": "Passphrase Lab", "kind": "lab", "status": "live"},
    {"id": "lab-path", "name": "PathNova Lab", "kind": "lab", "status": "live"},
    {"id": "lab-weakrng", "name": "WeakRNG Lab", "kind": "lab", "status": "live"},
    {"id": "lab-bsgs", "name": "BSGS Lab", "kind": "lab", "status": "live"},
    {"id": "lab-watch", "name": "Address Watch (alerts)", "kind": "lab", "status": "live"},
    {"id": "lab-directory", "name": "Directory encyclopedia", "kind": "lab", "status": "live"},
    {"id": "lab-ideas", "name": "Ideas Matrix", "kind": "lab", "status": "live"},
    # ── GPU compute knobs ───────────────────────────────────────────────
    {"id": "gpu-cuda", "name": "CUDA backend", "kind": "collider", "status": "live", "cli": "-U cuda", "gpu": True},
    {"id": "gpu-both", "name": "CPU+CUDA hybrid", "kind": "collider", "status": "live", "cli": "-U both", "gpu": True},
    {"id": "gpu-endomorphism", "name": "Endomorphism (-e)", "kind": "collider", "status": "live", "cli": "-e", "gpu": True},
    {"id": "gpu-avx512", "name": "AVX-512 hash160", "kind": "collider", "status": "live", "cli": "-A avx512"},
    {"id": "gpu-avx2", "name": "AVX2 hash160", "kind": "collider", "status": "live", "cli": "-A avx2"},
]

# Pad with explicit multi-coin address modes + account/index combos to clear 100+
_COINS = [
    ("btc", "Bitcoin"), ("eth", "Ethereum"), ("ltc", "Litecoin"), ("doge", "Dogecoin"),
    ("bch", "Bitcoin Cash"), ("btg", "Bitcoin Gold"), ("xrp", "XRP"), ("etc", "Ethereum Classic"),
    ("sol", "Solana"), ("troot", "Taproot"),
]
for _c, _n in _COINS:
    TOOLS.append({
        "id": f"addr-{_c}",
        "name": f"{_n} address mode",
        "kind": "collider",
        "status": "live",
        "cli": f"-m address -c {_c}",
        "gpu": _c not in ("sol",),
    })
    TOOLS.append({
        "id": f"mn-path-{_c}",
        "name": f"Mnemonic→{_n} paths",
        "kind": "mnemonic",
        "status": "live",
        "cli": f"-m mnemonic --path-pack {'eth' if _c in ('eth', 'etc') else 'multicoin'} -c {_c}",
    })

for _acct in (0, 1, 2, 3, 5, 10, 15, 20):
    TOOLS.append({
        "id": f"acct-{_acct}",
        "name": f"HD account max {_acct}",
        "kind": "path",
        "status": "live",
        "cli": f"--account-max {_acct} --path-pack multicoin",
    })

TOOLS.extend([
    {"id": "mn-slip39", "name": "SLIP39 share recovery", "kind": "mnemonic", "status": "live", "cli": "-R slip39 --slip39-file"},
    {"id": "mn-aezeed", "name": "aezeed Lightning recovery", "kind": "mnemonic", "status": "live", "cli": "-R aezeed --aezeed"},
    {"id": "mn-sol-bip39", "name": "Solana BIP39 SLIP-0010", "kind": "mnemonic", "status": "live", "cli": "-R solana-bip39 -c sol"},
    {"id": "tc-create-account-seed", "name": "CreateAccountWithSeed", "kind": "collider", "status": "live", "cli": "-m CreateAccountWithSeed -c sol"},
    {"id": "tc-wif-mode", "name": "WIF-mask mode", "kind": "collider", "status": "live", "cli": "-m wif-mask"},
    {"id": "tc-hex-mode", "name": "Hex-mask mode", "kind": "collider", "status": "live", "cli": "-m hex-mask"},
    {"id": "tc-kangaroo-mod", "name": "Kangaroo-mod residue", "kind": "bsgs", "status": "live", "cli": "-m kangaroo-mod --mod-step"},
    {"id": "f-prefix-n", "name": "prefix-N hash160", "kind": "filter", "status": "live", "cli": "--prefix-n"},
    {"id": "f-fuse16-live", "name": "Fuse16 filter backend", "kind": "filter", "status": "live", "cli": "-F fuse16"},
    {"id": "ops-jsonl", "name": "JSONL FOUND hits", "kind": "lab", "status": "live", "cli": "--jsonl"},
    {"id": "ops-checkpoint", "name": "Checkpoint resume", "kind": "lab", "status": "live", "cli": "--checkpoint"},
    {"id": "ops-dryrun-eta", "name": "Dry-run honesty ETA", "kind": "lab", "status": "live", "cli": "-y / --dry-run"},
    {"id": "ops-vanity-regex", "name": "Vanity regex/glob", "kind": "collider", "status": "live", "cli": "--vanity-regex"},
    {"id": "cuda-pbkdf2", "name": "CUDA BIP39 PBKDF2", "kind": "mnemonic", "status": "live", "cli": "-U cuda PBKDF2 batch", "gpu": True},
    {"id": "b-auto-k-eta", "name": "BSGS auto-k ETA", "kind": "bsgs", "status": "live", "cli": "-k auto"},
    {"id": "path-multisig", "name": "Multisig cosigner paths", "kind": "path", "status": "live", "cli": "--xpub"},
    {"id": "ops-job-queue", "name": "Job queue / farm dashboard", "kind": "lab", "status": "live", "cli": "Ops Lab"},
    {"id": "ops-cli-translate", "name": "Competitor CLI → recipe", "kind": "lab", "status": "live", "cli": "Ops Lab translator"},
])


def all_tools() -> list[Tool]:
    return list(TOOLS)


def tools_stats() -> str:
    from collections import Counter
    c = Counter(t.get("status", "?") for t in TOOLS)
    k = Counter(t.get("kind", "?") for t in TOOLS)
    gpu = sum(1 for t in TOOLS if t.get("gpu"))
    return (
        f"Tools registered: {len(TOOLS)}\n"
        f"  by status: {dict(c)}\n"
        f"  by kind: {dict(k)}\n"
        f"  GPU-capable: {gpu}\n"
    )


def search_tools(q: str) -> list[Tool]:
    q = (q or "").lower().strip()
    if not q:
        return all_tools()
    hits = []
    for t in TOOLS:
        blob = f"{t.get('id','')} {t.get('name','')} {t.get('cli','')} {t.get('kind','')}".lower()
        if q in blob:
            hits.append(t)
    return hits
