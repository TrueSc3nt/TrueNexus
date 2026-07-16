<p align="center">
  <img src="https://img.shields.io/badge/TrueNexus-Command%20Center-D4A017?style=for-the-badge" alt="TrueNexus"/>
  <img src="https://img.shields.io/badge/by-TrueScent-111111?style=for-the-badge" alt="TrueScent"/>
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Platform-Windows-0078D6?style=for-the-badge&logo=windows&logoColor=white" alt="Windows"/>
</p>

<h1 align="center">TrueNexus</h1>

<p align="center">
  <b>The professional desktop command center for the TrueScent collider arsenal.</b><br/>
  One interface. Two battle-tested engines. An entire research lab of next-gen modes.
</p>

<p align="center">
  <a href="https://t.me/TrueScent">Telegram @TrueScent</a> ·
  <a href="https://github.com/TrueSc3nt/TrueCollider">TrueCollider</a> ·
  <a href="https://github.com/TrueSc3nt/TrueMkeyCollider">TrueMkeyCollider</a>
</p>

---

## Why TrueNexus exists

Serious recovery and puzzle work dies in a mess of `.bat` files, forgotten flags, and half-remembered bit ranges.

**TrueNexus** is the opposite of that chaos:

| For beginners | For professionals |
|---------------|-------------------|
| Puzzle dropdown 1→160 fills the range for you | Exact flag control for every live mode |
| Dry-run before you burn GPU hours | Embedded console with copy / paste / stop |
| Plain-language mode advisor | Research Labs expose tomorrow’s algorithms today |
| Browse buttons for every file type | Themes, presets, path packs, hybrid DL sketches |

This is not a toy skin. It is a **control surface** for tools the world is meant to take seriously.

---

## Engines inside

### 1) [TrueCollider](https://github.com/TrueSc3nt/TrueCollider)
Multi-currency private-key / seed / vanity / discrete-log hunter.

- CPU SIMD (SSE / AVX2 / AVX-512) + optional **CUDA / OpenCL**
- Modes: `address` · `rmd160` · `xpoint` · `bsgs` · `kangaroo` · `vanity` · `minikeys` · `mnemonic` · `poetry` · `brainwallet` · `pubkey2addr`
- Collider search patterns: `chaos` · `gravity` · `spiral` · `reverse` · `auto` · …
- Binary fuse filters, GLV endomorphism, multi-coin encode (BTC family, ETH, SOL, taproot, …)

### 2) [TrueMkeyCollider](https://github.com/TrueSc3nt/TrueMkeyCollider)
Windows **CUDA AES** cracker for Bitcoin Core `wallet.dat` **mkey / ckey** blobs (crackBTCwallet lineage).

- Random / sequential / mixed key walks
- Partial-key GPU mode (`--partial`)
- Auto post-hit decrypt → WIF → `FOUND_WALLET.txt`
- Grid / streams / VRAM auto budgeting

---

## Quick start (Windows)

```bat
cd %USERPROFILE%\Desktop\TrueNexus
pip install -r requirements.txt
Launch_TrueNexus.bat
```

Or:

```bat
python -m truenexus
```

### Point the GUI at your binaries

