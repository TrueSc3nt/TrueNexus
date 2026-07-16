# TrueMkeyCollider

Windows **CUDA** GPU port of [crackBTCwallet](https://github.com/albertobsd/crackBTCwallet) (AlbertoBSD) — brute-force **AES-256 keys** against encrypted Bitcoin Core **`mkey` / `ckey`** blobs from `wallet.dat`.

On a hit it runs the **full post-hit pipeline** automatically: IV from pubkey → AES-CBC decrypt → padding check → WIF → `FOUND_WALLET.txt`.

## Throughput

Each trial is an **AES-256 decrypt + padding check**. Status output reports AES key trials and auto-scales units through **K/M/G/T/P/E**.

Measured peak on this packager’s RTX 3060 Ti (random AES, `-g 256,256 -streams 4 -M auto`): about **111 Mkeys/s**.

Key space remains **2^256** — GPU buys rate, not feasibility for unknown keys. Useful flags for throughput: large `-g` grids, multi-stream launches (`-streams`), and aggressive `-M auto` keys/launch sizing.

**Partial-key mode** (`--partial HEX`) is where AES GPU earns its keep: fix a known prefix (cold-boot / recall of leading bytes) and search only the unknown suffix. This does **not** claim a break of unknown full AES-256 master keys.

For passphrase/KDF, salvage, Hashcat bridge, and Recovery Lab GUI, use sibling **[TrueWalletCollider](https://github.com/TrueSc3nt/TrueWalletCollider)** (shares this CUDA crack core).

## Requirements

- Windows 10/11 x64
- Visual Studio 2022 (or Build Tools) with MSVC C++
- NVIDIA CUDA Toolkit **12.x** preferred (auto-detects 12.0–12.8 and 13.x)
- NVIDIA GPU compute capability ≥ 7.5 (fatbin: `sm_75` … `sm_90`)

## Build

```bat
cd %USERPROFILE%\Desktop\TrueMkeyCollider
build_cuda.bat
```

Produces `TrueMkeyCollider.exe` and runs `--selftest` (includes auto WIF + file save).

## Quick start

```bat
commands.bat
```

Or:

```bat
TrueMkeyCollider.exe --selftest
TrueMkeyCollider.exe -ckeys data\ckeys.txt --try 563758754506d53828c5383d2cb6296efe7f217c5ef6a84b13bce3ecec66da2e
TrueMkeyCollider.exe -ckeys data\ckeys.txt -mckey data\mckeys.txt -r -M auto -d 0 -g 256,256 -streams 4
TrueMkeyCollider.exe -ckeys data\ckeys.txt -r -g 512,512 -M auto -streams 4 -n 100000000
TrueMkeyCollider.exe -ckeys data\ckeys.txt --partial 56375875 -n 1000000000
```

### Manual helpers (crackBTCwallet shell equivalents)

```bat
TrueMkeyCollider.exe --cmd doublesha256 0382ca08ce78b0935099c74db12873a7dc1cba10a44165ce8cc1d0602f49ee97f5
TrueMkeyCollider.exe --cmd aesdecrypt 35fc5f8253f1bcf2c185571a35413f1f 56375875…da2e 2e24da42…3155
TrueMkeyCollider.exe --cmd privatekeytowif 3ea5eaabe7f7b997ce732acc9cf08315a805109003ce2bd918bac1b73b82d7b7
```

PoC WIFs:

- uncompressed `5JHsqscg3o1iAWjRP83nWWJFbgMrjnXwVQoxejtAqp4t6cCVgbo`
- compressed `KyKVQiQTML68gzEEce7HsEK9S4j4XqyZWQ6GdaGrSSk8XZJHqNWe`

## CLI

| Flag | Meaning |
|------|---------|
| `-ckeys FILE` | encrypted ckeys (`HEX96 [PUBHEX]` lines) |
| `-mckey FILE` | encrypted mkeys (96-hex lines) |
| `-pubkeys FILE` | companion pubkeys if ckeys are enc-only |
| `-f FILE` | crackBTCwallet-style `load ckey/mkey` commands |
| `-r` / `-q` / `-rs` | random / sequential / mixed |
| `-s HEX64` | sequential start key |
| `-w N` | mixed span (default 256) |
| `-d N` | CUDA device |
| `-g B,T` | blocks,threads (e.g. `256,256` / `512,512`; default=auto from SM count) |
| `-streams N` | concurrent CUDA streams (default 4) |
| `-M auto\|MB` | VRAM budget → keys/launch (~90% free when auto) |
| `-n N` | stop after N keys |
| `-o FILE` | short hit log (default `key_found.txt`) |
| `--found FILE` | full recovery dump (default `FOUND_WALLET.txt`) |
| `--try HEX64` | host-verify one key + **auto decrypt/WIF/save** |
| `--partial HEX` | known key prefix (1..31 bytes) → `MODE_PARTIAL` GPU search |
| `--selftest` | PoC host + GPU + WIF pipeline |
| `--cmd …` | `doublesha256` / `aesdecrypt` / `privatekeytowif` |

File formats: see [docs/FORMAT.md](docs/FORMAT.md).

## Auto post-hit (on AES padding OK)

1. For each matching ckey with pubkey: `IV = first 16 bytes of double-SHA256(pubkey)`
2. Full AES-CBC decrypt of the 48-byte blob
3. Verify sixteen `0x10` padding bytes
4. Strip padding → 32-byte privkey
5. Derive uncompressed + compressed WIF
6. Print all steps; append `FOUND_WALLET.txt`

If the ckey line is **only** 96-hex with no pubkey / `-pubkeys`, the AES key is still saved and the tool explains that pubkey is required for IV (same as crackBTCwallet needing the pubkey associated with the ckey — see `get_mkey_ckey` output).

## Honest gaps vs crackBTCwallet

| Feature | Original | This port |
|---------|----------|-----------|
| AES last-block padding check | Yes (AES-NI / ctaes) | Yes (CUDA + host ctaes) |
| Full CBC decrypt / WIF | Shell commands | **Auto on hit** + `--cmd` helpers |
| Interactive shell | Yes | CLI / `--cmd` |
| `get_mkey_ckey` wallet.dat extractor | Yes | Not bundled (use original or paste hex+pubkey) |
| Password derivation (`BytesToKeySHA512AES`) | Shell helper | Not implemented |
| Multi-target mkey+ckey | Yes | Yes (up to 64) |

## Attribution

- Search logic / formats / PoC: [crackBTCwallet](https://github.com/albertobsd/crackBTCwallet) (MIT, Luis Alberto / AlbertoBSD)
- Host AES: [ctaes](https://github.com/bitcoin-core/ctaes) (Pieter Wuille, MIT)
- Grid / stream / `-M auto` UX: implemented for AES key search on CUDA

## Disclaimer

Educational / recovery research only. You are responsible for lawful use on wallets you own.
