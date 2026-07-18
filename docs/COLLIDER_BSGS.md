# Collider-bsgs → TrueCollider mapping

Reference: [pp717/Collider-bsgs](https://github.com/pp717/Collider-bsgs) (CUDA BSGS puzzle/pubkey search).

TrueNexus ships:

1. **Collider Lab** — launch bundled `tools/Collider-bsgs/Collider.exe` (original) **or** TrueCollider bridge.
2. **TrueCollider aliases** — same puzzle CLI as Collider without a second mental model.

## Flag aliases (TrueCollider)

| Collider.exe | TrueCollider (`keyhunt` / `keyhunt_cuda`) |
|--------------|-------------------------------------------|
| `-pb PUBKEY` | `--pb PUBKEY` (writes `collider_pb_target.txt`, forces `-m bsgs`) |
| `-infile pubs.txt` | `--infile pubs.txt` (same as `-f`) |
| `-pk START` | `--pk START` |
| `-pke END` | `--pke END` → range `START:END` |
| `-w 22` (baby 2^w) | `--baby-bits 22` (`-w` is mnemonic word-count in TrueCollider) |
| `-htsz 26` | `--htsz 26` (soft-maps bloom multiplier) |
| `-wl` / `-wt` | `--wl` / `--wt` (workfile / autosave seconds) |
| `-d 0` | Collider Lab only on original; TrueCollider uses `-U cuda` |
| `-r BITS` (random) | `--mode random` (Collider bridge **default**) |
| *(no native rseq)* | `--mode rseq --walk 2M\|1B\|1T` or `-B rseq` |
| sequential giants | `--mode sequential` or `-B sequential` |

### Search modes (TrueCollider bridge)

| Mode | Behavior |
|------|----------|
| `random` | New random giant start every step (default for Collider bridge) |
| `sequential` | Linear giants from range start |
| `rseq` | Random start → walk `--walk` keys sequentially → reseed |

Walk accepts `2M`, `10M`, `1B`, `1T`, `5000000`, `0x100000`, `billion`, etc.

## Puzzle recipe (example #125)

```
keyhunt_cuda.exe -m bsgs -B random -U cuda --pb <PUBHEX> --pk 100000000000000000000000000000000 --pke 1ffffffffffffffffffffffffffffffff -t 4
```

Or classic:

```
keyhunt_cuda.exe -m bsgs -B random -U cuda -f puzzle_125_pub.txt -r 100000000000000000000000000000000:1ffffffffffffffffffffffffffffffff -t 4
```

## Native Collider.exe

```
tools\Collider-bsgs\Collider.exe -d 0 -w 22 -htsz 26 -pb <PUB> -pk <START> -pke <END>
```

Use **Collider Lab** for one-click Preview/Launch.

## GPU mnemonic note

With `-m mnemonic -U cuda`, TrueCollider runs BIP39 checksum + PBKDF2 on host (SHA512), then batches derived privkeys through **GPU secp EC + hash160** for P2PKH / nested / native segwit path packs (including multicoin).