1. Open the **Settings** tab  
2. Browse to `keyhunt.exe` / `keyhunt_cuda.exe` (TrueCollider build)  
3. Browse to `TrueMkeyCollider.exe`  
4. Set working directory (usually your TrueCollider folder with `tests\`)  
5. **Save Settings**

---

## Interface map

| Tab | What it does |
|-----|----------------|
| **Home** | Orientation, mode advisor, quick links |
| **TrueCollider** | Full live CLI builder + research-aware dropdowns |
| **Puzzles** | Dropdown **Puzzle #001 → #160**, auto bit-range, recommend mode, write target file |
| **Mnemonic Lab** | BIP-39 live + mask / passphrase / Electrum / SLIP39 / lattice research suite |
| **BSGS Lab** | Live `-B` strategies + Grumpy / Orbit / HerdHandoff / residue research |
| **Address / RMD160** | Fuse strategies, BIP-32 paths, Shadow160 research |
| **TrueMkey** | Full AES GPU builder (`-ckeys`, `-mckey`, `--partial`, `--selftest`, …) |
| **Ideas Matrix** | Every named algorithm from the improvement research doc |
| **Settings** | Paths, theme persistence |
| **About** | Telegram + donation |

**Right panel:** always-on **Embedded Console** — run GUI-built jobs *or* type raw shell commands.

---

## Puzzles 1–160

Selecting **Puzzle #N** sets:

- Bits = `N`
- Range = `[2^(N-1) … 2^N - 1]` in hex
- Recommendation text (address grind vs BSGS vs kangaroo)

Known public challenge addresses are embedded for common unsolved / famous puzzles (e.g. 66–75, 80, 130–160).  
For others, supply your own `-f` target file.

**Beginner path:** Puzzles → `#066` → Auto-write target → Dry-run on TrueCollider → Launch.

---

## TrueCollider command encyclopedia

### Modes (`-m`)

| Mode | You have… | Engine does… |
|------|-----------|--------------|
| `address` | Address list | priv → pub → address → fuse match |
| `rmd160` | 40-hex hash160 | Same, skip Base58 (faster) |
| `xpoint` | Pubkey / x-only | Match X coordinate |
| `bsgs` | Pubkey + range | Baby-step giant-step ECDLP |
| `kangaroo` | Pubkey + range | Pollard's kangaroo / DP |
| `vanity` | Prefix (`-v`) | Address prefix grind |
| `minikeys` | Address list | Bitcoin `S…` minikey space |
| `mnemonic` | Address list | Random BIP-39 → BIP-32 paths |
| `poetry` | Address list | Poetry wordlist → key |
| `brainwallet` | Address list | Passphrase mutations → SHA256 key |
| `pubkey2addr` | Address list | Pure random keyspace walk |

### Search patterns (`-x`)

| Pattern | Intent |
|---------|--------|
| `sequential` | Linear coverage |
| `random` | Uniform random bases |
| `chaos` | Logistic-map ergodic coverage |
| `gravity` | Bias toward last hit region |
| `spiral` | Outward from range midpoint |
| `reverse` | Inverted BSGS roles |
| `auto` | Cycle spiral → chaos → gravity → reverse |

**Research (UI-ready):** `hilbert`, `sobol`

### BSGS (`-B`, `-k`, `-n`, `-S`)

| Flag | Meaning |
|------|---------|
| `-B sequential\|backward\|both\|random\|dance` | Giant-step strategy |
| `-k auto\|512\|1024…` | Baby-table multiplier (RAM) |
| `-n 0x…` | Table span (must be valid BSGS N) |
| `-S` | Save/load bloom/fuse tables |

**Research strategies in UI:** `grumpy`, `interleave`, `orbit`, `residue`, `handoff`, `negmap`, `nested`, `async-resolve`, …

### Performance

| Flag | Meaning |
|------|---------|
| `-e` | GLV endomorphism (~3× on grind modes) |
| `-t N` | CPU threads |
| `-U cuda\|opencl` | GPU backend |
| `-M auto\|MB` | Memory / VRAM budget |
| `-A auto\|avx2\|avx512` | SIMD level |
| `-y` | Dry-run (print plan, exit) |
| `-q` `-s N` | Quiet + stats interval |

### Mnemonic

| Flag | Meaning |
|------|---------|
| `-w 12\|24\|…` | Word count (`0` = random length) |
| `-L english\|all\|…` | BIP-39 language |
| `-W` | ETH keccak address checks |
| `-D N` | Indices per path |

**Mnemonic Lab research submodes (UI):**  
`mask` · `model` · `lastword` · `pass-dict` · `pass-mask` · `electrum-v1/v2` · `slip39` · `aezeed` · `bip85` · `milksad` · `lattice` · `checksum-prism` · …

> Live TrueCollider today runs **random valid BIP-39** with empty passphrase and BTC paths 44/49/84.  
> Research submodes are first-class in TrueNexus so the product surface is ready as kernels land.

---

## TrueMkeyCollider command encyclopedia

| Flag | Meaning |
|------|---------|
| `-ckeys FILE` | Encrypted ckeys (`HEX96 [PUBKEY]`) |
| `-mckey FILE` | Encrypted mkeys |
| `-pubkeys FILE` | Companion pubkeys if needed for IV |
| `-r` / `-q` / `-rs` | Random / sequential / mixed |
| `-d N` | CUDA device |
| `-g B,T` | Grid blocks,threads |
| `-streams N` | Concurrent CUDA streams |
| `-M auto\|MB` | VRAM → keys/launch |
| `-n N` | Stop after N keys |
| `--partial HEX` | Known key prefix → search suffix only |
| `--try HEX64` | Host-verify one key + auto WIF pipeline |
| `--selftest` | Full PoC |
| `--found FILE` | Recovery dump (default `FOUND_WALLET.txt`) |

---

## Research Labs (Ideas Matrix)

TrueNexus surfaces the full improvement vision as named product concepts:

| Codename | Class |
|----------|-------|
| **OrbitBSGS** | Endomorphism-collapsed baby tables |
| **HerdHandoff** | BSGS → kangaroo cascade |
| **GrumpyBSGS** | Bernstein–Lange two giants + baby |
| **InterleaveBSGS** | Average-case interleaved BSGS |
| **GaudrySchost / ResidueHerd** | Modular / multi-dimensional DL |
| **FuseCascade** | Multi-resolution filters |
| **HilbertStride / SobolWalk** | Quasirandom key orderings |
| **Shadow160** | Partial hash160 birthday collider |
| **CrystalPRNG** | Milk Sad / Randstorm / weak RNG spaces |
| **MnemonicLattice** | Checksum lattice seed search |
| **ChecksumPrism** | Multi-language same-entropy |
| **PathNova** | Wallet derivation path packs |
| **WordOrbit / PhraseGravity / SeedCascadeVerify** | Intelligent mnemonic recovery |

Live flags launch today. Research entries preview with honest annotations — no fake “AI finds keys” theater.

---

## Themes

Switch from the header menu:

- Obsidian Gold *(default)*
- Arctic Steel
- Plasma Cyan
- Ember Forge
- Forest Signal
- Midnight Violet

Preference persists in `presets/user_settings.json`.

---

## Project layout

```
TrueNexus/
├── Launch_TrueNexus.bat
├── README.md
├── requirements.txt
├── assets/
├── docs/
├── logs/
├── presets/
└── truenexus/
    ├── app.py           # GUI
    ├── builders.py      # CLI compilers
    ├── puzzles.py       # Puzzle 1–160
    ├── runner.py        # Console process host
    ├── themes.py
    └── __main__.py
```

---

## Support the work

**Telegram:** [https://t.me/TrueScent](https://t.me/TrueScent)

**Donate BTC:**

```
bc1qke9ets26d6vs8ardndteds57frcald98n8g3te
```

If TrueNexus or the collider tools save you time, fuel the forge.

---

## Disclaimer

Educational and **authorized recovery / research** only.  
You are solely responsible for lawful use on wallets and systems you own or have explicit permission to test.  
Full 256-bit blind search is not practical. TrueNexus will never pretend otherwise.

---

## Credits

- **TrueScent** — TrueNexus, TrueCollider, TrueMkeyCollider  
- [albertobsd/keyhunt](https://github.com/albertobsd/keyhunt) — foundational hunter  
- [albertobsd/crackBTCwallet](https://github.com/albertobsd/crackBTCwallet) — mkey/ckey lineage  
- Research lineage: Pollard, van Oorschot–Wiener, Gaudry–Schost, Bernstein–Lange, binary fuse filters (Graf–Lemire)

---

<p align="center">
  <b>TrueNexus</b> — forge calmly. hunt precisely. recover honestly.
</p>
