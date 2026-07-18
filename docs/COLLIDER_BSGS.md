# Collider-bsgs → TrueCollider mapping

Reference: [pp717/Collider-bsgs](https://github.com/pp717/Collider-bsgs) (CUDA BSGS puzzle/pubkey search).

TrueCollider already ships a full BSGS/kangaroo stack (`-m bsgs`, `-m kangaroo`, `-B …`, `-U cuda`). Use this cheat-sheet to run **Collider-style** jobs without a separate binary.

| Collider.exe | TrueCollider keyhunt |
|--------------|----------------------|
| `-pb PUBKEY` | put pubkey in file → `-f pub.txt -m bsgs` (or xpoint) |
| `-infile pubs.txt` | `-f pubs.txt` |
| `-pk START` | `-r START:END` (hex range) |
| `-pke END` | second half of `-r` |
| `-w 22` (baby 2^w) | tune `-k` / `-n` table size (see BSGS Lab) |
| `-htsz 26` | related to bloom/table sizing (`-z`, `-n`) |
| `-d 0,1` | `-d 0` / multi-GPU via `-U cuda` + device flags |
| `-t/-b/-p` grid | `-g blocks,threads` style GPU knobs |
| `-wl` / `-wt` resume | TrueCollider work/save files + freeze-table |

## Puzzle recipe (example #125)

```
keyhunt_cuda.exe -m bsgs -B random -U cuda -f puzzle_125_pub.txt -r 100000000000000000000000000000000:1ffffffffffffffffffffffffffffffff -t 4
```

Use **Puzzles** tab or **Tools Arsenal → Collider-bsgs recipe** for one-click presets.

## VanBit-style vanity

```
keyhunt_cuda.exe -m vanity -U cuda -v 1Love
```

TrueNexus **Vanity Lab** wraps this.
