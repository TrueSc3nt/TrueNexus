# TrueNexus Research 2026 — Idea Wave

Local implant of the lawful research plan (forums / GitHub synthesis 2024–2026).

**Hard refusals (ANTI — never implant):**

- Internet private-key scraper + balance check + auto-withdraw
- Puzzle/address RBF / mempool race to hijack a foreign spend

**Lawful substitute:** **Address Watch** tab — balance + last-tx **alerts only**.

---

## Status tags

| Tag | Meaning |
|-----|---------|
| LIVE | Already in TrueCollider / TrueNexus |
| GAP | Competitors ship; we still need |
| NOVEL | Rarely or never fully open-sourced as one product |
| ANTI | Explicitly refused |

## P0 (engine next)

1. CUDA PBKDF2-HMAC-SHA512 on-device  
2. Checksum-first GPU gate  
3. SOTA kangaroo CUDA (RCKangaroo-class)  
4. Multi-coin fuse (one EC → multi encodings)  
5. Device-resident hash160 + XOR/fuse GPU prefilter  

## Catalog sections (§11)

- **A** GPU mnemonic / PBKDF2 (20)  
- **B** ECDLP / kangaroo / BSGS (12)  
- **C** Address / hash160 / filters (8)  
- **D** Weak RNG (6)  
- **E** Multi-currency (7)  
- **F** TrueNexus UX / ops (6) — includes Address Watch LIVE  
- **G** Rare novel (11)  

See Ideas Matrix → filter **gap only** / **novel only** / **anti only**.  
Full mirror: `truenexus/ideas_catalog.py`.

## Sources (non-endorsement)

XopMC / OpenCL BIP39 engines / multi-coin CUDA mnemonic · RCKangaroo / PSCKangaroo · JeanLucPons Kangaroo · BitcoinAddressFinder · brainflayer blooms · TrueCollider BSGS/HerdHandoff stack.
