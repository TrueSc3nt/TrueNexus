# TrueCollider — Research Ideas for Improvement

**Local research document only. Do not publish or push this file.**  
Author session: deep survey of TrueCollider’s current modes + open literature / competing tools (2024–2026) + original algorithm proposals.  
Target: invent modes and algorithms that are *not* already first-class in TrueCollider, and that most Bitcoin GPU hunters have never shipped as a unified product.

---

## 0. Codebase-verified notes (from local inventory)

Confirmed in `keyhunt.cpp` / GPU dispatcher (not assumptions):

- Mnemonic always calls `mnemonic_to_seed(mnemonic, "", …)` — passphrase API exists but is never searched.
- Mnemonic paths are hard-coded BIP-44/49/84 with **coin type `0'`**; `-W` only changes address *encoding* to ETH keccak — it does **not** switch to `m/44'/60'/…`.
- Mnemonic has no change chain (`/1/N`), no BIP-86, no custom `-p`, no SOL/SLIP-0010 path.
- CUDA BSGS GRP assist exists but is still correctness-first (serial giant cycles); kangaroo is not RCKangaroo-class.
- Dead CLI residue: `-E` appears in getopt with no handler — free flag letter for a future mode.
- Extra white space not fully covered elsewhere: Solana `CreateAccountWithSeed` vanity, `binary_fuse16` for huge target sets, WIF/hex-mask mutation as its own mode, checkpoint/resume of RNG + mnemonic combination cursors.

---

## 0b. What TrueCollider already has (baseline — do not reinvent)

| Area | Already present |
|------|-----------------|
| Core modes (`-m`) | `address`, `rmd160`, `xpoint`, `bsgs`, `kangaroo`, `vanity`, `minikeys`, `mnemonic`, `poetry`, `brainwallet`, `pubkey2addr` |
| Key ordering (`-x`) | sequential, random, chaos, gravity, spiral, reverse, auto |
| BSGS walk (`-B`) | sequential, backward, both, random, dance |
| Filters | Bloom + **binary fuse** (already ahead of many forks) |
| Crypto stack | secp256k1 SIMD hash160, CUDA EC assist, OpenCL hash, ed25519/SOL, endomorphism `-e` |
| Mnemonic today | Random BIP-39 (12–24), checksum, PBKDF2, BIP-44/49/84, 10 languages, ETH `-W`, index depth `-D` |

**Honest gap:** mnemonic mode is currently *random full-phrase generation* with empty passphrase and three hard-coded BTC paths. It is **not** a recovery suite. BSGS is classical Keyhunt-style with fuse tiers; kangaroo exists but is not RCKangaroo-class yet. Address/rmd160 have chaos/gravity/spiral ordering but no weak-RNG, collision, or residue-class engines.

Everything below is designed to fill those gaps with **new product surfaces** TrueCollider could own.

---

## 1. North-star product vision

Turn TrueCollider into the first open toolkit that unifies:

1. **Interval ECDLP** (BSGS + kangaroo + research variants)  
2. **Hash160 / address hunting** (with weak-entropy and space-filling orderings)  
3. **Full mnemonic / seed ecosystem** (recovery, not just random grind)

…under one CLI, one filter stack, one FOUND_* hit format, and one GPU dispatcher.

---

## 2. Brand-new algorithms (TrueCollider-original names)

These are *composites* of real math + TrueCollider’s existing chaos/gravity/spiral DNA. Most Bitcoin hunters never expose them as named modes.

### 2.1 OrbitBSGS (endomorphism-collapsed baby table)

**Idea:** secp256k1 has efficient endomorphism `(λ, β)`. Instead of storing baby points `i·G`, store **orbit representatives** `{±P, ±λP, ±λ²P}` as one filter entry with a 3-bit orbit tag. Giant steps query the orbit-normalized x-coordinate.

**Why new for TrueCollider:** `-e` already exists for address mode; BSGS rarely gets full orbit collapse + fuse filter + GPU GRP in one stack.  
**Expected win:** ~√3–√6 smaller baby table for same coverage (theory-dependent; measure on puzzle 70–90).  
**Flag sketch:** `-m bsgs -B orbit` or `-m bsgs --orbit`.

