# Bundled tools (local runtime)

TrueNexus looks here first so you do **not** need Desktop paths in Settings.

```
tools/
  TrueCollider/
    keyhunt.exe
    keyhunt_cuda.exe
    tests/          # sample targets
    docs/
  TrueMkeyCollider/
    TrueMkeyCollider.exe
    data/
    docs/
```

## Refresh after rebuilding

If you rebuild collider/mkey elsewhere, run:

```bat
Sync_Tools.bat
```

That copies only the runtime binaries + tests/data (not the multi‑GB CUDA toolkit).

## Disk note

Do **not** copy `cuda_toolkit\` into this tree — it is huge and not required to launch the already-built `.exe` files.
