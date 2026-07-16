"""TrueNexus — professional GUI command center."""

from __future__ import annotations

import json
import os
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from truenexus import __donate_btc__, __telegram__, __truecollider__, __truemkey__, __version__
from truenexus.builders import (
    BSGS_STRATEGIES,
    COINS,
    FILTER_STRATS,
    GPU,
    LANGS,
    LOOK,
    MNEMONIC_SUBMODES,
    MODES_LIVE,
    MODES_RESEARCH,
    SEARCH_PATTERNS,
    VECTOR,
    ColliderConfig,
    MkeyConfig,
    explain_flag,
)
from truenexus.puzzles import (
    KNOWN_ADDR,
    all_puzzle_labels,
    parse_puzzle_number,
    puzzle_range_hex,
    recommend_mode,
    write_puzzle_target_file,
)
from truenexus.runner import ProcessRunner
from truenexus.themes import DEFAULT_THEME, THEMES

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "presets" / "user_settings.json"
LOG_DIR = ROOT / "logs"


def _default_paths() -> dict:
    home = Path.home()
    desktop = home / "Desktop"
    return {
        "truecollider_exe": str(desktop / "updayingkeyunt" / "TrueCollider-master" / "keyhunt.exe"),
        "truecollider_cuda": str(desktop / "updayingkeyunt" / "TrueCollider-master" / "keyhunt_cuda.exe"),
        "truemkey_exe": str(desktop / "TrueMkeyCollider" / "TrueMkeyCollider.exe"),
        "workdir": str(desktop / "updayingkeyunt" / "TrueCollider-master"),
        "theme": DEFAULT_THEME,
    }


class TrueNexusApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"TrueNexus  ·  v{__version__}  ·  by TrueScent")
        self.geometry("1440x900")
        self.minsize(1180, 720)
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        (ROOT / "presets").mkdir(parents=True, exist_ok=True)

        self.settings = _default_paths()
        self._load_settings()
        self.theme_name = self.settings.get("theme", DEFAULT_THEME)
        self._apply_theme(self.theme_name)

        self.runner = ProcessRunner(self._append_console, self._on_proc_done)
        self._build_ui()
        self._append_console(
            f"TrueNexus v{__version__} online.\n"
            f"Telegram: {__telegram__}\n"
            f"Donate BTC: {__donate_btc__}\n"
            f"Tools: TrueCollider · TrueMkeyCollider\n"
            "Tip: use Dry-Run before long GPU jobs. Research modes show in menus but map to live flags until kernels ship.\n\n"
        )

    # ── theme / settings ────────────────────────────────────────────────
    def _apply_theme(self, name: str) -> None:
        self.theme = THEMES.get(name, THEMES[DEFAULT_THEME])
        self.theme_name = name
        ctk.set_appearance_mode(self.theme["mode"])
        ctk.set_default_color_theme("dark-blue")
        self.configure(fg_color=self.theme["fg"])

    def _load_settings(self) -> None:
        if CONFIG_PATH.exists():
            try:
                self.settings.update(json.loads(CONFIG_PATH.read_text(encoding="utf-8")))
            except Exception:
                pass

    def _save_settings(self) -> None:
        self.settings["theme"] = self.theme_name
        CONFIG_PATH.write_text(json.dumps(self.settings, indent=2), encoding="utf-8")
        messagebox.showinfo("Saved", f"Settings written to\n{CONFIG_PATH}")

    # ── UI shell ────────────────────────────────────────────────────────
    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color=self.theme["card"], corner_radius=0, height=72)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            header, text="TRUENEXUS",
            font=ctk.CTkFont(family="Segoe UI Semibold", size=26, weight="bold"),
            text_color=self.theme["accent"],
        ).grid(row=0, column=0, padx=20, pady=(12, 0), sticky="w")
        ctk.CTkLabel(
            header,
            text="Unified arsenal for TrueCollider · TrueMkeyCollider · Research Labs",
            font=ctk.CTkFont(size=13),
            text_color=self.theme["muted"],
        ).grid(row=1, column=0, padx=20, pady=(0, 12), sticky="w")

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.grid(row=0, column=1, rowspan=2, padx=16, sticky="e")
        ctk.CTkLabel(right, text="Theme", text_color=self.theme["muted"]).pack(side="left", padx=(0, 6))
        self.theme_menu = ctk.CTkOptionMenu(
            right, values=list(THEMES.keys()), command=self._on_theme,
            width=160, fg_color=self.theme["accent"], button_color=self.theme["accent"],
        )
        self.theme_menu.set(self.theme_name)
        self.theme_menu.pack(side="left", padx=4)
        ctk.CTkButton(right, text="Copy Donate", width=110, command=self._copy_donate,
                      fg_color=self.theme["card"], border_width=1, border_color=self.theme["accent"],
                      text_color=self.theme["accent"]).pack(side="left", padx=4)
        ctk.CTkButton(right, text="Telegram", width=100, command=self._open_telegram,
                      fg_color=self.theme["accent"], text_color="#111").pack(side="left", padx=4)

        body = ctk.CTkFrame(self, fg_color="transparent")
        body.grid(row=1, column=0, sticky="nsew", padx=12, pady=8)
        body.grid_columnconfigure(0, weight=3)
        body.grid_columnconfigure(1, weight=2)
        body.grid_rowconfigure(0, weight=1)

        self.tabs = ctk.CTkTabview(body, fg_color=self.theme["card"], segmented_button_selected_color=self.theme["accent"])
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        for name in (
            "Home", "TrueCollider", "Puzzles", "Mnemonic Lab", "BSGS Lab",
            "Address / RMD160", "TrueMkey", "Ideas Matrix", "Settings", "About",
        ):
            self.tabs.add(name)

        self._build_home()
        self._build_collider()
        self._build_puzzles()
        self._build_mnemonic()
        self._build_bsgs()
        self._build_address()
        self._build_mkey()
        self._build_ideas()
        self._build_settings()
        self._build_about()

        # Console column
        cons = ctk.CTkFrame(body, fg_color=self.theme["card"])
        cons.grid(row=0, column=1, sticky="nsew")
        cons.grid_rowconfigure(1, weight=1)
        cons.grid_columnconfigure(0, weight=1)

        topc = ctk.CTkFrame(cons, fg_color="transparent")
        topc.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        ctk.CTkLabel(topc, text="Embedded Console", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=self.theme["accent"]).pack(side="left")
        ctk.CTkButton(topc, text="Copy All", width=80, command=self._copy_console).pack(side="right", padx=2)
        ctk.CTkButton(topc, text="Clear", width=70, command=self._clear_console).pack(side="right", padx=2)
        ctk.CTkButton(topc, text="Stop", width=70, fg_color=self.theme["danger"],
                      command=self.runner.stop).pack(side="right", padx=2)

        self.console = ctk.CTkTextbox(
            cons, font=ctk.CTkFont(family="Consolas", size=13),
            fg_color=self.theme["console_bg"], text_color=self.theme["console_fg"],
            wrap="word",
        )
        self.console.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 6))

        cmdrow = ctk.CTkFrame(cons, fg_color="transparent")
        cmdrow.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        cmdrow.grid_columnconfigure(0, weight=1)
        self.cmd_entry = ctk.CTkEntry(cmdrow, placeholder_text="Type a shell command and press Run / Enter…")
        self.cmd_entry.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.cmd_entry.bind("<Return>", lambda _e: self._run_raw_cmd())
        ctk.CTkButton(cmdrow, text="Run", width=80, fg_color=self.theme["accent"], text_color="#111",
                      command=self._run_raw_cmd).grid(row=0, column=1)

        # Status bar
        self.status = ctk.CTkLabel(self, text="Ready", anchor="w", text_color=self.theme["muted"])
        self.status.grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 8))

    def _scroll(self, parent: ctk.CTkFrame) -> ctk.CTkScrollableFrame:
        return ctk.CTkScrollableFrame(parent, fg_color="transparent")

    def _label(self, parent, text: str, **kw):
        return ctk.CTkLabel(parent, text=text, anchor="w", text_color=self.theme["text"], **kw)

    def _section(self, parent, title: str):
        self._label(parent, title, font=ctk.CTkFont(size=18, weight="bold"),
                    text_color=self.theme["accent"]).pack(anchor="w", pady=(12, 6))

    def _browse(self, var: ctk.StringVar, filetypes=None):
        path = filedialog.askopenfilename(filetypes=filetypes or [("All", "*.*")])
        if path:
            var.set(path)

    def _browse_dir(self, var: ctk.StringVar):
        path = filedialog.askdirectory()
        if path:
            var.set(path)

    # ── Home ────────────────────────────────────────────────────────────
    def _build_home(self) -> None:
        tab = self.tabs.tab("Home")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Welcome to TrueNexus")
        blurb = (
            "TrueNexus is the professional control surface for TrueScent's open tooling.\n\n"
            "• TrueCollider — multi-coin key / seed / BSGS / kangaroo hunter (CPU SIMD + CUDA/OpenCL)\n"
            "• TrueMkeyCollider — CUDA AES cracker for Bitcoin Core wallet.dat mkey/ckey blobs\n"
            "• Research Labs — every idea from the improvement matrix, exposed as dropdowns\n\n"
            "New users: start on the Puzzles tab → pick Puzzle #66 → Dry-Run → Launch.\n"
            "Pros: jump to BSGS Lab / Mnemonic Lab / TrueMkey and craft exact flags.\n"
            "Everyone: the console on the right is a real shell — copy, paste, run, stop."
        )
        self._label(f, blurb, justify="left").pack(anchor="w", pady=4)
        btns = ctk.CTkFrame(f, fg_color="transparent")
        btns.pack(anchor="w", pady=12)
        ctk.CTkButton(btns, text="Open TrueCollider Repo", command=lambda: self._open_url(__truecollider__),
                      fg_color=self.theme["accent"], text_color="#111").pack(side="left", padx=4)
        ctk.CTkButton(btns, text="Open TrueMkey Repo", command=lambda: self._open_url(__truemkey__)).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="Quick Puzzle 66", command=self._quick_puzzle66).pack(side="left", padx=4)

        self._section(f, "Mode advisor")
        self.advisor = ctk.CTkTextbox(f, height=140)
        self.advisor.pack(fill="x", pady=4)
        self.advisor.insert("1.0", self._advisor_text())
        self.advisor.configure(state="disabled")

    def _advisor_text(self) -> str:
        return (
            "Have only an address? → TrueCollider mode address / rmd160\n"
            "Have a public key + known bit range? → bsgs (mid) or kangaroo (large)\n"
            "Have a partial seed phrase? → Mnemonic Lab → mask / lastword (research UI)\n"
            "Have wallet.dat ckey/mkey hex? → TrueMkey tab (AES GPU)\n"
            "Chasing vanity prefix? → vanity mode + -v\n"
            "Broken RNG era wallet? → Ideas Matrix → CrystalPRNG / Milk Sad\n"
        )

    # ── TrueCollider ────────────────────────────────────────────────────
    def _build_collider(self) -> None:
        tab = self.tabs.tab("TrueCollider")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Binary & workspace")

        self.tc_exe = ctk.StringVar(value=self.settings.get("truecollider_exe", ""))
        self.tc_cwd = ctk.StringVar(value=self.settings.get("workdir", ""))
        self._path_row(f, "keyhunt.exe / keyhunt_cuda.exe", self.tc_exe, exe=True)
        self._path_row(f, "Working directory", self.tc_cwd, directory=True)

        self._section(f, "Core search")
        grid = ctk.CTkFrame(f, fg_color="transparent")
        grid.pack(fill="x")
        modes = MODES_LIVE + MODES_RESEARCH
        self.tc_mode = self._dropdown(grid, "Mode (-m)", modes, "address", 0, 0)
        self.tc_coin = self._dropdown(grid, "Coin (-c)", COINS, "btc", 0, 1)
        self.tc_look = self._dropdown(grid, "Look (-l)", LOOK, "compress", 1, 0)
        self.tc_pattern = self._dropdown(grid, "Pattern (-x)", SEARCH_PATTERNS, "chaos", 1, 1)
        self.tc_gpu = self._dropdown(grid, "GPU (-U)", GPU, "none", 2, 0)
        self.tc_vector = self._dropdown(grid, "Vector (-A)", VECTOR, "auto", 2, 1)

        self.tc_target = ctk.StringVar()
        self._path_row(f, "Target file (-f)  addresses / rmd / pubkeys / bloom sources", self.tc_target)

        opts = ctk.CTkFrame(f, fg_color="transparent")
        opts.pack(fill="x", pady=6)
        self.tc_bits = self._entry(opts, "Bits (-b)", "", 0, 0)
        self.tc_r0 = self._entry(opts, "Range start", "", 0, 1)
        self.tc_r1 = self._entry(opts, "Range end", "", 1, 0)
        self.tc_threads = self._entry(opts, "Threads (-t)", "8", 1, 1)
        self.tc_mem = self._entry(opts, "Memory (-M)", "auto", 2, 0)
        self.tc_stats = self._entry(opts, "Stats sec (-s)", "10", 2, 1)
        self.tc_vanity = self._entry(opts, "Vanity (-v)", "", 3, 0)
        self.tc_extra = self._entry(opts, "Extra args", "", 3, 1)

        flags = ctk.CTkFrame(f, fg_color="transparent")
        flags.pack(fill="x", pady=4)
        self.tc_endo = ctk.CTkCheckBox(flags, text="Endomorphism (-e)")
        self.tc_endo.select()
        self.tc_endo.pack(side="left", padx=6)
        self.tc_quiet = ctk.CTkCheckBox(flags, text="Quiet (-q)")
        self.tc_quiet.select()
        self.tc_quiet.pack(side="left", padx=6)
        self.tc_dry = ctk.CTkCheckBox(flags, text="Dry-run (-y)")
        self.tc_dry.pack(side="left", padx=6)
        self.tc_save = ctk.CTkCheckBox(flags, text="Save bloom/fuse (-S)")
        self.tc_save.pack(side="left", padx=6)

        self.tc_preview = ctk.CTkTextbox(f, height=90, font=ctk.CTkFont(family="Consolas", size=13))
        self.tc_preview.pack(fill="x", pady=8)
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkButton(row, text="Preview Command", command=self._preview_collider).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Copy Command", command=lambda: self._copy_text(self.tc_preview.get("1.0", "end"))).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Launch TrueCollider", fg_color=self.theme["accent"], text_color="#111",
                      command=self._launch_collider).pack(side="left", padx=4)

    def _path_row(self, parent, label, var, directory=False, exe=False):
        self._label(parent, label, text_color=self.theme["muted"]).pack(anchor="w", pady=(8, 2))
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x")
        row.grid_columnconfigure(0, weight=1)
        ctk.CTkEntry(row, textvariable=var).grid(row=0, column=0, sticky="ew", padx=(0, 6))
        if directory:
            ctk.CTkButton(row, text="Browse", width=90, command=lambda: self._browse_dir(var)).grid(row=0, column=1)
        else:
            ftypes = [("Executable", "*.exe"), ("All", "*.*")] if exe else [
                ("Text / hex", "*.txt *.rmd *.hex *.bloom *.fuse"), ("All", "*.*")
            ]
            ctk.CTkButton(row, text="Browse", width=90, command=lambda: self._browse(var, ftypes)).grid(row=0, column=1)

    def _dropdown(self, parent, label, values, default, r, c):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(row=r, column=c, sticky="ew", padx=6, pady=4)
        parent.grid_columnconfigure(c, weight=1)
        self._label(box, label, text_color=self.theme["muted"]).pack(anchor="w")
        menu = ctk.CTkOptionMenu(box, values=values, width=220)
        menu.set(default)
        menu.pack(fill="x")
        return menu

    def _entry(self, parent, label, default, r, c):
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(row=r, column=c, sticky="ew", padx=6, pady=4)
        parent.grid_columnconfigure(c, weight=1)
        self._label(box, label, text_color=self.theme["muted"]).pack(anchor="w")
        var = ctk.StringVar(value=default)
        ctk.CTkEntry(box, textvariable=var).pack(fill="x")
        return var

    def _collider_cfg(self) -> ColliderConfig:
        exe = self.tc_exe.get().strip()
        if self.tc_gpu.get() == "cuda" and "keyhunt_cuda" not in exe.lower():
            cuda = self.settings.get("truecollider_cuda", "")
            if cuda and Path(cuda).exists():
                exe = cuda
        return ColliderConfig(
            exe=exe or "keyhunt.exe",
            mode=self.tc_mode.get(),
            target_file=self.tc_target.get().strip(),
            coin=self.tc_coin.get(),
            look=self.tc_look.get(),
            bits=self.tc_bits.get().strip(),
            range_start=self.tc_r0.get().strip(),
            range_end=self.tc_r1.get().strip(),
            search_pattern=self.tc_pattern.get(),
            threads=self.tc_threads.get().strip() or "8",
            endomorphism=bool(self.tc_endo.get()),
            gpu=self.tc_gpu.get(),
            memory=self.tc_mem.get().strip() or "auto",
            quiet=bool(self.tc_quiet.get()),
            stats=self.tc_stats.get().strip() or "10",
            dry_run=bool(self.tc_dry.get()),
            vanity=self.tc_vanity.get().strip(),
            vector=self.tc_vector.get(),
            save_bloom=bool(self.tc_save.get()),
            extra_args=self.tc_extra.get().strip(),
            bsgs_strategy=getattr(self, "bsgs_strat", ctk.StringVar(value="random")).get()
            if hasattr(self, "bsgs_strat") else "random",
            k_factor=getattr(self, "bsgs_k", ctk.StringVar(value="auto")).get()
            if hasattr(self, "bsgs_k") else "auto",
            n_table=getattr(self, "bsgs_n", ctk.StringVar(value="")).get()
            if hasattr(self, "bsgs_n") else "",
            mnemonic_words=getattr(self, "mn_words", ctk.StringVar(value="12")).get()
            if hasattr(self, "mn_words") else "12",
            mnemonic_lang=getattr(self, "mn_lang", ctk.StringVar(value="english")).get()
            if hasattr(self, "mn_lang") else "english",
            mnemonic_eth=bool(self.mn_eth.get()) if hasattr(self, "mn_eth") else False,
            mnemonic_submode=getattr(self, "mn_sub", ctk.StringVar(value="random (live)")).get()
            if hasattr(self, "mn_sub") else "random (live)",
            seed_mask=getattr(self, "mn_mask", ctk.StringVar(value="")).get()
            if hasattr(self, "mn_mask") else "",
            passphrase_file=getattr(self, "mn_pass", ctk.StringVar(value="")).get()
            if hasattr(self, "mn_pass") else "",
            derivation_path=getattr(self, "addr_path", ctk.StringVar(value="")).get()
            if hasattr(self, "addr_path") else "",
            derivation_depth=getattr(self, "addr_depth", ctk.StringVar(value="1")).get()
            if hasattr(self, "addr_depth") else "1",
            filter_strategy=getattr(self, "addr_filter", ctk.StringVar(value="default fuse")).get()
            if hasattr(self, "addr_filter") else "default fuse",
        )

    def _preview_collider(self) -> None:
        cfg = self._collider_cfg()
        # Merge lab-specific if set
        if hasattr(self, "bsgs_strat"):
            cfg.bsgs_strategy = self.bsgs_strat.get()
            cfg.k_factor = self.bsgs_k.get()
            cfg.n_table = self.bsgs_n.get()
        if hasattr(self, "mn_sub"):
            cfg.mnemonic_submode = self.mn_sub.get()
            cfg.mnemonic_words = self.mn_words.get()
            cfg.mnemonic_lang = self.mn_lang.get()
            cfg.mnemonic_eth = bool(self.mn_eth.get())
            cfg.seed_mask = self.mn_mask.get()
            cfg.passphrase_file = self.mn_pass.get()
            cfg.derivation_depth = self.mn_depth.get()
        cmd, warns = cfg.build()
        self.tc_preview.delete("1.0", "end")
        self.tc_preview.insert("1.0", cmd)
        if warns:
            self._append_console("\n".join(warns) + "\n")
        self.status.configure(text="Command preview ready")

    def _launch_collider(self) -> None:
        self._preview_collider()
        cmd = self.tc_preview.get("1.0", "end").strip().split("  REM")[0].strip()
        cwd = self.tc_cwd.get().strip() or None
        self.settings["truecollider_exe"] = self.tc_exe.get().strip()
        self.settings["workdir"] = self.tc_cwd.get().strip()
        self._set_status("Launching TrueCollider…")
        self.runner.start(cmd, cwd=cwd)

    # ── Puzzles ─────────────────────────────────────────────────────────
    def _build_puzzles(self) -> None:
        tab = self.tabs.tab("Puzzles")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Bitcoin Puzzle Challenge 1–160")
        self._label(
            f,
            "Select a puzzle. TrueNexus fills bit range automatically and recommends a mode.\n"
            "For address mode you still need a target .txt (Browse or Auto-write known address).",
            text_color=self.theme["muted"],
        ).pack(anchor="w")

        self.puzzle_menu = ctk.CTkOptionMenu(f, values=all_puzzle_labels(), width=700, command=self._on_puzzle)
        self.puzzle_menu.set(all_puzzle_labels()[65])  # #66
        self.puzzle_menu.pack(anchor="w", pady=8)

        self.puzzle_info = ctk.CTkTextbox(f, height=120)
        self.puzzle_info.pack(fill="x", pady=4)
        self._on_puzzle(self.puzzle_menu.get())

        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", pady=8)
        ctk.CTkButton(row, text="Apply Range → TrueCollider", command=self._apply_puzzle).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Auto-write target .txt", command=self._write_puzzle_file).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Launch Puzzle Job", fg_color=self.theme["accent"], text_color="#111",
                      command=self._launch_puzzle).pack(side="left", padx=4)

    def _on_puzzle(self, label: str) -> None:
        n = parse_puzzle_number(label)
        start, end = puzzle_range_hex(n)
        addr = KNOWN_ADDR.get(n, "(no built-in address — supply your own target file)")
        txt = (
            f"Puzzle #{n}\n"
            f"Bits: {n}\n"
            f"Range: 0x{start} : 0x{end}\n"
            f"Address: {addr}\n"
            f"Recommended: {recommend_mode(n)}\n"
        )
        self.puzzle_info.delete("1.0", "end")
        self.puzzle_info.insert("1.0", txt)

    def _apply_puzzle(self) -> None:
        n = parse_puzzle_number(self.puzzle_menu.get())
        start, end = puzzle_range_hex(n)
        self.tc_bits.set(str(n))
        self.tc_r0.set(start)
        self.tc_r1.set(end)
        self.tc_mode.set("address" if n <= 90 else "bsgs")
        self.tc_pattern.set("chaos" if n <= 80 else "random")
        self.tabs.set("TrueCollider")
        self._set_status(f"Applied puzzle #{n} range to TrueCollider tab")

    def _write_puzzle_file(self) -> None:
        n = parse_puzzle_number(self.puzzle_menu.get())
        if n not in KNOWN_ADDR:
            messagebox.showwarning("No address", "This puzzle has no built-in address. Browse a target file manually.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", initialfile=f"puzzle_{n}.txt",
            filetypes=[("Text", "*.txt")],
        )
        if not path:
            return
        write_puzzle_target_file(n, path)
        self.tc_target.set(path)
        self._append_console(f"[TrueNexus] Wrote puzzle target: {path}\n")

    def _launch_puzzle(self) -> None:
        self._apply_puzzle()
        if not self.tc_target.get().strip():
            self._write_puzzle_file()
        self.tc_dry.deselect()
        self._launch_collider()

    def _quick_puzzle66(self) -> None:
        self.tabs.set("Puzzles")
        self.puzzle_menu.set(all_puzzle_labels()[65])
        self._on_puzzle(self.puzzle_menu.get())
        self._apply_puzzle()

    # ── Mnemonic Lab ────────────────────────────────────────────────────
    def _build_mnemonic(self) -> None:
        tab = self.tabs.tab("Mnemonic Lab")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Full mnemonic ecosystem")
        self._label(
            f,
            "Live today: random BIP-39 → PBKDF2 → BIP-44/49/84.\n"
            "Research dropdowns (mask, passphrase, Electrum, SLIP39, …) are wired in the UI and annotated in previews\n"
            "so the suite is ready as TrueCollider kernels land.",
            text_color=self.theme["muted"],
        ).pack(anchor="w")

        g = ctk.CTkFrame(f, fg_color="transparent")
        g.pack(fill="x", pady=6)
        self.mn_sub = self._dropdown(g, "Mnemonic submode", MNEMONIC_SUBMODES, "random (live)", 0, 0)
        self.mn_words_menu = self._dropdown(g, "Words (-w)", ["0", "12", "15", "18", "21", "24"], "12", 0, 1)
        self.mn_words = ctk.StringVar(value="12")
        self.mn_words_menu.configure(command=lambda v: self.mn_words.set(v))
        self.mn_lang_menu = self._dropdown(g, "Language (-L)", LANGS, "english", 1, 0)
        self.mn_lang = ctk.StringVar(value="english")
        self.mn_lang_menu.configure(command=lambda v: self.mn_lang.set(v))
        self.mn_depth = self._entry(g, "Index depth (-D)", "5", 1, 1)

        self.mn_mask = ctk.StringVar()
        self._label(f, "Seed mask / known words (use ? for unknown)", text_color=self.theme["muted"]).pack(anchor="w", pady=(8, 2))
        ctk.CTkEntry(f, textvariable=self.mn_mask, placeholder_text="abandon ? ? zoo ... about").pack(fill="x")

        self.mn_pass = ctk.StringVar()
        self._path_row(f, "Passphrase dictionary (25th word)", self.mn_pass)

        self.mn_eth = ctk.CTkCheckBox(f, text="ETH keccak checks (-W)  [note: live paths still use coin-type 0']")
        self.mn_eth.pack(anchor="w", pady=8)

        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", pady=8)
        ctk.CTkButton(row, text="Apply → TrueCollider (mnemonic)", command=self._apply_mnemonic).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Preview & Launch", fg_color=self.theme["accent"], text_color="#111",
                      command=self._launch_mnemonic).pack(side="left", padx=4)

        self._section(f, "Path packs (research-ready presets)")
        for name, path in [
            ("BTC standard", "m/44'/0'/0'/0 + m/49' + m/84' + m/86'"),
            ("ETH Ledger Live", "m/44'/60'/0'/0  and  m/44'/60'/0'"),
            ("Electrum", "m/0/  and  m/1/ gap"),
            ("Solana BIP39", "ed25519 SLIP-0010 paths"),
        ]:
            self._label(f, f"• {name}: {path}", text_color=self.theme["muted"]).pack(anchor="w")

    def _apply_mnemonic(self) -> None:
        self.tc_mode.set("mnemonic")
        self.mn_words.set(self.mn_words_menu.get())
        self.mn_lang.set(self.mn_lang_menu.get())
        self.tabs.set("TrueCollider")
        self._set_status("Mnemonic lab settings applied")

    def _launch_mnemonic(self) -> None:
        self._apply_mnemonic()
        self._launch_collider()

    # ── BSGS Lab ────────────────────────────────────────────────────────
    def _build_bsgs(self) -> None:
        tab = self.tabs.tab("BSGS Lab")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Baby-Step Giant-Step & hybrid DL")
        self._label(
            f,
            "Live strategies: sequential / backward / both / random / dance.\n"
            "Research: grumpy, interleave, orbit, residue, handoff (HerdHandoff), negmap, nested, async-resolve…",
            text_color=self.theme["muted"],
        ).pack(anchor="w")

        g = ctk.CTkFrame(f, fg_color="transparent")
        g.pack(fill="x")
        self.bsgs_strat = self._dropdown(g, "Strategy (-B)", BSGS_STRATEGIES, "random", 0, 0)
        self.bsgs_k = self._entry(g, "K factor (-k)", "auto", 0, 1)
        self.bsgs_n = self._entry(g, "Table N (-n)", "0x100000000000", 1, 0)
        self.bsgs_mod = self._entry(g, "Residue M:R (research)", "", 1, 1)

        tips = (
            "RAM guide: 8G→-k512 | 16G→-k1024 | 32G→-k2048 | 64G+→raise -n and -k\n"
            "Pubkey required in -f (66 or 130 hex). Prefer kangaroo when N is huge.\n"
            "HerdHandoff: run coarse BSGS then auto-pocket kangaroo (research).\n"
        )
        self._label(f, tips, justify="left").pack(anchor="w", pady=8)
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkButton(row, text="Apply BSGS → TrueCollider", command=self._apply_bsgs).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Launch", fg_color=self.theme["accent"], text_color="#111",
                      command=self._launch_bsgs).pack(side="left", padx=4)

    def _apply_bsgs(self) -> None:
        self.tc_mode.set("bsgs")
        self.tc_save.select()
        self.tabs.set("TrueCollider")
        self._set_status("BSGS lab applied")

    def _launch_bsgs(self) -> None:
        self._apply_bsgs()
        self._launch_collider()

    # ── Address / RMD160 ────────────────────────────────────────────────
    def _build_address(self) -> None:
        tab = self.tabs.tab("Address / RMD160")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Address & hash160 hunting")
        g = ctk.CTkFrame(f, fg_color="transparent")
        g.pack(fill="x")
        self.addr_mode = self._dropdown(g, "Mode", ["address", "rmd160", "xpoint", "pubkey2addr", "shadow160 (research)"], "address", 0, 0)
        self.addr_filter = self._dropdown(g, "Filter strategy", FILTER_STRATS, "default fuse", 0, 1)
        self.addr_path = self._entry(g, "BIP-32 path (-p)", "m/84'/0'/0'/0", 1, 0)
        self.addr_depth = self._entry(g, "Depth (-D)", "10", 1, 1)

        self._label(
            f,
            "shadow160 = birthday / partial RIPEMD-160 collider (research).\n"
            "FuseCascade / fuse16 = multi-resolution filters for huge target lists (research).\n"
            "Hilbert / Sobol patterns live under Pattern (-x) on the TrueCollider tab.",
            text_color=self.theme["muted"],
        ).pack(anchor="w", pady=8)
        ctk.CTkButton(f, text="Apply → TrueCollider", command=self._apply_address).pack(anchor="w", pady=4)

    def _apply_address(self) -> None:
        mode = self.addr_mode.get().split(" (")[0]
        self.tc_mode.set(mode if mode in MODES_LIVE else "rmd160")
        self.tabs.set("TrueCollider")

    # ── TrueMkey ────────────────────────────────────────────────────────
    def _build_mkey(self) -> None:
        tab = self.tabs.tab("TrueMkey")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "TrueMkeyCollider — CUDA AES mkey/ckey")
        self._label(
            f,
            "GPU AES-256 trials against Bitcoin Core wallet.dat encrypted keys.\n"
            "Partial-key mode (--partial) is where GPU earns its keep. Full 2^256 is not feasible.",
            text_color=self.theme["muted"],
        ).pack(anchor="w")

        self.mk_exe = ctk.StringVar(value=self.settings.get("truemkey_exe", ""))
        self._path_row(f, "TrueMkeyCollider.exe", self.mk_exe, exe=True)
        self.mk_ckeys = ctk.StringVar()
        self.mk_mkeys = ctk.StringVar()
        self.mk_pubs = ctk.StringVar()
        self._path_row(f, "ckeys file (-ckeys)", self.mk_ckeys)
        self._path_row(f, "mkeys file (-mckey)", self.mk_mkeys)
        self._path_row(f, "pubkeys file (-pubkeys) optional", self.mk_pubs)

        g = ctk.CTkFrame(f, fg_color="transparent")
        g.pack(fill="x")
        self.mk_mode = self._dropdown(g, "Walk", ["random", "sequential", "mixed"], "random", 0, 0)
        self.mk_grid = self._entry(g, "Grid -g", "256,256", 0, 1)
        self.mk_streams = self._entry(g, "Streams", "4", 1, 0)
        self.mk_mem = self._entry(g, "Memory -M", "auto", 1, 1)
        self.mk_dev = self._entry(g, "Device -d", "0", 2, 0)
        self.mk_partial = self._entry(g, "Partial prefix", "", 2, 1)
        self.mk_try = self._entry(g, "--try HEX", "", 3, 0)
        self.mk_limit = self._entry(g, "Limit -n", "", 3, 1)

        self.mk_selftest = ctk.CTkCheckBox(f, text="Self-test PoC (--selftest)")
        self.mk_selftest.pack(anchor="w", pady=6)

        self.mk_preview = ctk.CTkTextbox(f, height=80, font=ctk.CTkFont(family="Consolas", size=13))
        self.mk_preview.pack(fill="x", pady=6)
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkButton(row, text="Preview", command=self._preview_mkey).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Copy", command=lambda: self._copy_text(self.mk_preview.get("1.0", "end"))).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Launch TrueMkey", fg_color=self.theme["accent"], text_color="#111",
                      command=self._launch_mkey).pack(side="left", padx=4)

    def _preview_mkey(self) -> None:
        cfg = MkeyConfig(
            exe=self.mk_exe.get().strip() or "TrueMkeyCollider.exe",
            ckeys=self.mk_ckeys.get().strip(),
            mkeys=self.mk_mkeys.get().strip(),
            pubkeys=self.mk_pubs.get().strip(),
            mode=self.mk_mode.get(),
            device=self.mk_dev.get().strip() or "0",
            grid=self.mk_grid.get().strip() or "256,256",
            streams=self.mk_streams.get().strip() or "4",
            memory=self.mk_mem.get().strip() or "auto",
            limit=self.mk_limit.get().strip(),
            partial=self.mk_partial.get().strip(),
            try_key=self.mk_try.get().strip(),
            selftest=bool(self.mk_selftest.get()),
        )
        self.mk_preview.delete("1.0", "end")
        self.mk_preview.insert("1.0", cfg.build())

    def _launch_mkey(self) -> None:
        self._preview_mkey()
        cmd = self.mk_preview.get("1.0", "end").strip()
        self.settings["truemkey_exe"] = self.mk_exe.get().strip()
        cwd = str(Path(self.mk_exe.get()).parent) if self.mk_exe.get() else None
        self.runner.start(cmd, cwd=cwd)

    # ── Ideas Matrix ────────────────────────────────────────────────────
    def _build_ideas(self) -> None:
        tab = self.tabs.tab("Ideas Matrix")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Research algorithms & modes")
        ideas = [
            ("OrbitBSGS", "Endomorphism-collapsed baby table for smaller RAM at same coverage."),
            ("HerdHandoff", "BSGS localizes a pocket → kangaroo finishes. Hybrid DL pipeline."),
            ("GrumpyBSGS", "Bernstein–Lange two grumpy giants + baby — better average-case."),
            ("InterleaveBSGS", "Average-case interleaved baby/giant work."),
            ("GaudrySchost / ResidueHerd", "Modular constraints k≡r (mod m); multi-dimensional walks."),
            ("FuseCascade", "Coarse→mid→exact multi-resolution filters for huge address sets."),
            ("HilbertStride / SobolWalk", "Quasirandom coverage stronger than plain random/chaos."),
            ("Shadow160", "Partial RIPEMD-160 birthday collider (DP herds)."),
            ("CrystalPRNG", "Milk Sad / Randstorm / Android SecureRandom / Profanity keyspaces."),
            ("MnemonicLattice", "Checksum-valid entropy enumeration, not word-by-word thrash."),
            ("ChecksumPrism", "One entropy → all BIP-39 languages in one pass."),
            ("PathNova", "Budgeted wallet path packs (Ledger/Trezor/MetaMask/Electrum)."),
            ("WordOrbit", "Fuzzy memory expansion: edit distance, phonetic, prefix."),
            ("SeedCascadeVerify", "Cheapest checks first: wordlist→checksum→PBKDF2→paths."),
            ("PhraseGravity", "Bias seed search after near-misses (gravity for mnemonic space)."),
            ("Producer/Consumer GPU", "Split checksum / PBKDF2 / EC across GPUs."),
        ]
        for title, desc in ideas:
            card = ctk.CTkFrame(f, fg_color=self.theme["fg"], corner_radius=8)
            card.pack(fill="x", pady=4)
            ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=14, weight="bold"),
                         text_color=self.theme["accent"]).pack(anchor="w", padx=10, pady=(8, 0))
            ctk.CTkLabel(card, text=desc, text_color=self.theme["muted"], wraplength=620,
                         justify="left").pack(anchor="w", padx=10, pady=(2, 8))

        self._section(f, "Flag encyclopedia (hover-level explanations)")
        for fl in ["-m", "-f", "-b", "-r", "-x", "-B", "-k", "-e", "-U", "-M", "-w", "-L", "--partial", "--selftest"]:
            self._label(f, f"{fl:12}  {explain_flag(fl)}", text_color=self.theme["muted"]).pack(anchor="w")

    # ── Settings ────────────────────────────────────────────────────────
    def _build_settings(self) -> None:
        tab = self.tabs.tab("Settings")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Paths & preferences")
        self.set_tc = ctk.StringVar(value=self.settings.get("truecollider_exe", ""))
        self.set_tcc = ctk.StringVar(value=self.settings.get("truecollider_cuda", ""))
        self.set_mk = ctk.StringVar(value=self.settings.get("truemkey_exe", ""))
        self.set_wd = ctk.StringVar(value=self.settings.get("workdir", ""))
        self._path_row(f, "TrueCollider CPU exe", self.set_tc, exe=True)
        self._path_row(f, "TrueCollider CUDA exe", self.set_tcc, exe=True)
        self._path_row(f, "TrueMkeyCollider exe", self.set_mk, exe=True)
        self._path_row(f, "Default workdir", self.set_wd, directory=True)
        ctk.CTkButton(f, text="Save Settings", fg_color=self.theme["accent"], text_color="#111",
                      command=self._persist_settings).pack(anchor="w", pady=12)
        ctk.CTkButton(f, text="Open logs folder", command=lambda: os.startfile(str(LOG_DIR))).pack(anchor="w")

    def _persist_settings(self) -> None:
        self.settings["truecollider_exe"] = self.set_tc.get().strip()
        self.settings["truecollider_cuda"] = self.set_tcc.get().strip()
        self.settings["truemkey_exe"] = self.set_mk.get().strip()
        self.settings["workdir"] = self.set_wd.get().strip()
        self.tc_exe.set(self.settings["truecollider_exe"])
        self.tc_cwd.set(self.settings["workdir"])
        self.mk_exe.set(self.settings["truemkey_exe"])
        self._save_settings()

    # ── About ───────────────────────────────────────────────────────────
    def _build_about(self) -> None:
        tab = self.tabs.tab("About")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "TrueNexus by TrueScent")
        about = (
            f"Version {__version__}\n\n"
            "TrueNexus is the unified desktop command center for:\n"
            f"  • TrueCollider     {__truecollider__}\n"
            f"  • TrueMkeyCollider {__truemkey__}\n\n"
            f"Telegram: {__telegram__}\n"
            f"Donate BTC:\n{__donate_btc__}\n\n"
            "Built for recovery researchers, puzzle hunters, and wallet owners\n"
            "who need a serious interface — not a toy.\n\n"
            "Disclaimer: educational / authorized recovery only. You are responsible\n"
            "for lawful use on systems and wallets you own or have permission to test."
        )
        box = ctk.CTkTextbox(f, height=320)
        box.pack(fill="both", expand=True, pady=8)
        box.insert("1.0", about)
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkButton(row, text="Copy BTC address", command=self._copy_donate).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Open Telegram", command=self._open_telegram,
                      fg_color=self.theme["accent"], text_color="#111").pack(side="left", padx=4)

    # ── console helpers ─────────────────────────────────────────────────
    def _append_console(self, text: str) -> None:
        def _do() -> None:
            self.console.insert("end", text)
            self.console.see("end")
        self.after(0, _do)

    def _clear_console(self) -> None:
        self.console.delete("1.0", "end")

    def _copy_console(self) -> None:
        self._copy_text(self.console.get("1.0", "end"))

    def _copy_text(self, text: str) -> None:
        self.clipboard_clear()
        self.clipboard_append(text.strip())
        self._set_status("Copied to clipboard")

    def _copy_donate(self) -> None:
        self._copy_text(__donate_btc__)
        messagebox.showinfo("Donation", f"BTC address copied:\n{__donate_btc__}")

    def _open_telegram(self) -> None:
        self._open_url(__telegram__)

    def _open_url(self, url: str) -> None:
        import webbrowser
        webbrowser.open(url)

    def _run_raw_cmd(self) -> None:
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return
        cwd = self.tc_cwd.get().strip() or str(ROOT)
        self.cmd_entry.delete(0, "end")
        self.runner.start(cmd, cwd=cwd)

    def _on_proc_done(self, code: int) -> None:
        self.after(0, lambda: self._set_status(f"Process finished ({code})"))

    def _set_status(self, text: str) -> None:
        self.status.configure(text=text)

    def _on_theme(self, name: str) -> None:
        self.settings["theme"] = name
        messagebox.showinfo(
            "Theme",
            f"Theme '{name}' saved. Restart TrueNexus to fully re-skin all panels.\n"
            "(Console colors update on next launch.)",
        )
        self._save_settings()


def main() -> None:
    # Allow `python -m truenexus.app` from TrueNexus root
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    app = TrueNexusApp()
    app.mainloop()


if __name__ == "__main__":
    main()