### 2.2 HerdHandoff (BSGS → Kangaroo cascade)

**Idea:** Run coarse BSGS / giant steps until a *near-miss* or a distinguished-point density spike localizes the key to a sub-interval of size `2^k` (e.g. 40–48 bits). Automatically spawn kangaroo herds only inside that pocket.

**Why new:** Tools pick either BSGS *or* kangaroo. Almost nobody auto-handoffs mid-run with a shared checkpoint format.  
**Flag sketch:** `-m hybrid-dl -r START:END -H 44` (handoff bit width).

### 2.3 GrumpyBSGS (Bernstein–Lange “two grumpy giants and a baby”)

**Idea:** Classic BSGS uses one baby ladder + one giant ladder. Grumpy giants use **two giant progressions with coprime steps** (`n` and `n+1`) against one baby set — higher average-case success probability for the same multiply budget (ePrint 2012/294).

**Why rare:** Almost no Bitcoin puzzle tool implements this. Academic, high memory, excellent for mid-range pubkeys when RAM is available.  
**Flag sketch:** `-m bsgs -B grumpy -n … -k …`.

### 2.4 InterleaveBSGS (Pollard interleaved average-case BSGS)

**Idea:** Alternate baby and giant work so expected cost drops toward ~1.33√N (negation → ~0.94√N) instead of textbook 1.5√N average.

**Why new here:** Keyhunt BSGS is usually “build all babies then walk giants.” Interleaving changes cache behavior and GPU scheduling.  
**Flag sketch:** `-m bsgs -B interleave`.

### 2.5 GaudrySchost / MultiDim-DL (modular & multi-constraint ECDLP)

**Idea:** When the key is known to satisfy constraints like `k ≡ r (mod m)` **or** a 2D lattice (e.g. `k = a·A + b·B` in a box), use Gaudry–Schost tame/wild birthday walks instead of 1D kangaroo.

**TrueCollider twist — ResidueHerd:** combine with `-x gravity` so residue classes that produce near-misses get more walkers.  
**Flag sketch:** `-m gaudry -mod 0x10:0x3` (M:R) or `-m kangaroo --mod-step M --mod-rem R`.

### 2.6 FuseCascade (multi-resolution filter pipeline)

**Idea:** Three fuse filters at different bit depths:

1. **Coarse** — first 48 bits of hash160 / x-coord (tiny, ultra-fast reject)  
2. **Mid** — 96 bits  
3. **Exact** — full element + binary search / exact table  

**Why new:** TrueCollider already has 3-tier BSGS blooms; generalize that pattern to *address* and *rmd160* for billion-scale target files without LMDB.  
**Flag sketch:** `-F cascade` (global filter strategy).

### 2.7 HilbertStride / SobolWalk (quasirandom key orderings)

**Idea:** Replace or extend chaos/spiral with:

- **Hilbert curve** over the bit-range (preserves locality → gravity mode becomes meaningful)  
- **Sobol / Halton** low-discrepancy sequences (better coverage than LCG/random; less clustering)

**Why interesting:** Chaos (logistic map) is cool branding; Sobol/Hilbert are mathematically stronger for “cover the cube evenly.” Almost unused in keyhunt forks.  
**Flag sketch:** `-x hilbert`, `-x sobol`.

### 2.8 Shadow160 (partial hash160 / birthday collider)

**Idea:** Not full address recovery — hunt **prefix collisions** on RIPEMD-160 (e.g. first 40–80 bits) using distinguished-point birthday walks (VanitySearch / BTCCollider lineage), then verify against funded hash160 sets.

**Why different from `-m rmd160`:** rmd160 today is *exact match grind*. Shadow160 is *collision search* with DP herds — different algorithm class.  
**Flag sketch:** `-m shadow160 -s 48` (collision bits).

### 2.9 CrystalPRNG (weak-entropy keyspace engines)

**Idea:** First-class modes that *enumerate known broken RNG keyspaces* instead of 256-bit random:

| Submode | Historical flaw | Search space |
|---------|-----------------|--------------|
| `milksad` | Libbitcoin Explorer MT19937 (CVE-2023-39910) | ~2³² + time window |
| `randstorm` | BitcoinJS / browser weak entropy | browser-version dependent |
| `android-sr` | Android SecureRandom (2013) | reduced entropy seeds |
| `profanity` | 32-bit seed ETH vanity | 2³² |
| `timestamp-key` | keys = f(unix time) / counter | user `-T` window × stride |

**Why new as product:** Scattered research tools exist; almost none ship as `-m address -x milksad` inside a multi-coin hunter with fuse filters.  
**Flag sketch:** `-m weakrng -R milksad -T start:end`.

### 2.10 MnemonicLattice (checksum lattice search)

**Idea:** Treat BIP-39 as a lattice over `GF(2)` checksum constraints. Unknown word positions become free variables; valid checksums form a coset. Enumerate **only checksum-valid candidates** (already implied by last-word math) using a bit-index Gray code over free entropy bits — not word-by-word 2048 loops.

**Why advanced:** Most tools loop words then reject checksum. Lattice enumeration can stream only valid seeds into PBKDF2.  
**Flag sketch:** `-m mnemonic -R lattice -f mask.txt`.

### 2.11 ChecksumPrism (multi-language same-entropy)

**Idea:** One entropy blob → render as EN/ES/FR/… wordlists simultaneously; check all language encodings against targets in one pass (TrueCollider already preloads 10 lists — this uses them *structurally*, not round-robin random).

**Flag sketch:** `-m mnemonic -L prism`.

### 2.12 PathNova (derivation path explosion, budgeted)

**Idea:** For each candidate seed, expand a **wallet fingerprint pack**:

- BIP-44/49/84/86 (BTC)  
- BIP-44 coin-types (LTC, DOGE, ETH, …)  
- Electrum `m/0/` / `m/1/`  
- Ledger Live quirks, Trust, MetaMask account indices  
- change=0/1, account 0..A, index 0..G  

Budgeted by `-D` and a YAML/JSON **path pack** so users don’t pay 10,000× by accident.

**Flag sketch:** `-m mnemonic --path-pack ledger-eth.json -D 20`.

---

## 3. New BSGS modes (beyond sequential / dance / reverse)

Proposed `-B` / submode expansion:

| Mode | Algorithm class | Best when | Novelty vs current TrueCollider |
|------|-----------------|-----------|----------------------------------|
| `grumpy` | 2 giants + 1 baby | Mid ranges, lots of RAM | Academic → productized |
| `interleave` | Average-case BSGS | Same as classic BSGS | Better constants |
| `orbit` | Endomorphism classes | secp256k1 only | Orbit table + fuse |
| `residue` | BSGS on arithmetic progression | `k ≡ r (mod m)` known | Modular reduction of N |
| `dual-range` | Shared baby table, 2 giant fronts | Two candidate ranges | Shared table amortization |
| `nested` / `fractal` | Hierarchical BSGS | Huge N, staged RAM | Coarse table → fine table |
| `async-resolve` | Giant GPU + CPU baby verify | Multi-GPU | PSCKangaroo-style queue |
| `multi-target` | One baby table, many pubkeys | Puzzle lists / cluster pubs | Batch pubkeys efficiently |
| `negmap` | Negation map on giant walk | Always (secp) | √2-ish constant cut |
| `handoff` | BSGS until pocket, then kangaroo | Large puzzles | Hybrid pipeline |
| `gravity-giant` | Giant starts biased by near-misses | After warm-up | Uses TrueCollider gravity DNA |
| `chaos-giant` | Logistic-map giant starts | Exploration | Unique branding + ergodicity |
| `sobol-giant` | LDS giant starts | Coverage proof | Stronger than random `-B` |
| `freeze-table` | Never rotate fuse slots once full | Week-long runs | Avoids FP explosion (PSC lesson) |
| `compact-dp` | 16-byte DP entries for hybrid | Kangaroo/BSGS bridge | Memory density |

### Implementation notes for BSGS upgrades

1. **GPU GRP today is serial (`<<<1,1>>>`)** — next leap is batched giant cycles per SM, not more CPU modes.  
2. **Auto-k from free RAM** (`-k auto` exists in docs) should also print *expected√N time* and recommend kangaroo when N is too large.  
3. **Checkpoint format** should store: baby fuse checksums, giant offset, RNG/LDS state, mode phase (for auto/gravity).  
4. **Multi-GPU:** one device builds/holds baby fuse in VRAM; others stream giants (producer/consumer).

---

## 4. New address & rmd160 modes

### 4.1 Address mode expansions (`-m address` submodes or `-x` / `-R`)

| Idea | What it does | Why it matters |
|------|--------------|----------------|
| `hilbert` / `sobol` | Quasirandom coverage of `-r` | Better than random/chaos for unknown distributions |
| `density-map` | Load a prior PDF over the range (e.g. timestamps, puzzle heuristics) and sample proportionally | Turns gravity into *informed* Bayesian search |
| `multi-coin-fuse` | One EC point → BTC hash160 + ETH keccak + taproot x-only in one pass | Already multi-coin; fuse the *hot loop* |
| `hd-fanout` | Each base key → BIP-32 children before filter (`-p` exists; make default packs + change chain) | Catches HD wallets from “raw key” lists |
| `vanity-regex` | Beyond prefix `-v`: regex / suffix / middle match | SOL grinders have this; BTC rarely |
| `balance-prior` | Optional offline snapshot of funded hash160 → search denser around historical weak keyspaces | Research / recovery framing |
| `stream-targets` | mmap / LMDB target DB for >100M addresses | BitcoinAddressFinder pattern |
| `gpu-hash160-device` | Finish CUDA path so hash+fuse stay on GPU | Biggest practical speed win |
| `stride-adaptive` | Auto-tune `-I` from measured bloom hit rate | Self-tuning hunter |
| `pair-compress` | Always compute compressed+uncompressed from one EC mul | Standard optimization, make default “both” cheaper |

### 4.2 RMD160-specific modes (`-m rmd160`)

| Idea | Description |
|------|-------------|
| `exact` (current) | Full 20-byte match via fuse |
| `prefix-N` | Match first N nybbles of hash160 (fast prefilter contests / research) |
| `shadow160` | Birthday DP collision toward target set (see §2.8) |
| `funded-only` | Load only hash160s with UTXO snapshot; ignore empty |
| `p2pkh/p2wpkh/p2tr-tags` | Tag each target with script type; skip wrong encode path |
| `rmd-of-xonly` | Taproot / x-only pipelines without Base58 |
| `dual-bloom-device` | Keep fuse in VRAM; CUDA writes hash160 directly into query |
| `cascade-filter` | FuseCascade specialized for 20-byte keys |
| `unsorted-ingest` | Build fuse from unsorted .rmd dumps without forcing sort first (streaming construction) |

### 4.3 Shared address/rmd160 algorithm: **CascadeHunt**

Pipeline that no competitor brands clearly:

```
privkey batch
  → GPU EC
  → hash160 (device)
  → coarse fuse (48-bit)
  → mid fuse
  → exact table
  → optional online -N balance
  → FOUND_*.txt
```

Add **early-exit stats**: if coarse hit-rate is absurd, warn that filter is saturated / targets malformed.

---

## 5. Mnemonic section — complete ecosystem (highest priority)

### 5.1 Reality check on current `-m mnemonic`

Today TrueCollider:

- Generates **random** valid BIP-39 phrases  
- Uses **empty** passphrase  
- Derives only **m/44'/0'/0'/0/i**, **m/49'/…**, **m/84'/…**  
- Optional ETH keccak via `-W`  
- Light GPU batch on derived privkeys  

It does **not** yet do recovery. The ideas below turn mnemonic into a full suite.

---

### 5.2 Proposed mnemonic submodes (`-m mnemonic -R <submode>`)

#### A. Recovery / constraint modes (must-have)

| Submode | User input | Engine |
|---------|------------|--------|
| `mask` | `word ? ? know …` or `x` placeholders | Enumerate unknown positions; checksum prune; PBKDF2 survivors |
| `model` | Constraint file: per-position candidate lists, optional/unknown slots | CryptoRecover “Mode 0” style — **highest real-world recovery value** |
| `lastword` | 11/23 known words | Only 128/256 valid last words (12/24) — **16× cut** |
| `prefix-word` | `?aba` / `aban*` partial spelling | Expand to BIP-39 candidates by prefix/edit distance |
| `typo` | Full phrase + max Hamming / Levenshtein | Wrong-word / swapped-adjacent recovery |
| `permute` | Known multiset of words, unknown order | `n!` with checksum prune (only feasible for small n) |
| `anagram` | Same as permute but allow 1–2 substitutions | Damaged paper recovery |
| `positional-swap` | Two positions swapped | Common human error — O(n²) tiny |
| `language-guess` | Phrase in unknown BIP-39 language | Try all 10 lists (ChecksumPrism) |
| `mixed-script` | NFC/NFKD normalization, Japanese full-width, etc. | Wallet import quirks |

#### B. Passphrase modes (“25th word”)

| Submode | Description |
|---------|-------------|
| `pass-dict` | Known mnemonic + dictionary lines |
| `pass-mask` | Hashcat-style `?l?l?d?d` masks |
| `pass-rules` | Dictionary × rule file (`best64`, custom) on GPU |
| `pass-hybrid` | dict + mask append/prepend |
| `pass-empty-plus` | Also test empty, spaces, wallet-default passphrases |

**Pipeline:** mnemonic fixed → salt `mnemonic`+pass → PBKDF2 → path pack → filter.

#### C. Alternate seed ecosystems

| Submode | Standard | Notes |
|---------|----------|-------|
| `electrum-v1` | Old Electrum 1626-word | Heavy stretch; still live for ancient wallets |
| `electrum-v2` | Electrum seed version bytes | **4096× prefilter** before PBKDF2 — huge win |
| `slip39` | Shamir shares (Trezor) | Share repair + combine |
| `aezeed` | LND aezeed | Lightning node recovery |
| `bip85` | Child mnemonic from parent | Search child index space |
| `rfc1751` | Ancient 128-bit word encoding | Curiosity + edge cases (CUDAHUNT keeps this) |
| `solana-bip39` | ed25519 path packs | TrueCollider already has SOL address mode |

#### D. Derivation / wallet packs

| Submode | Behavior |
|---------|----------|
| `paths-btc` | 44/49/84/86 + change 0/1 |
| `paths-eth` | `m/44'/60'/0'/0/i`, Ledger Live `m/44'/60'/0'/i` |
| `paths-electrum` | `m/0/i`, `m/1/i` gap limits |
| `paths-custom` | `-p` multipath file |
| `account-sweep` | account 0..A × index 0..G |
| `multisig-cosigner` | xpub + candidate seed as cosigner (advanced) |

#### E. Search strategy modes (mnemonic-specific `-x`)

| Strategy | Meaning |
|----------|---------|
| `checksum-first` | Never PBKDF2 invalid phrases |
| `entropy-guided` | Fill most constrained slots first (max prune) |
| `freq-prior` | Rank BIP-39 words by empirical wallet frequency |
| `lattice` | MnemonicLattice bit enumeration (§2.10) |
| `checkpointed` | Resume cursor into combination space |
| `random-dedup` | Random walk + bloom of seen entropy hashes |
| `producer-split` | GPU A: candidates+checksum; GPU B: PBKDF2; GPU C: EC (hashcat issue #4606 pattern) |

---

### 5.3 Novel mnemonic algorithms (TrueCollider-original)

#### 5.3.1 WordOrbit

If the user remembers “it was something like *river*”, expand via:

- edit distance ≤ 2 within BIP-39  
- phonetic / metaphone  
- shared 4-letter prefix  
- adjacent keyboard typos  

Feed expansion into `model` mode. Competitors mention this; few fuse it with multi-path GPU and fuse filters.

#### 5.3.2 ChecksumWindow

When *exactly one* unknown word is **not** the last word, precompute which replacements keep checksum validity using incremental SHA-256 state — avoid full re-hash of all entropy for each trial.

#### 5.3.3 SeedCascadeVerify (progressive verification pipeline)

Ordered cheapest → most expensive:

1. Wordlist membership  
2. Checksum / Electrum version  
3. PBKDF2  
4. Derive only path index 0  
5. Coarse fuse  
6. Full path pack on survivors only  

This is how 4-missing-word recoveries become practical.

#### 5.3.4 DualTarget Anchor

If user knows **two** addresses from the same seed (BTC + ETH, or two indices), use the second as an almost-free reject after first path hit — collapses false positives from bloom and wrong path packs.

#### 5.3.5 EntropyTimeline (Milk Sad for mnemonics)

`bx seed` / MT19937 mnemonic generation: enumerate time-seeded entropy → BIP-39 → path pack.  
Wire as `-m mnemonic -R milksad -T 2017-01-01:2017-12-31`.

#### 5.3.6 PhraseGravity

When a near-miss occurs (checksum ok, path ok, fuse almost-hit / wrong index), bias next trials toward neighboring word indices and nearby derivation indices — **gravity mode for seed space**.

---

### 5.4 GPU architecture for mnemonic (critical)

PBKDF2-HMAC-SHA512 (2048 iters) dominates. Recommended TrueCollider architecture:

```
┌─────────────┐    valid seeds     ┌──────────────┐    privkeys    ┌─────────────┐
│ Producer GPU │ ───────────────► │ PBKDF2 GPUs  │ ─────────────► │ EC+fuse GPU │
│ checksum gen │                  │ (N devices)  │                │ hash160/eth │
└─────────────┘                   └──────────────┘                └─────────────┘
```

- Host only does hit formatting + FOUND_*.txt  
- Checkpoint every K batches (bit cursor + LDS state)  
- Metrics: raw candidates/s, checksum-pass/s, PBKDF2/s, addresses/s (four meters — be honest in UI)

---

### 5.5 CLI sketch (mnemonic suite)

```bat
REM Partial seed recovery (3 missing words)
keyhunt -m mnemonic -R mask -w 12 -f targets.txt ^
  --seed "abandon ? ? zoo ... about" -D 5 --path-pack btc-std.json -U cuda

REM Last word only
keyhunt -m mnemonic -R lastword --seed "w1 w2 ... w11 ?" -f targets.txt

REM Passphrase dict
keyhunt -m mnemonic -R pass-dict --seed "full twelve words ..." ^
  --pass-file rockyou-btc.txt -f targets.txt -U cuda

REM Electrum v2
keyhunt -m mnemonic -R electrum-v2 --seed "word ? word ..." -f targets.txt

REM Model file constraints
keyhunt -m mnemonic -R model --model constraints.json -f targets.txt

REM Milk Sad time window
keyhunt -m mnemonic -R milksad -T 1514764800:1546300800 -f targets.txt
```

---

## 6. Cross-cutting “never shipped together” features

| Feature | Description | Why rare |
|---------|-------------|----------|
| **Unified hit schema** | JSONL: mode, coin, path, mnemonic, pass, priv, addr, ts | Scripts/dashboards |
| **Dry-run complexity** | Print search space size + ETA for mask/pass/BSGS | Beginners stop wasting GPU |
| **Mode advisor** | `keyhunt --advise` reads target file → suggests address vs bsgs vs kangaroo vs mnemonic | Nobody does this well |
| **Shared fuse cache** | Persist fuse for huge address dumps across modes | Rebuild cost |
| **Multi-GPU work stealer** | Dynamic shards for mask spaces | Static stride wastes GPU |
| **Property tests** | Known-answer vectors for every new DL / mnemonic mode | Prevents silent wrong kernels |
| **Research harness** | Auto-benchmark grumpy vs interleave vs kangaroo on puzzle 40–70 | Publish honest SPEEDS.md |

---

## 7. Priority roadmap (impact × feasibility)

### P0 — ship first (user-visible, high ROI)

1. **Mnemonic `mask` + `lastword` + checksum-first** (CPU then CUDA PBKDF2)  
2. **Mnemonic `pass-dict` / `pass-mask`**  
3. **Custom path packs** for mnemonic (BIP-86, ETH Ledger Live, Electrum)  
4. **BSGS `negmap` + better GPU batched giants**  
5. **Device-side hash160 + fuse for address/rmd160**  

### P1 — differentiators

6. **Mnemonic `model` file + WordOrbit**  
7. **Electrum v2** (huge prefilter win)  
8. **HerdHandoff hybrid DL**  
9. **`-x sobol` / `-x hilbert`** for address/rmd160  
10. **`weakrng` / Milk Sad mnemonic+key modes**  

### P2 — research prestige

11. **GrumpyBSGS + InterleaveBSGS**  
12. **OrbitBSGS**  
13. **GaudrySchost / residue herds**  
14. **Shadow160 birthday collider**  
15. **SLIP39 + aezeed**  
16. **FuseCascade for billion-address sets**  

### P3 — moonshots

17. **ChecksumPrism + MnemonicLattice**  
18. **Multi-GPU producer/consumer mnemonic pipeline**  
19. **DualTarget Anchor recovery**  
20. **PathNova multisig cosigner search**  

---

## 8. Suggested new help-table (future README section)

| Mode / submode | Target | Algorithm |
|----------------|--------|-----------|
| `address` + `-x sobol` | Addresses | Quasirandom grind |
| `rmd160` + `-R prefix` | Partial hash160 | Prefix match |
| `rmd160` / `shadow160` | Funded hash160 set | DP birthday |
| `bsgs -B grumpy` | Pubkey | 2-giant BSGS |
| `bsgs -B orbit` | Pubkey | Endomorphism BSGS |
| `bsgs -B handoff` | Pubkey | BSGS→kangaroo |
| `kangaroo --mod` | Pubkey + residue | Constrained kangaroo |
| `weakrng -R milksad` | Addresses | MT19937 keyspace |
| `mnemonic -R mask` | Addresses | Partial BIP-39 |
| `mnemonic -R pass-*` | Addresses | 25th word |
| `mnemonic -R electrum-v2` | Addresses | Electrum seed |
| `mnemonic -R milksad` | Addresses | Weak seed RNG |
| `mnemonic -R model` | Addresses | Constraint solver |

---

## 9. What to *avoid* (anti-ideas)

- Claiming full 256-bit or full 12-word blind search is “practical.”  
- Shipping “AI finds private keys” theater without a real constraint model.  
- Adding 50 half-finished `-x` names that only reshuffle RNG.  
- GPU kernels that skip checksum validation (wastes 15/16 of PBKDF2).  
- Rotating fuse entries on month-long BSGS runs (false-positive death spiral).

---

## 10. Sources consulted (research trail)

Open tools / writeups: TrueCollider README + ROADMAP + HELP_DUMP; Keyhunt / Collider BSGS lineage; RCKangaroo / PSCKangaroo (ALL-TAME, 16-byte DP, async BSGS resolve); JeanLucPons Kangaroo; BitcoinAddressFinder; BTCCollider; Hydra; btcrecover / seedrecover; CryptoRecover; wrecover; CUDAHUNT; bitcoin-mnemonic-recovery (OpenCL); hashcat multi-GPU PBKDF2↔ECC pipelining discussion.

Papers / algorithms: Pollard kangaroo & rho; van Oorschot–Wiener parallel collision search; Gaudry–Schost multidimensional DLP; Bernstein–Lange “Two grumpy giants and a baby” (ePrint 2012/294); Galbraith et al. interval DLP improvements; binary fuse filters (Graf–Lemire); secp256k1 GLV endomorphism; BIP-39/32/44/49/84/85/86; SLIP39; Electrum seed versioning; CVE-2023-39910 Milk Sad; Android SecureRandom / Randstorm histories.

---

## 11. Recommended next conversation (when you want to build)

Pick **one lane** to implement first:

1. **Mnemonic recovery lane** → `mask` + `lastword` + checksum-first + path packs  
2. **BSGS research lane** → `grumpy` / `interleave` / `orbit` + GPU giant batching  
3. **Address/rmd160 speed lane** → device hash160 + FuseCascade + sobol/hilbert  

Say which lane, and this document becomes an implementation checklist.

---

*End of local ideas document. Keep this file on disk only unless you explicitly decide to publish a redacted version.*
