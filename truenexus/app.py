"""TrueNexus — professional GUI command center."""

from __future__ import annotations

import json
import os
import sys
import time
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from truenexus import __donate_btc__, __telegram__, __truecollider__, __truemkey__, __version__
from truenexus.builders import (
    ADDRESS_SUBMODES,
    BSGS_STRATEGIES,
    COINS,
    FILTER_STRATS,
    GPU,
    LANGS,
    LOOK,
    MNEMONIC_STRATEGIES,
    MNEMONIC_SUBMODES,
    MODES_ALL,
    MODES_LIVE,
    PATH_PACKS,
    RMD160_SUBMODES,
    SEARCH_PATTERNS,
    VECTOR,
    WEAKRNG_SUBMODES,
    ColliderConfig,
    MkeyConfig,
    explain_flag,
)
from truenexus.ideas_catalog import (
    ANTI_IDEAS,
    RECIPES as RECIPE_ITEMS,
    ROADMAP_P0,
    ROADMAP_P1,
    ROADMAP_P2,
    ROADMAP_P3,
    SOURCES,
    all_idea_cards,
    completeness_report,
)
from truenexus.builders import RECIPES as RECIPE_LABELS
from truenexus.directory import directory_stats, format_entry, search_directory
from truenexus.idea_labs import LAB_SPECS, lab_labels
from truenexus.wallet_forensics import export_for_truemkey, inspect_wallet_dat
from truenexus.chain_rpc import sync_chain_rpcs, list_main_rpcs, default_chains_dir
from truenexus.tools_registry import all_tools, search_tools, tools_stats
from truenexus.puzzles import (
    KNOWN_ADDR,
    KNOWN_PUBKEYS,
    has_known_pubkey,
    known_pubkey_puzzles,
    parse_puzzle_number,
    puzzle_label,
    puzzle_pubkey,
    puzzle_range_display,
    puzzle_range_hex,
    puzzle_status,
    recommend_mode,
    write_puzzle_target_file,
)
from truenexus.runner import ProcessRunner
from truenexus.themes import DEFAULT_THEME, THEMES
from truenexus.watch import WatchBook, parse_watch_lines, poll_once

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "presets" / "user_settings.json"
LOG_DIR = ROOT / "logs"
TOOLS_DIR = ROOT / "tools"


def _default_paths() -> dict:
    """Prefer bundled tools/ next to TrueNexus; then D:\\TrueScent; then Desktop."""
    collider = TOOLS_DIR / "TrueCollider"
    mkey = TOOLS_DIR / "TrueMkeyCollider"
    desktop = Path.home() / "Desktop"
    ds = Path("D:/TrueScent")

    def pick(*candidates: Path) -> str:
        for p in candidates:
            if p.is_file():
                return str(p.resolve())
        return str(candidates[0])

    tc_exe = pick(
        collider / "keyhunt.exe",
        ds / "TrueCollider" / "keyhunt.exe",
        desktop / "updayingkeyunt" / "TrueCollider-master" / "keyhunt.exe",
    )
    tc_cuda = pick(
        collider / "keyhunt_cuda.exe",
        ds / "TrueCollider" / "keyhunt_cuda.exe",
        desktop / "updayingkeyunt" / "TrueCollider-master" / "keyhunt_cuda.exe",
    )
    mk_exe = pick(
        mkey / "TrueMkeyCollider.exe",
        ds / "TrueMkeyCollider" / "TrueMkeyCollider.exe",
        desktop / "TrueMkeyCollider" / "TrueMkeyCollider.exe",
    )
    if collider.is_dir():
        workdir = collider
    elif (ds / "TrueCollider").is_dir():
        workdir = ds / "TrueCollider"
    else:
        workdir = desktop / "updayingkeyunt" / "TrueCollider-master"
    return {
        "truecollider_exe": tc_exe,
        "truecollider_cuda": tc_cuda,
        "truemkey_exe": mk_exe,
        "workdir": str(workdir.resolve()) if workdir.exists() else str(collider),
        "theme": DEFAULT_THEME,
    }


class TrueNexusApp(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()
        self.title(f"TrueNexus  ·  v{__version__}  ·  by TrueScent")
        self.geometry("1540x920")
        self.minsize(1280, 760)
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        (ROOT / "presets").mkdir(parents=True, exist_ok=True)

        self.settings = _default_paths()
        self._load_settings()
        self.theme_name = self.settings.get("theme", DEFAULT_THEME)
        self._apply_theme(self.theme_name)

        self.runner = ProcessRunner(self._append_console, self._on_proc_done)
        self._console_q: list[str] = []
        self._status_q: list[str] = []
        # Buffered console refresh (GPU spam crashed the GUI when flushing every 50ms)
        try:
            self._console_refresh_sec = int(self.settings.get("console_refresh_sec", 10))
        except Exception:
            self._console_refresh_sec = 10
        if self._console_refresh_sec not in (5, 10, 15, 20):
            self._console_refresh_sec = 10
        self._console_last_flush = 0.0
        self._console_force_flush = True  # show startup banner immediately
        self._console_pending_bytes = 0
        self._console_dropped_note = False
        self._build_ui()
        self.after(200, self._ui_tick)
        self._append_console(
            f"TrueNexus v{__version__} online.\n"
            f"Telegram: {__telegram__}\n"
            f"Donate BTC: {__donate_btc__}\n"
            f"Tools: TrueCollider · TrueMkeyCollider\n"
            f"Bundled tools dir: {TOOLS_DIR}\n"
            f"  keyhunt: {self.settings.get('truecollider_exe')}\n"
            f"  mkey:    {self.settings.get('truemkey_exe')}\n"
            f"Console refresh: every {self._console_refresh_sec}s (change above the console for GPU runs).\n"
            "Tip: use Dry-Run before long GPU jobs. Edit Settings anytime — Save persists paths.\n"
            "Console Run executes shell commands in the workdir. Stop cancels the child process.\n\n"
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
        body.grid_columnconfigure(0, weight=0)  # sidebar
        body.grid_columnconfigure(1, weight=3)  # main pages
        body.grid_columnconfigure(2, weight=2)  # console
        body.grid_rowconfigure(0, weight=1)

        # Sidebar nav (replaces squashed horizontal CTkTabview strip)
        # Sidebar nav — Core · Labs · Tools · Docs
        nav_names = (
            "Home",
            "Directory",
            "TrueCollider",
            "Puzzles",
            "Mnemonic Lab",
            "Passphrase Lab",
            "PathNova Lab",
            "BSGS Lab",
            "BSGS Strategies",
            "Kangaroo Lab",
            "Address / RMD160",
            "Address Subs",
            "Shadow160 Lab",
            "Patterns Lab",
            "Filters Lab",
            "WeakRNG Lab",
            "WeakRNG Full",
            "Vanity Lab",
            "Algorithms Lab",
            "GPU Lab",
            "Multi-coin Lab",
            "Research 2026",
            "TrueMkey",
            "Wallet Lab",
            "Collider Lab",
            "Ops Lab",
            "Tools Arsenal",
            "Chain RPCs",
            "Address Watch",
            "Ideas Matrix",
            "Roadmap",
            "Recipes",
            "Full Ideas Doc",
            "Settings",
            "About",
        )
        sidebar = ctk.CTkFrame(body, fg_color=self.theme["card"], width=220, corner_radius=10)
        sidebar.grid(row=0, column=0, sticky="nsw", padx=(0, 8))
        sidebar.grid_propagate(False)
        ctk.CTkLabel(
            sidebar, text="NAV", font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.theme["muted"],
        ).pack(anchor="w", padx=14, pady=(12, 6))
        nav_scroll = ctk.CTkScrollableFrame(sidebar, fg_color="transparent", width=200)
        nav_scroll.pack(fill="both", expand=True, padx=6, pady=(0, 10))

        content_host = ctk.CTkFrame(body, fg_color=self.theme["card"], corner_radius=10)
        content_host.grid(row=0, column=1, sticky="nsew", padx=(0, 8))
        content_host.grid_rowconfigure(0, weight=1)
        content_host.grid_columnconfigure(0, weight=1)

        self._nav_buttons: dict[str, ctk.CTkButton] = {}
        self._nav_pages: dict[str, ctk.CTkFrame] = {}
        self._nav_current = "Home"

        class _TabProxy:
            """Drop-in for CTkTabview: .tab(name) / .set(name)."""

            def __init__(self, app: "TrueNexusApp") -> None:
                self._app = app

            def tab(self, name: str) -> ctk.CTkFrame:
                return self._app._nav_pages[name]

            def set(self, name: str) -> None:
                self._app._show_nav(name)

            def add(self, name: str) -> None:
                page = ctk.CTkFrame(content_host, fg_color="transparent")
                self._app._nav_pages[name] = page

        self.tabs = _TabProxy(self)
        for name in nav_names:
            self.tabs.add(name)
            btn = ctk.CTkButton(
                nav_scroll,
                text=name,
                anchor="w",
                height=34,
                fg_color="transparent",
                text_color=self.theme["text"],
                hover_color=self.theme["fg"],
                command=lambda n=name: self._show_nav(n),
            )
            btn.pack(fill="x", pady=2, padx=4)
            self._nav_buttons[name] = btn

        self._build_home()
        self._build_directory()
        self._build_collider()
        self._build_puzzles()
        self._build_mnemonic()
        self._build_bsgs()
        self._build_address()
        self._build_weakrng()
        self._build_idea_labs()  # Passphrase, PathNova, Kangaroo, Shadow160, …
        self._build_mkey()
        self._build_wallet_lab()
        self._build_collider_lab()
        self._build_ops_lab()
        self._build_tools_arsenal()
        self._build_chain_rpcs()
        self._build_watch()
        self._build_ideas()
        self._build_roadmap()
        self._build_recipes()
        self._build_ideas_doc()
        self._build_settings()
        self._build_about()
        self._show_nav("Home")

        # Console column
        cons = ctk.CTkFrame(body, fg_color=self.theme["card"])
        cons.grid(row=0, column=2, sticky="nsew")
        cons.grid_rowconfigure(1, weight=1)
        cons.grid_columnconfigure(0, weight=1)

        topc = ctk.CTkFrame(cons, fg_color="transparent")
        topc.grid(row=0, column=0, sticky="ew", padx=10, pady=8)
        ctk.CTkLabel(topc, text="Embedded Console", font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=self.theme["accent"]).pack(side="left")
        ctk.CTkButton(topc, text="Copy All", width=80, command=self._copy_console).pack(side="right", padx=2)
        ctk.CTkButton(topc, text="Clear", width=70, command=self._clear_console).pack(side="right", padx=2)
        ctk.CTkButton(topc, text="Stop", width=70, fg_color=self.theme["danger"],
                      command=self._stop_and_flush).pack(side="right", padx=2)
        ctk.CTkButton(topc, text="Refresh now", width=100, command=self._refresh_console_now).pack(side="right", padx=2)
        self.console_refresh = ctk.CTkOptionMenu(
            topc,
            values=["5 sec", "10 sec", "15 sec", "20 sec"],
            width=90,
            command=self._on_console_refresh,
        )
        self.console_refresh.set(f"{self._console_refresh_sec} sec")
        self.console_refresh.pack(side="right", padx=4)
        ctk.CTkLabel(topc, text="Refresh", text_color=self.theme["muted"]).pack(side="right", padx=(8, 2))

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

    def _show_nav(self, name: str) -> None:
        """Switch sidebar page — keeps labels fully readable (no squashed tab strip)."""
        if name not in self._nav_pages:
            return
        for n, page in self._nav_pages.items():
            page.grid_forget()
        page = self._nav_pages[name]
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_rowconfigure(0, weight=1)
        page.grid_columnconfigure(0, weight=1)
        self._nav_current = name
        for n, btn in self._nav_buttons.items():
            if n == name:
                btn.configure(
                    fg_color=self.theme["accent"],
                    text_color="#111111",
                    hover_color=self.theme["accent2"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=self.theme["text"],
                    hover_color=self.theme["fg"],
                )
        self._set_status(f"{name}")

    def _scroll(self, parent: ctk.CTkFrame) -> ctk.CTkScrollableFrame:
        return ctk.CTkScrollableFrame(parent, fg_color="transparent")

    def _label(self, parent, text: str, **kw):
        kw.setdefault("text_color", self.theme["text"])
        kw.setdefault("anchor", "w")
        return ctk.CTkLabel(parent, text=text, **kw)

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
            "• Idea Labs — every idea group has its own tab (Mnemonic, Passphrase, Kangaroo, …)\n"
            "• Directory — how to use EVERY mode, flag, and setting\n\n"
            "New users: open Directory → search your goal, or Puzzles → #66 → Dry-Run → Launch.\n"
            "Pros: jump straight to the lab tab for that algorithm, then Preview on TrueCollider.\n"
            "Everyone: the console on the right is a real shell — copy, paste, run, stop."
        )
        self._label(f, blurb, justify="left").pack(anchor="w", pady=4)
        btns = ctk.CTkFrame(f, fg_color="transparent")
        btns.pack(anchor="w", pady=12)
        ctk.CTkButton(btns, text="Open Directory", command=lambda: self.tabs.set("Directory"),
                      fg_color=self.theme["accent"], text_color="#111").pack(side="left", padx=4)
        ctk.CTkButton(btns, text="Open TrueCollider Repo", command=lambda: self._open_url(__truecollider__)).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="Open TrueMkey Repo", command=lambda: self._open_url(__truemkey__)).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="Quick Puzzle 66", command=self._quick_puzzle66).pack(side="left", padx=4)

        self._section(f, "Mode advisor")
        self.advisor = ctk.CTkTextbox(f, height=120)
        self.advisor.pack(fill="x", pady=4)
        self.advisor.insert("1.0", self._advisor_text())
        self.advisor.configure(state="disabled")

        self._section(f, "Roadmap snapshot")
        self._label(
            f,
            "P0: " + " · ".join(ROADMAP_P0[:3]) + "...\n"
            "P1: " + " · ".join(ROADMAP_P1[:3]) + "...\n"
            "P2: " + " · ".join(ROADMAP_P2[:3]) + "...\n"
            "P3: " + " · ".join(ROADMAP_P3[:3]) + "...\n"
            "Full catalog lives in Ideas Matrix / Full Ideas Doc (loaded on demand).",
            text_color=self.theme["muted"],
            justify="left",
        ).pack(anchor="w", pady=6)

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
        self.tc_mode = self._dropdown(grid, "Mode (-m) — ALL live + research", MODES_ALL, "address", 0, 0)
        self.tc_mode.configure(command=self._on_tc_mode)
        self.tc_coin = self._dropdown(grid, "Coin (-c)", COINS, "btc", 0, 1)
        self.tc_look = self._dropdown(grid, "Look (-l)", LOOK, "compress", 1, 0)
        self.tc_pattern = self._dropdown(grid, "Pattern (-x)", SEARCH_PATTERNS, "chaos", 1, 1)
        self.tc_gpu = self._dropdown(
            grid, "GPU (-U) — none=CPU / cuda / opencl / both", GPU,
            self.settings.get("default_gpu", "none"), 2, 0,
        )
        self.tc_gpu.configure(command=self._on_tc_gpu)
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
        self.tc_stride = self._entry(opts, "Stride (-I)", "", 4, 0)
        self.tc_time = self._entry(opts, "Time window (-T)", "", 4, 1)
        self.tc_collision = self._entry(opts, "Shadow bits", "48", 5, 0)
        self.tc_filter = self._dropdown(opts, "Filter (-F)", FILTER_STRATS, "default fuse", 5, 1)
        self.tc_words = self._entry(opts, "Words (-w)", "12", 6, 0)

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
        self.tc_balance = ctk.CTkCheckBox(flags, text="Balance check (-N)")
        self.tc_balance.pack(side="left", padx=6)

        more = ctk.CTkFrame(f, fg_color="transparent")
        more.pack(fill="x", pady=4)
        self.tc_handoff = self._entry(more, "HerdHandoff -H bits", "44", 0, 0)
        self.tc_balance_url = self._entry(more, "-N URL optional", "", 0, 1)
        self.tc_density = ctk.StringVar()
        self._path_row(f, "Density-map prior file (research)", self.tc_density)
        self.tc_funded = ctk.StringVar()
        self._path_row(f, "Funded-only UTXO/hash160 snapshot (research)", self.tc_funded)
        self.tc_wifmask = self._entry(
            ctk.CTkFrame(f, fg_color="transparent"), "WIF/hex mask pattern", "", 0, 0
        )

        # BSGS / DL settings — shown automatically when mode needs a pubkey
        self.tc_bsgs_frame = ctk.CTkFrame(f, fg_color=self.theme.get("card", "#1a1a22"), corner_radius=8)
        self._build_bsgs_controls(self.tc_bsgs_frame)
        self._tc_bsgs_visible = False

        self.tc_preview = ctk.CTkTextbox(f, height=90, font=ctk.CTkFont(family="Consolas", size=13))
        self.tc_preview.pack(fill="x", pady=8)
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkButton(row, text="Preview Command", command=self._preview_collider).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Copy Command", command=lambda: self._copy_text(self.tc_preview.get("1.0", "end"))).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Launch TrueCollider", fg_color=self.theme["accent"], text_color="#111",
                      command=self._launch_collider).pack(side="left", padx=4)
        self._sync_tc_bsgs_panel()

    def _on_tc_gpu(self, _value: str | None = None) -> None:
        """Keep TrueMkey + Settings compute box in sync with TrueCollider GPU."""
        if not hasattr(self, "tc_gpu"):
            return
        val = self.tc_gpu.get()
        if hasattr(self, "mk_gpu"):
            try:
                self.mk_gpu.set(val)
                self._sync_mk_gpu_panel()
            except Exception:
                pass
        if hasattr(self, "set_gpu"):
            try:
                self.set_gpu.set(val)
            except Exception:
                pass
        self.settings["default_gpu"] = val
        self._set_status(f"Compute: {val} (TrueCollider + TrueMkey)")

    def _mode_token(self, label: str | None = None) -> str:
        raw = (label if label is not None else self.tc_mode.get()) or ""
        return raw.split(" (")[0].strip().lower()

    def _set_tc_mode(self, token: str) -> None:
        """Set Mode dropdown by live token (bsgs, kangaroo, …) and refresh BSGS panel."""
        token = (token or "").strip().lower()
        vals = list(getattr(self.tc_mode, "_values", []) or [])
        chosen = None
        for v in vals:
            if v.lower() == token or v.lower().startswith(token + " ") or v.lower().startswith(token + "("):
                chosen = v
                break
            if token and token == v.split(" (")[0].strip().lower():
                chosen = v
                break
        if chosen:
            self.tc_mode.set(chosen)
        self._on_tc_mode(chosen or token)

    def _on_tc_mode(self, _value: str | None = None) -> None:
        self._sync_tc_bsgs_panel(apply_defaults=True)

    def _is_dl_mode(self, token: str | None = None) -> bool:
        t = token or self._mode_token()
        return t in ("bsgs", "kangaroo", "hybrid-dl", "gaudry", "xpoint")

    def _sync_tc_bsgs_panel(self, apply_defaults: bool = False) -> None:
        """Show full BSGS settings on TrueCollider when a DL/pubkey mode is selected."""
        if not hasattr(self, "tc_bsgs_frame") or not hasattr(self, "tc_preview"):
            return
        token = self._mode_token()
        show = self._is_dl_mode(token)
        if show and not getattr(self, "_tc_bsgs_visible", False):
            self.tc_bsgs_frame.pack(fill="x", pady=8, padx=2, before=self.tc_preview)
            self._tc_bsgs_visible = True
        elif not show and getattr(self, "_tc_bsgs_visible", False):
            self.tc_bsgs_frame.pack_forget()
            self._tc_bsgs_visible = False
        if show and apply_defaults:
            self._apply_bsgs_defaults(token)

    def _apply_bsgs_defaults(self, token: str | None = None) -> None:
        token = token or self._mode_token()
        if hasattr(self, "tc_save"):
            self.tc_save.select()
        if token == "hybrid-dl" and hasattr(self, "bsgs_strat"):
            for v in getattr(self.bsgs_strat, "_values", []) or []:
                if v.split(" (")[0].strip().lower() == "handoff":
                    self.bsgs_strat.set(v)
                    break
        if hasattr(self, "bsgs_h") and hasattr(self, "tc_handoff"):
            h = self.bsgs_h.get().strip() or self.tc_handoff.get().strip() or "44"
            self.bsgs_h.set(h)
            self.tc_handoff.set(h)
        self._set_status(f"TrueCollider: {token} — BSGS / DL settings ready")

    def _build_bsgs_controls(self, parent) -> None:
        """Shared BSGS / hybrid-DL controls (TrueCollider panel)."""
        pad = ctk.CTkFrame(parent, fg_color="transparent")
        pad.pack(fill="x", padx=10, pady=8)
        self._section(pad, "BSGS / DL settings (-B -k -n -H)")
        self._label(
            pad,
            "Shown automatically for bsgs · kangaroo · hybrid-dl · gaudry · xpoint.\n"
            "Need a compressed/uncompressed pubkey in -f. Puzzle known-pubkey list: "
            + ", ".join(str(n) for n in known_pubkey_puzzles()),
            text_color=self.theme["muted"],
        ).pack(anchor="w", pady=(0, 6))
        g = ctk.CTkFrame(pad, fg_color="transparent")
        g.pack(fill="x")
        self.bsgs_strat = self._dropdown(g, "Strategy (-B) — ALL live + research", BSGS_STRATEGIES, "random", 0, 0)
        self.bsgs_k = self._entry(g, "K factor (-k)", "auto", 0, 1)
        self.bsgs_n = self._entry(g, "Table N (-n)", "0x100000000000", 1, 0)
        self.bsgs_mod = self._entry(g, "Residue M:R (Gaudry/ResidueHerd)", "", 1, 1)
        self.bsgs_r2 = self._entry(g, "Dual-range second START:END", "", 2, 0)
        self.bsgs_h = self._entry(g, "Handoff pocket bits -H", "44", 2, 1)
        self.bsgs_freeze = ctk.CTkCheckBox(g, text="freeze-table (research)")
        self.bsgs_freeze.grid(row=3, column=0, sticky="w", padx=6, pady=4)
        self.bsgs_batch = ctk.CTkCheckBox(g, text="batched-gpu-giants (research)")
        self.bsgs_batch.grid(row=3, column=1, sticky="w", padx=6, pady=4)

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
        vals = list(values) if values else ["(none)"]
        # Match default to a real value (prefix match) — prevents blank/broken OptionMenus
        chosen = vals[0]
        d = (default or "").strip()
        if d in vals:
            chosen = d
        else:
            token = d.split(" (")[0].strip().lower()
            for v in vals:
                if v.lower() == token or v.lower().startswith(token + " ") or v.lower().startswith(token + "("):
                    chosen = v
                    break
                if token and token == v.split(" (")[0].strip().lower():
                    chosen = v
                    break
        menu = ctk.CTkOptionMenu(box, values=vals, width=220)
        menu.set(chosen)
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
            balance_check=bool(self.tc_balance.get()) if hasattr(self, "tc_balance") else False,
            balance_url=self.tc_balance_url.get().strip() if hasattr(self, "tc_balance_url") else "",
            handoff_bits=(
                self.tc_handoff.get().strip() if hasattr(self, "tc_handoff") else ""
            ) or (self.bsgs_h.get().strip() if hasattr(self, "bsgs_h") else ""),
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
            mnemonic_words=(
                (self.mn_words.get() if hasattr(self, "mn_words") else "")
                or (self.tc_words.get().strip() if hasattr(self, "tc_words") else "")
                or "12"
            ),
            mnemonic_lang=getattr(self, "mn_lang", ctk.StringVar(value="english")).get()
            if hasattr(self, "mn_lang") else "english",
            mnemonic_eth=bool(self.mn_eth.get()) if hasattr(self, "mn_eth") else False,
            mnemonic_submode=self.mn_sub.get() if hasattr(self, "mn_sub") else "random",
            mnemonic_strategy=self.mn_strat.get() if hasattr(self, "mn_strat") else "checksum-first (research)",
            seed_mask=(
                (self.mn_mask.get().strip() if hasattr(self, "mn_mask") and self.mn_mask.get().strip()
                 else (self.mn_known.get().strip() if hasattr(self, "mn_known") else ""))
            ),
            passphrase_file=self.mn_pass.get() if hasattr(self, "mn_pass") else "",
            passphrase_mask=self.mn_passmask.get() if hasattr(self, "mn_passmask") else "",
            passphrase_rules=self.mn_rules.get() if hasattr(self, "mn_rules") else "",
            model_file=self.mn_model.get() if hasattr(self, "mn_model") else "",
            dual_target_file=self.mn_dual.get() if hasattr(self, "mn_dual") else "",
            path_pack=self.mn_pack.get() if hasattr(self, "mn_pack") else "btc-std",
            include_change=bool(self.mn_change.get()) if hasattr(self, "mn_change") else True,
            include_bip86=bool(self.mn_bip86.get()) if hasattr(self, "mn_bip86") else True,
            derivation_path=self.addr_path.get() if hasattr(self, "addr_path") else "",
            derivation_depth=(
                self.mn_depth.get() if hasattr(self, "mn_depth") and self.tc_mode.get().startswith("mnemonic")
                else (self.addr_depth.get() if hasattr(self, "addr_depth") else "1")
            ),
            filter_strategy=(
                self.tc_filter.get() if hasattr(self, "tc_filter")
                else (self.addr_filter.get() if hasattr(self, "addr_filter") else "default fuse")
            ),
            address_sub=self.addr_sub.get() if hasattr(self, "addr_sub") else "default",
            rmd160_sub=self.rmd_sub.get() if hasattr(self, "rmd_sub") else "exact",
            weakrng_sub=self.wr_sub.get() if hasattr(self, "wr_sub") else "milksad",
            timestamp_window=(
                self.tc_time.get().strip() if hasattr(self, "tc_time") and self.tc_time.get().strip()
                else (self.wr_ts.get() if hasattr(self, "wr_ts") else "")
            ),
            residue_mr=self.bsgs_mod.get() if hasattr(self, "bsgs_mod") else "",
            collision_bits=(
                self.tc_collision.get().strip() if hasattr(self, "tc_collision") and self.tc_collision.get().strip()
                else (self.shadow_bits.get() if hasattr(self, "shadow_bits") else "48")
            ),
            stride=(
                self.tc_stride.get().strip() if hasattr(self, "tc_stride") and self.tc_stride.get().strip()
                else (self.addr_stride.get() if hasattr(self, "addr_stride") else "")
            ),
            density_map_file=self.tc_density.get() if hasattr(self, "tc_density") else "",
            funded_file=self.tc_funded.get() if hasattr(self, "tc_funded") else "",
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
            cfg.mnemonic_strategy = self.mn_strat.get() if hasattr(self, "mn_strat") else cfg.mnemonic_strategy
            cfg.mnemonic_words = self.mn_words.get()
            cfg.mnemonic_lang = self.mn_lang.get()
            cfg.mnemonic_eth = bool(self.mn_eth.get())
            cfg.seed_mask = self.mn_mask.get()
            cfg.passphrase_file = self.mn_pass.get()
            cfg.model_file = self.mn_model.get() if hasattr(self, "mn_model") else ""
            cfg.dual_target_file = self.mn_dual.get() if hasattr(self, "mn_dual") else ""
            cfg.path_pack = self.mn_pack.get() if hasattr(self, "mn_pack") else cfg.path_pack
            cfg.derivation_depth = self.mn_depth.get()
        if hasattr(self, "bsgs_mod"):
            cfg.residue_mr = self.bsgs_mod.get()
        if hasattr(self, "wr_sub"):
            cfg.weakrng_sub = self.wr_sub.get()
            cfg.timestamp_window = self.wr_ts.get()
        cmd, warns = cfg.build()
        self.tc_preview.delete("1.0", "end")
        self.tc_preview.insert("1.0", cmd)
        if warns:
            self._append_console("\n".join(warns) + "\n")
        self.status.configure(text="Command preview ready")

    def _launch_collider(self) -> None:
        self._preview_collider()
        cmd = self.tc_preview.get("1.0", "end").strip().split("  REM")[0].strip()
        if not cmd:
            messagebox.showerror("Launch", "Command is empty. Preview first.")
            return
        exe = self.tc_exe.get().strip()
        if not exe or not Path(exe).is_file():
            messagebox.showerror(
                "Launch",
                f"TrueCollider exe not found:\n{exe}\n\nFix path in Settings and Save.",
            )
            return
        cwd = self.tc_cwd.get().strip() or str(Path(exe).parent)
        if not Path(cwd).is_dir():
            messagebox.showerror("Launch", f"Working directory missing:\n{cwd}")
            return
        self.settings["truecollider_exe"] = exe
        self.settings["workdir"] = cwd
        self._set_status("Launching TrueCollider...")
        self.runner.start(cmd, cwd=cwd)

    # ── Puzzles ─────────────────────────────────────────────────────────
    def _build_puzzles(self) -> None:
        tab = self.tabs.tab("Puzzles")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Bitcoin Puzzle Challenge 1-160")
        self._label(
            f,
            "Type a puzzle number 1..160 (or use the slider). Ranges are exact: "
            "puzzle N = [2^(N-1) .. 2^N - 1].\n"
            "Target: Address grind, or Known pubkey → auto-switches TrueCollider to BSGS settings.\n"
            f"Known pubkeys built-in: {', '.join(str(n) for n in known_pubkey_puzzles())}.",
            text_color=self.theme["muted"],
        ).pack(anchor="w")

        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", pady=8)
        self._label(row, "Puzzle #", text_color=self.theme["muted"]).pack(side="left", padx=(0, 8))
        self.puzzle_num = ctk.StringVar(value="66")
        self.puzzle_entry = ctk.CTkEntry(row, textvariable=self.puzzle_num, width=80)
        self.puzzle_entry.pack(side="left", padx=4)
        self.puzzle_entry.bind("<Return>", lambda _e: self._refresh_puzzle())
        self.puzzle_entry.bind("<FocusOut>", lambda _e: self._refresh_puzzle())
        ctk.CTkButton(row, text="Go", width=60, command=self._refresh_puzzle).pack(side="left", padx=4)
        ctk.CTkButton(row, text="-1", width=40, command=lambda: self._nudge_puzzle(-1)).pack(side="left", padx=2)
        ctk.CTkButton(row, text="+1", width=40, command=lambda: self._nudge_puzzle(1)).pack(side="left", padx=2)

        kind_row = ctk.CTkFrame(f, fg_color="transparent")
        kind_row.pack(fill="x", pady=4)
        self._label(kind_row, "Target type", text_color=self.theme["muted"]).pack(side="left", padx=(0, 8))
        self.puzzle_kind = ctk.CTkOptionMenu(
            kind_row,
            values=["Address (grind)", "Known pubkey (BSGS)"],
            width=220,
            command=self._on_puzzle_kind,
        )
        self.puzzle_kind.set("Address (grind)")
        self.puzzle_kind.pack(side="left", padx=4)
        ctk.CTkButton(
            kind_row, text="Jump to next known pubkey", width=180,
            command=self._jump_known_pubkey_puzzle,
        ).pack(side="left", padx=8)

        self.puzzle_slider = ctk.CTkSlider(
            f, from_=1, to=160, number_of_steps=159, command=self._on_puzzle_slider
        )
        self.puzzle_slider.set(66)
        self.puzzle_slider.pack(fill="x", pady=6)

        self.puzzle_info = ctk.CTkTextbox(f, height=140, font=ctk.CTkFont(family="Consolas", size=13))
        self.puzzle_info.pack(fill="x", pady=4)
        self._refresh_puzzle()

        brow = ctk.CTkFrame(f, fg_color="transparent")
        brow.pack(fill="x", pady=8)
        ctk.CTkButton(brow, text="Apply Range -> TrueCollider", command=self._apply_puzzle).pack(side="left", padx=4)
        ctk.CTkButton(brow, text="Write target .txt", command=self._write_puzzle_file).pack(side="left", padx=4)
        ctk.CTkButton(
            brow, text="Launch Puzzle Job", fg_color=self.theme["accent"], text_color="#111",
            command=self._launch_puzzle,
        ).pack(side="left", padx=4)
        self.puzzle_dry = ctk.CTkCheckBox(brow, text="Dry-run first (-y)")
        self.puzzle_dry.select()
        self.puzzle_dry.pack(side="left", padx=12)

    def _current_puzzle(self) -> int:
        try:
            n = parse_puzzle_number(self.puzzle_num.get())
        except Exception:
            n = 66
            self.puzzle_num.set("66")
        if n < 1:
            n = 1
        if n > 160:
            n = 160
        self.puzzle_num.set(str(n))
        return n

    def _nudge_puzzle(self, delta: int) -> None:
        n = self._current_puzzle() + delta
        n = max(1, min(160, n))
        self.puzzle_num.set(str(n))
        self.puzzle_slider.set(n)
        self._refresh_puzzle()

    def _on_puzzle_slider(self, value: float) -> None:
        n = int(round(float(value)))
        self.puzzle_num.set(str(n))
        self._refresh_puzzle()

    def _on_puzzle_kind(self, value: str) -> None:
        if "pubkey" in (value or "").lower():
            n = self._current_puzzle()
            if not has_known_pubkey(n):
                nxt = self._next_known_pubkey(n)
                if nxt:
                    self.puzzle_num.set(str(nxt))
                    self.puzzle_slider.set(nxt)
            self._refresh_puzzle()
            self._set_status("Puzzle target: known pubkey → will apply BSGS settings")
        else:
            self._refresh_puzzle()

    def _next_known_pubkey(self, from_n: int) -> int | None:
        pubs = known_pubkey_puzzles()
        for n in pubs:
            if n > from_n:
                return n
        return pubs[0] if pubs else None

    def _jump_known_pubkey_puzzle(self) -> None:
        n = self._current_puzzle()
        pubs = known_pubkey_puzzles()
        nxt = self._next_known_pubkey(n) or (pubs[0] if pubs else None)
        if nxt is None:
            messagebox.showinfo("Known pubkeys", "No known-pubkey puzzles in catalog.")
            return
        self.puzzle_num.set(str(nxt))
        self.puzzle_slider.set(nxt)
        self.puzzle_kind.set("Known pubkey (BSGS)")
        self._refresh_puzzle()
        self._set_status(f"Jumped to puzzle #{nxt} (known pubkey)")

    def _puzzle_uses_pubkey(self) -> bool:
        kind = self.puzzle_kind.get() if hasattr(self, "puzzle_kind") else ""
        return "pubkey" in (kind or "").lower()

    def _refresh_puzzle(self) -> None:
        n = self._current_puzzle()
        try:
            self.puzzle_slider.set(n)
        except Exception:
            pass
        start, end = puzzle_range_hex(n)
        addr = KNOWN_ADDR.get(n, "(missing address)")
        st = puzzle_status(n)
        pub = puzzle_pubkey(n)
        pub_line = f"Pubkey:  {pub}\n" if pub else "Pubkey:  (none known — address grind only)\n"
        txt = (
            f"{puzzle_label(n)}\n"
            f"Source: https://privatekeys.pw/puzzles/bitcoin-puzzle-tx\n"
            f"Status: {st}\n"
            f"Bits: {n}   (keyspace 2^{n-1} .. 2^{n}-1)\n"
            f"Range: {puzzle_range_display(n)}\n"
            f"CLI:  -b {n}   or   -r {start}:{end}\n"
            f"Address: {addr}\n"
            f"{pub_line}"
            f"Recommended: {recommend_mode(n)}\n"
        )
        self.puzzle_info.delete("1.0", "end")
        self.puzzle_info.insert("1.0", txt)

    def _apply_puzzle(self) -> None:
        n = self._current_puzzle()
        start, end = puzzle_range_hex(n)
        self.tc_bits.set(str(n))
        self.tc_r0.set(start)
        self.tc_r1.set(end)
        use_pub = self._puzzle_uses_pubkey()
        if use_pub:
            if not has_known_pubkey(n):
                messagebox.showwarning(
                    "No known pubkey",
                    f"Puzzle #{n} has no built-in pubkey.\n"
                    f"Known: {', '.join(str(x) for x in known_pubkey_puzzles())}",
                )
                return
            mode = "kangaroo" if n >= 145 else "bsgs"
            self._set_tc_mode(mode)
            try:
                self._write_puzzle_file()
            except Exception as exc:
                messagebox.showerror("Pubkey target", str(exc))
                return
            self.tabs.set("TrueCollider")
            self._set_status(f"Applied puzzle #{n} as {mode} (known pubkey)")
            return
        try:
            self._set_tc_mode("address")
        except Exception:
            pass
        try:
            self.tc_pattern.set("chaos" if n <= 80 else "random")
        except Exception:
            pass
        self.tabs.set("TrueCollider")
        self._set_status(f"Applied puzzle #{n} range ({puzzle_range_display(n)})")

    def _write_puzzle_file(self) -> None:
        n = self._current_puzzle()
        use_pub = self._puzzle_uses_pubkey()
        if use_pub:
            if not has_known_pubkey(n):
                messagebox.showwarning("No pubkey", f"Puzzle #{n} has no known pubkey.")
                return
            kind = "pubkey"
        else:
            if n not in KNOWN_ADDR:
                messagebox.showwarning("No address", "Puzzle address missing from catalog.")
                return
            kind = "address"
        out_dir = Path(self.tc_cwd.get().strip() or ROOT / "presets")
        out_dir.mkdir(parents=True, exist_ok=True)
        suffix = "pub" if kind == "pubkey" else "addr"
        path = str(out_dir / f"puzzle_{n}_{suffix}.txt")
        write_puzzle_target_file(n, path, kind=kind)
        self.tc_target.set(path)
        self._append_console(f"[TrueNexus] Wrote puzzle target ({kind}): {path}\n")
        self._set_status(f"Wrote {path}")
        return path

    def _launch_puzzle(self) -> None:
        self._apply_puzzle()
        if not self.tc_target.get().strip():
            self._write_puzzle_file()
        if hasattr(self, "puzzle_dry") and self.puzzle_dry.get():
            self.tc_dry.select()
        else:
            self.tc_dry.deselect()
        self._launch_collider()

    def _quick_puzzle66(self) -> None:
        self.tabs.set("Puzzles")
        self.puzzle_num.set("66")
        self.puzzle_slider.set(66)
        self._refresh_puzzle()
        self._apply_puzzle()

    # ── Mnemonic Lab ────────────────────────────────────────────────────
    def _build_mnemonic(self) -> None:
        tab = self.tabs.tab("Mnemonic Lab")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Complete mnemonic ecosystem (every idea)")
        self._label(
            f,
            "Live today: random BIP-39 → PBKDF2 → BIP-44/49/84.\n"
            "ALL recovery / passphrase / Electrum / SLIP39 / strategy ideas are in the dropdowns.",
            text_color=self.theme["muted"],
        ).pack(anchor="w")

        g = ctk.CTkFrame(f, fg_color="transparent")
        g.pack(fill="x", pady=6)
        self.mn_sub = self._dropdown(g, "Submode (recovery/pass/ecosystem/paths)", MNEMONIC_SUBMODES, "random", 0, 0)
        self.mn_strat = self._dropdown(g, "Strategy (checksum-first, lattice, …)", MNEMONIC_STRATEGIES, "checksum-first", 0, 1)
        self.mn_words_menu = self._dropdown(g, "Words (-w)", ["0", "12", "15", "18", "21", "24"], "12", 1, 0)
        self.mn_words = ctk.StringVar(value="12")
        self.mn_words_menu.configure(command=lambda v: self.mn_words.set(v))
        self.mn_lang_menu = self._dropdown(g, "Language (-L)", LANGS, "english", 1, 1)
        self.mn_lang = ctk.StringVar(value="english")
        self.mn_lang_menu.configure(command=lambda v: self.mn_lang.set(v))
        self.mn_depth = self._entry(g, "Index depth (-D)", "5", 2, 0)
        self.mn_pack = self._dropdown(g, "PathNova pack", PATH_PACKS, "btc-std", 2, 1)

        self.mn_mask = ctk.StringVar()
        self._label(f, "Seed mask / known words (use ? or x for unknown)", text_color=self.theme["muted"]).pack(anchor="w", pady=(8, 2))
        ctk.CTkEntry(f, textvariable=self.mn_mask, placeholder_text="abandon ? ? zoo ... about").pack(fill="x")

        self.mn_known = ctk.StringVar()
        self._label(f, "Known full mnemonic (for pass-* / lastword modes)", text_color=self.theme["muted"]).pack(anchor="w", pady=(8, 2))
        ctk.CTkEntry(f, textvariable=self.mn_known, placeholder_text="twelve or twenty-four known words ...").pack(fill="x")

        self.mn_passmask = ctk.StringVar()
        self._label(f, "Passphrase hashcat mask (pass-mask) e.g. ?l?l?d?d", text_color=self.theme["muted"]).pack(anchor="w", pady=(8, 2))
        ctk.CTkEntry(f, textvariable=self.mn_passmask, placeholder_text="?l?l?l?d?d").pack(fill="x")

        self.mn_pass = ctk.StringVar()
        self.mn_rules = ctk.StringVar()
        self.mn_model = ctk.StringVar()
        self.mn_dual = ctk.StringVar()
        self._path_row(f, "Passphrase dictionary (pass-dict / pass-hybrid)", self.mn_pass)
        self._path_row(f, "Passphrase rules file (pass-rules / best64)", self.mn_rules)
        self._path_row(f, "Model constraints file (JSON/TXT)", self.mn_model)
        self._path_row(f, "DualTarget second address file", self.mn_dual)
        self.mn_change = ctk.CTkCheckBox(f, text="Include change chain /1/N (PathNova)")
        self.mn_change.select()
        self.mn_change.pack(anchor="w", pady=4)
        self.mn_bip86 = ctk.CTkCheckBox(f, text="Include BIP-86 Taproot paths")
        self.mn_bip86.select()
        self.mn_bip86.pack(anchor="w", pady=4)

        self.mn_eth = ctk.CTkCheckBox(f, text="ETH keccak checks (-W)  [live paths still coin-type 0' until PathNova lands]")
        self.mn_eth.pack(anchor="w", pady=8)

        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", pady=8)
        ctk.CTkButton(row, text="Apply → TrueCollider (mnemonic)", command=self._apply_mnemonic).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Preview & Launch", fg_color=self.theme["accent"], text_color="#111",
                      command=self._launch_mnemonic).pack(side="left", padx=4)

        self._section(f, "Included submodes (from ideas doc)")
        self._label(
            f,
            "Recovery: mask · model · lastword · prefix-word · typo · permute · anagram · positional-swap · language-guess · mixed-script\n"
            "Passphrase: pass-dict · pass-mask · pass-rules · pass-hybrid · pass-empty-plus\n"
            "Ecosystems: electrum-v1/v2 · slip39 · aezeed · bip85 · rfc1751 · solana-bip39 · milksad\n"
            "Strategies: checksum-first · entropy-guided · freq-prior · lattice · checkpointed · producer-split · WordOrbit · PhraseGravity · SeedCascadeVerify · DualTarget · ChecksumPrism",
            text_color=self.theme["muted"],
            justify="left",
        ).pack(anchor="w")

    def _apply_mnemonic(self) -> None:
        self._set_tc_mode("mnemonic")
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
            "Full BSGS controls live on the TrueCollider tab and appear automatically\n"
            "when you select bsgs / kangaroo / hybrid-dl / gaudry / xpoint.\n"
            "Puzzles → Target type “Known pubkey (BSGS)” also switches those settings.",
            text_color=self.theme["muted"],
        ).pack(anchor="w")

        tips = (
            "Live: sequential · backward · both · random · dance\n"
            "Research: grumpy · interleave · orbit · residue · dual-range · nested/fractal ·\n"
            "async-resolve · multi-target · negmap · handoff · gravity/chaos/sobol-giant ·\n"
            "freeze-table · compact-dp\n"
            "RAM guide: 8G→-k512 | 16G→-k1024 | 32G→-k2048 | Prefer kangaroo when N is huge.\n"
            f"Known-pubkey puzzles: {', '.join(str(n) for n in known_pubkey_puzzles())}\n"
        )
        self._label(f, tips, justify="left").pack(anchor="w", pady=8)
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkButton(row, text="Open TrueCollider BSGS settings", command=self._apply_bsgs).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Launch", fg_color=self.theme["accent"], text_color="#111",
                      command=self._launch_bsgs).pack(side="left", padx=4)

    def _apply_bsgs(self) -> None:
        self._set_tc_mode("bsgs")
        self.tabs.set("TrueCollider")
        self._set_status("BSGS settings shown on TrueCollider")

    def _launch_bsgs(self) -> None:
        self._apply_bsgs()
        self._launch_collider()

    # ── Address / RMD160 ────────────────────────────────────────────────
    def _build_address(self) -> None:
        tab = self.tabs.tab("Address / RMD160")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Address & hash160 — every expansion idea")
        g = ctk.CTkFrame(f, fg_color="transparent")
        g.pack(fill="x")
        self.addr_mode = self._dropdown(
            g, "Base mode",
            ["address", "rmd160", "xpoint", "pubkey2addr", "shadow160"],
            "address", 0, 0,
        )
        self.addr_sub = self._dropdown(g, "Address submode", ADDRESS_SUBMODES, "default", 0, 1)
        self.rmd_sub = self._dropdown(g, "RMD160 submode", RMD160_SUBMODES, "exact", 1, 0)
        self.addr_filter = self._dropdown(g, "Filter (FuseCascade / fuse16 / …)", FILTER_STRATS, "default fuse", 1, 1)
        self.addr_path = self._entry(g, "BIP-32 path (-p)", "m/84'/0'/0'/0", 2, 0)
        self.addr_depth = self._entry(g, "Depth (-D)", "10", 2, 1)
        self.shadow_bits = self._entry(g, "Shadow160 collision bits", "48", 3, 0)
        self.addr_stride = self._entry(g, "Stride (-I) / adaptive intent", "", 3, 1)

        self._label(
            f,
            "Address ideas: hilbert/sobol · density-map · multi-coin-fuse · hd-fanout · vanity-regex ·\n"
            "balance-prior · stream-targets · gpu-hash160-device · stride-adaptive · pair-compress · CascadeHunt\n"
            "RMD160 ideas: exact · prefix-N · shadow160 · funded-only · script-tags · rmd-of-xonly ·\n"
            "dual-bloom-device · cascade-filter · unsorted-ingest",
            text_color=self.theme["muted"],
            justify="left",
        ).pack(anchor="w", pady=8)
        ctk.CTkButton(f, text="Apply → TrueCollider", command=self._apply_address).pack(anchor="w", pady=4)

    def _apply_address(self) -> None:
        mode = self.addr_mode.get().split(" (")[0]
        token = mode if mode in MODES_LIVE else "rmd160"
        self._set_tc_mode(token)
        self.tabs.set("TrueCollider")

    # ── WeakRNG / CrystalPRNG ───────────────────────────────────────────
    def _build_weakrng(self) -> None:
        tab = self.tabs.tab("WeakRNG Lab")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "CrystalPRNG — weak entropy keyspaces")
        self._label(
            f,
            "Enumerate broken RNG spaces instead of pretending 256-bit is searchable.\n"
            "All submodes from the ideas doc are here.",
            text_color=self.theme["muted"],
        ).pack(anchor="w")
        g = ctk.CTkFrame(f, fg_color="transparent")
        g.pack(fill="x", pady=6)
        self.wr_sub = self._dropdown(g, "WeakRNG submode", WEAKRNG_SUBMODES, "milksad", 0, 0)
        self.wr_ts = self._entry(g, "Timestamp / window (-T or start:end)", "", 0, 1)
        for name, desc in [
            ("milksad", "Libbitcoin Explorer MT19937 — CVE-2023-39910 (~2^32 + time)"),
            ("randstorm", "BitcoinJS / browser weak entropy eras"),
            ("android-sr", "Android SecureRandom 2013 reduced entropy"),
            ("profanity", "32-bit seed ETH vanity generator"),
            ("timestamp-key", "Keys derived from unix time / counters"),
        ]:
            self._label(f, f"• {name}: {desc}", text_color=self.theme["muted"]).pack(anchor="w")
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", pady=10)
        ctk.CTkButton(row, text="Apply → TrueCollider (weakrng)", command=self._apply_weakrng).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Also set mnemonic milksad", command=self._apply_mn_milksad).pack(side="left", padx=4)

    def _apply_weakrng(self) -> None:
        self._set_tc_mode("weakrng")
        self.tabs.set("TrueCollider")
        self._set_status(f"WeakRNG {self.wr_sub.get()} applied")

    def _apply_mn_milksad(self) -> None:
        self._set_tc_mode("mnemonic")
        if hasattr(self, "mn_sub"):
            # find milksad in list
            for v in MNEMONIC_SUBMODES:
                if "milksad" in v:
                    self.mn_sub.set(v)
                    break
        self.tabs.set("Mnemonic Lab")
        self._set_status("Mnemonic Milk Sad / EntropyTimeline selected")

    # ── Directory (how to use everything) ───────────────────────────────
    def _build_directory(self) -> None:
        tab = self.tabs.tab("Directory")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Directory — how to use every mode, flag & setting")
        self._label(
            f,
            "Search literally everything: modes, -x patterns, -B strategies, CLI flags,\n"
            "TrueMkey options, GUI tabs, and the full ideas catalog (including Research 2026).\n"
            "LIVE = works now · GAP/NOVEL/RESEARCH = roadmap · ANTI = refused forever.",
            text_color=self.theme["muted"],
        ).pack(anchor="w")

        stats = ctk.CTkTextbox(f, height=70, font=ctk.CTkFont(family="Consolas", size=12))
        stats.pack(fill="x", pady=4)
        stats.insert("1.0", directory_stats())
        stats.configure(state="disabled")

        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", pady=6)
        self.dir_query = ctk.StringVar(value="")
        ctk.CTkEntry(
            row, textvariable=self.dir_query, width=420,
            placeholder_text="Search e.g. kangaroo, -H, pass-mask, hilbert, ANTI…",
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            row, text="Search", fg_color=self.theme["accent"], text_color="#111",
            command=self._directory_search,
        ).pack(side="left", padx=2)
        ctk.CTkButton(row, text="Show ALL", command=lambda: self._directory_search(show_all=True)).pack(side="left", padx=2)
        ctk.CTkButton(
            row, text="Copy results",
            command=lambda: self._copy_text(self.dir_results.get("1.0", "end")),
        ).pack(side="left", padx=2)

        cat = ctk.CTkFrame(f, fg_color="transparent")
        cat.pack(fill="x", pady=4)
        self._label(cat, "Quick jumps:", text_color=self.theme["muted"]).pack(side="left", padx=(0, 6))
        for label, q in (
            ("Modes", "Modes (-m)"),
            ("Flags", "CLI flags"),
            ("BSGS", "BSGS"),
            ("Mnemonic", "Mnemonic"),
            ("ANTI", "ANTI"),
            ("GPU", "GPU"),
            ("GUI", "GUI tabs"),
        ):
            ctk.CTkButton(
                cat, text=label, width=70,
                command=lambda qq=q: self._directory_jump(qq),
            ).pack(side="left", padx=2)

        self.dir_results = ctk.CTkTextbox(f, height=480, font=ctk.CTkFont(family="Consolas", size=12))
        self.dir_results.pack(fill="both", expand=True, pady=6)
        self.dir_results.insert(
            "1.0",
            "Click Show ALL or Search.\n\n"
            "Tip: type a flag like -m or -H, a mode like shadow160, or a lab name.\n",
        )

    def _directory_jump(self, query: str) -> None:
        self.dir_query.set(query)
        self._directory_search()

    def _directory_search(self, show_all: bool = False) -> None:
        q = "*" if show_all else (self.dir_query.get() if hasattr(self, "dir_query") else "")
        hits = search_directory(q)
        self.dir_results.delete("1.0", "end")
        if not hits:
            self.dir_results.insert("1.0", f"No matches for “{q}”. Try Show ALL or a shorter query.\n")
            return
        self.dir_results.insert("1.0", f"{len(hits)} match(es) for “{q or '*'}”\n{'=' * 60}\n\n")
        current_section = None
        for section, name, status, desc in hits:
            if section != current_section:
                current_section = section
                self.dir_results.insert("end", f"\n## {section}\n{'-' * 40}\n")
            self.dir_results.insert("end", format_entry(section, name, status, desc) + "\n")
        self.dir_results.see("1.0")
        self._set_status(f"Directory: {len(hits)} entries")

    # ── Idea Labs (one tab per idea group) ──────────────────────────────
    def _build_idea_labs(self) -> None:
        self._lab_widgets: dict[str, dict] = {}
        for spec in LAB_SPECS:
            self._build_one_idea_lab(spec)

    def _build_one_idea_lab(self, spec: dict) -> None:
        nav = spec["nav"]
        tab = self.tabs.tab(nav)
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, spec["title"])
        self._label(f, spec["blurb"], text_color=self.theme["muted"], justify="left").pack(anchor="w")

        items = spec["items"]
        labels = lab_labels(items)
        desc_map = {lab_labels([it])[0]: it[2] for it in items}

        g = ctk.CTkFrame(f, fg_color="transparent")
        g.pack(fill="x", pady=8)
        menu = self._dropdown(g, "Select idea / mode", labels, labels[0], 0, 0)
        widgets: dict = {"menu": menu, "spec": spec, "desc_map": desc_map}

        # Optional extra fields
        extras = set(spec.get("extra_fields") or [])
        row2 = ctk.CTkFrame(f, fg_color="transparent")
        row2.pack(fill="x", pady=4)
        r = 0
        if "handoff_bits" in extras:
            widgets["handoff"] = self._entry(row2, "Handoff bits (-H)", "44", r, 0)
            r = 0
        if "shadow_bits" in extras:
            widgets["shadow"] = self._entry(row2, "Shadow bits", "48", 0, 1 if "handoff" in widgets else 0)
        if "vanity" in extras:
            widgets["vanity"] = self._entry(row2, "Vanity prefix (-v)", "1Cool", 0, 0)
        if "words" in extras:
            widgets["words"] = self._entry(row2, "Word count (-w)", "12", 0, 1)
        if "gpu" in extras:
            widgets["gpu"] = self._dropdown(row2, "GPU (-U)", GPU, self.settings.get("default_gpu", "none"), 0, 0)
        if "memory" in extras:
            widgets["memory"] = self._entry(row2, "Memory (-M)", "auto", 0, 1)
        if "vector" in extras:
            widgets["vector"] = self._dropdown(row2, "Vector (-A)", VECTOR, "auto", 1, 0)
        if "threads" in extras:
            widgets["threads"] = self._entry(row2, "Threads (-t)", self.settings.get("default_threads", "8"), 1, 1)
        if "coin" in extras:
            widgets["coin"] = self._dropdown(row2, "Coin (-c)", COINS, "btc", 0, 0)
        if "k_factor" in extras:
            widgets["k_factor"] = self._entry(row2, "K factor (-k)", "auto", 0, 1)
        if "timestamp" in extras:
            widgets["timestamp"] = self._entry(row2, "Time window (-T start:end)", "", 0, 0)
        if "stride" in extras:
            widgets["stride"] = self._entry(row2, "Stride (-I)", "", 0, 1)
        if "depth" in extras:
            widgets["depth"] = self._entry(row2, "Index depth (-D)", "5", 0, 0)

        if "seed" in extras:
            widgets["seed"] = ctk.StringVar()
            self._label(f, "Known mnemonic / seed (--seed)", text_color=self.theme["muted"]).pack(anchor="w", pady=(6, 2))
            ctk.CTkEntry(f, textvariable=widgets["seed"]).pack(fill="x")
        if "pass_file" in extras:
            widgets["pass_file"] = ctk.StringVar()
            self._path_row(f, "Passphrase dictionary", widgets["pass_file"])
        if "pass_mask" in extras:
            widgets["pass_mask"] = ctk.StringVar()
            self._label(f, "Passphrase mask (?l?d…)", text_color=self.theme["muted"]).pack(anchor="w", pady=(6, 2))
            ctk.CTkEntry(f, textvariable=widgets["pass_mask"], placeholder_text="?l?l?l?d?d").pack(fill="x")
        if "pass_rules" in extras:
            widgets["pass_rules"] = ctk.StringVar()
            self._path_row(f, "Passphrase rules file", widgets["pass_rules"])
        if "density_map" in extras:
            widgets["density_map"] = ctk.StringVar()
            self._path_row(f, "Density map file (--density-map)", widgets["density_map"])
        if "funded" in extras:
            widgets["funded"] = ctk.StringVar()
            self._path_row(f, "Funded snapshot (--funded)", widgets["funded"])
        if "target" in extras:
            widgets["target"] = ctk.StringVar()
            self._path_row(f, "Target file (-f)", widgets["target"])
        if "change" in extras:
            widgets["change"] = ctk.CTkCheckBox(f, text="Include change /1/N")
            widgets["change"].select()
            widgets["change"].pack(anchor="w", pady=2)
        if "bip86" in extras:
            widgets["bip86"] = ctk.CTkCheckBox(f, text="Include BIP-86 Taproot")
            widgets["bip86"].select()
            widgets["bip86"].pack(anchor="w", pady=2)

        info = ctk.CTkTextbox(f, height=120)
        info.pack(fill="x", pady=8)
        info.insert("1.0", desc_map.get(labels[0], ""))
        widgets["info"] = info

        def on_pick(val: str, _w=widgets, _dm=desc_map) -> None:
            _w["info"].delete("1.0", "end")
            _w["info"].insert("1.0", _dm.get(val, ""))

        menu.configure(command=on_pick)

        # Catalog list
        self._section(f, f"All items in this lab ({len(items)})")
        listing = ctk.CTkTextbox(f, height=160, font=ctk.CTkFont(family="Consolas", size=12))
        listing.pack(fill="x", pady=4)
        for name, status, desc in items:
            listing.insert("end", f"[{status.upper():8}] {name:28}  {desc}\n")
        listing.configure(state="disabled")

        btn = ctk.CTkFrame(f, fg_color="transparent")
        btn.pack(fill="x", pady=10)
        ctk.CTkButton(
            btn, text="Apply → TrueCollider",
            command=lambda n=nav: self._apply_idea_lab(n),
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            btn, text="Apply + Launch", fg_color=self.theme["accent"], text_color="#111",
            command=lambda n=nav: self._launch_idea_lab(n),
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            btn, text="Open Directory help",
            command=lambda: self.tabs.set("Directory"),
        ).pack(side="left", padx=4)

        self._lab_widgets[nav] = widgets

    def _token(self, label: str) -> str:
        return (label or "").split(" (")[0].strip()

    def _apply_idea_lab(self, nav: str) -> None:
        w = self._lab_widgets.get(nav) or {}
        spec = w.get("spec") or {}
        kind = spec.get("kind", "")
        raw = w["menu"].get() if "menu" in w else ""
        token = self._token(raw)
        mode = spec.get("default_mode", "address")

        # Map selection → TrueCollider fields
        if kind == "mnemonic_sub":
            mode = "mnemonic"
            if hasattr(self, "mn_sub"):
                for v in MNEMONIC_SUBMODES:
                    if self._token(v) == token or token in v:
                        self.mn_sub.set(v)
                        break
            if w.get("seed") and w["seed"].get().strip() and hasattr(self, "mn_known"):
                self.mn_known.set(w["seed"].get().strip())
                if hasattr(self, "mn_mask"):
                    self.mn_mask.set(w["seed"].get().strip())
            if w.get("pass_file") and hasattr(self, "mn_pass"):
                self.mn_pass.set(w["pass_file"].get())
            if w.get("pass_mask") and hasattr(self, "mn_passmask"):
                self.mn_passmask.set(w["pass_mask"].get())
            if w.get("pass_rules") and hasattr(self, "mn_rules"):
                self.mn_rules.set(w["pass_rules"].get())

        elif kind == "path_pack":
            mode = "mnemonic"
            if hasattr(self, "mn_pack"):
                # map paths-btc → btc-std etc.
                pack_map = {
                    "paths-btc": "btc-std", "paths-eth": "eth", "paths-electrum": "electrum",
                    "paths-custom": "custom", "account-sweep": "account-sweep",
                    "change-chain-1": "btc-std", "bip86-taproot": "btc-std",
                }
                pack = pack_map.get(token, token)
                vals = list(getattr(self.mn_pack, "_values", []) or PATH_PACKS)
                for v in vals:
                    if self._token(v) == pack or pack in v:
                        self.mn_pack.set(v)
                        break
            if w.get("change") and hasattr(self, "mn_change"):
                (self.mn_change.select() if w["change"].get() else self.mn_change.deselect())
            if w.get("bip86") and hasattr(self, "mn_bip86"):
                (self.mn_bip86.select() if w["bip86"].get() else self.mn_bip86.deselect())
            if w.get("depth") and hasattr(self, "mn_depth"):
                self.mn_depth.set(w["depth"].get())

        elif kind == "kangaroo":
            if token in ("handoff", "compact-dp"):
                mode = "bsgs" if token != "kangaroo" else "kangaroo"
                if token == "handoff":
                    mode = "hybrid-dl"
                if hasattr(self, "bsgs_strat"):
                    for v in getattr(self.bsgs_strat, "_values", []) or []:
                        if self._token(v) == token or token in v:
                            self.bsgs_strat.set(v)
                            break
            elif token == "hybrid-dl":
                mode = "hybrid-dl"
            elif "SOTA" in token or "Multi-GPU" in token:
                mode = "kangaroo"
            else:
                mode = "kangaroo" if token == "kangaroo" else mode
            if w.get("handoff") and hasattr(self, "tc_handoff"):
                self.tc_handoff.set(w["handoff"].get())
            elif w.get("handoff") and hasattr(self, "bsgs_handoff"):
                try:
                    self.bsgs_handoff.set(w["handoff"].get())
                except Exception:
                    pass

        elif kind == "shadow160":
            mode = "shadow160" if token in ("shadow160",) or "shadow" in token else "rmd160"
            if hasattr(self, "tc_collision") or hasattr(self, "rmd_bits"):
                bits = w["shadow"].get() if w.get("shadow") else "48"
                if hasattr(self, "tc_collision"):
                    self.tc_collision.set(bits)

        elif kind == "pattern":
            if hasattr(self, "tc_pattern"):
                for v in getattr(self.tc_pattern, "_values", []) or SEARCH_PATTERNS:
                    if self._token(v) == token or token in v:
                        self.tc_pattern.set(v)
                        break
            if w.get("density_map") and w["density_map"].get().strip():
                # stash into funded/density if field exists on TC
                if hasattr(self, "tc_density"):
                    self.tc_density.set(w["density_map"].get())

        elif kind == "filter":
            if hasattr(self, "tc_filter"):
                for v in getattr(self.tc_filter, "_values", []) or FILTER_STRATS:
                    if self._token(v) == token or token.split()[0] in v:
                        self.tc_filter.set(v)
                        break

        elif kind == "vanity":
            mode = token if token in ("vanity", "poetry", "brainwallet", "minikeys") else "vanity"
            if w.get("vanity") and hasattr(self, "tc_vanity"):
                self.tc_vanity.set(w["vanity"].get())
            if w.get("words") and hasattr(self, "tc_words"):
                self.tc_words.set(w["words"].get())

        elif kind == "algorithm":
            algo_map = {
                "OrbitBSGS": ("bsgs", "orbit"),
                "HerdHandoff": ("hybrid-dl", "handoff"),
                "GrumpyBSGS": ("bsgs", "grumpy"),
                "InterleaveBSGS": ("bsgs", "interleave"),
                "GaudrySchost / MultiDim-DL": ("gaudry", None),
                "ResidueHerd": ("gaudry", "residue"),
                "FuseCascade": ("address", None),
                "HilbertStride": ("address", None),
                "SobolWalk": ("address", None),
                "HaltonWalk": ("address", None),
                "Shadow160": ("shadow160", None),
                "CrystalPRNG": ("weakrng", None),
                "MnemonicLattice": ("mnemonic", None),
                "ChecksumPrism": ("mnemonic", None),
                "PathNova": ("mnemonic", None),
            }
            mode, bstrat = algo_map.get(token, ("bsgs", None))
            if "Hilbert" in token or "Sobol" in token or "Halton" in token:
                pat = "hilbert" if "Hilbert" in token else ("sobol" if "Sobol" in token else "halton")
                if hasattr(self, "tc_pattern"):
                    for v in getattr(self.tc_pattern, "_values", []) or []:
                        if pat in v.lower():
                            self.tc_pattern.set(v)
                            break
            if "FuseCascade" in token and hasattr(self, "tc_filter"):
                for v in getattr(self.tc_filter, "_values", []) or []:
                    if "cascade" in v.lower():
                        self.tc_filter.set(v)
                        break
            if bstrat and hasattr(self, "bsgs_strat"):
                for v in getattr(self.bsgs_strat, "_values", []) or []:
                    if self._token(v) == bstrat:
                        self.bsgs_strat.set(v)
                        break
            if token == "MnemonicLattice" and hasattr(self, "mn_sub"):
                for v in MNEMONIC_SUBMODES:
                    if "lattice" in v:
                        self.mn_sub.set(v)
                        break

        elif kind == "gpu":
            if w.get("gpu") and hasattr(self, "tc_gpu"):
                self.tc_gpu.set(w["gpu"].get())
            if w.get("memory") and hasattr(self, "tc_mem"):
                self.tc_mem.set(w["memory"].get())
            if w.get("vector") and hasattr(self, "tc_vector"):
                self.tc_vector.set(w["vector"].get())
            if w.get("threads") and hasattr(self, "tc_threads"):
                self.tc_threads.set(w["threads"].get())

        elif kind == "coin":
            if token in COINS and hasattr(self, "tc_coin"):
                self.tc_coin.set(token)
            elif w.get("coin") and hasattr(self, "tc_coin"):
                self.tc_coin.set(w["coin"].get())

        elif kind == "bsgs_strat":
            mode = "bsgs"
            if token == "handoff":
                mode = "hybrid-dl"
            if hasattr(self, "bsgs_strat"):
                for v in getattr(self.bsgs_strat, "_values", []) or BSGS_STRATEGIES:
                    if self._token(v) == token:
                        self.bsgs_strat.set(v)
                        break
            if w.get("k_factor") and hasattr(self, "bsgs_k"):
                self.bsgs_k.set(w["k_factor"].get())

        elif kind == "address_sub":
            mode = "address"
            if token in ("hilbert", "sobol", "density-map") and hasattr(self, "tc_pattern"):
                for v in getattr(self.tc_pattern, "_values", []) or []:
                    if token in v.lower():
                        self.tc_pattern.set(v)
                        break
            if w.get("stride") and hasattr(self, "tc_stride"):
                self.tc_stride.set(w["stride"].get())

        elif kind == "weakrng":
            mode = "weakrng"
            if hasattr(self, "wr_sub"):
                for v in getattr(self.wr_sub, "_values", []) or WEAKRNG_SUBMODES:
                    if self._token(v) == token or token in v:
                        self.wr_sub.set(v)
                        break
            if w.get("timestamp") and w["timestamp"].get().strip() and hasattr(self, "tc_time"):
                self.tc_time.set(w["timestamp"].get().strip())

        elif kind == "research":
            # Best-effort map research names to live modes
            low = token.lower()
            if "kangaroo" in low or "dp " in low:
                mode = "kangaroo"
            elif "bsgs" in low or "orbit" in low or "grumpy" in low:
                mode = "bsgs"
            elif "mnemonic" in low or "pbkdf" in low or "passphrase" in low or "bip39" in low:
                mode = "mnemonic"
            elif "shadow" in low or "hash160" in low:
                mode = "shadow160"
            elif "weak" in low or "milk" in low or "profanity" in low:
                mode = "weakrng"
            else:
                mode = "address"

        if w.get("target") and w["target"].get().strip() and hasattr(self, "tc_target"):
            self.tc_target.set(w["target"].get().strip())
        if w.get("funded") and w["funded"].get().strip() and hasattr(self, "tc_funded"):
            self.tc_funded.set(w["funded"].get().strip())

        self._set_tc_mode(mode)
        self.tabs.set("TrueCollider")
        self._set_status(f"{nav}: applied “{token}” → mode {mode}")

    def _launch_idea_lab(self, nav: str) -> None:
        self._apply_idea_lab(nav)
        self._launch_collider()

    # ── TrueMkey ────────────────────────────────────────────────────────
    def _build_mkey(self) -> None:
        tab = self.tabs.tab("TrueMkey")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "TrueMkeyCollider — AES mkey/ckey")
        self._label(
            f,
            "Same CPU / GPU box as TrueCollider. CUDA search for AES trials; CPU for --try / host helpers.\n"
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
        mk_gpu_default = self.settings.get("default_gpu", "cuda")
        if mk_gpu_default not in GPU:
            mk_gpu_default = "cuda"
        self.mk_gpu = self._dropdown(
            g, "GPU (-U) — none=CPU / cuda / opencl / both (same as TrueCollider)", GPU, mk_gpu_default, 0, 0
        )
        self.mk_gpu.configure(command=self._on_mk_gpu)
        self.mk_mode = self._dropdown(g, "Walk", ["random", "sequential", "mixed"], "random", 0, 1)

        self.mk_gpu_opts = ctk.CTkFrame(f, fg_color="transparent")
        self.mk_gpu_opts.pack(fill="x", pady=4)
        self.mk_grid = self._entry(self.mk_gpu_opts, "Grid -g", "256,256", 0, 0)
        self.mk_streams = self._entry(self.mk_gpu_opts, "Streams", "4", 0, 1)
        self.mk_mem = self._entry(self.mk_gpu_opts, "Memory -M", "auto", 1, 0)
        self.mk_dev = self._entry(self.mk_gpu_opts, "Device -d", "0", 1, 1)

        self.mk_more = ctk.CTkFrame(f, fg_color="transparent")
        self.mk_more.pack(fill="x")
        self.mk_partial = self._entry(self.mk_more, "Partial prefix", "", 0, 0)
        self.mk_try = self._entry(self.mk_more, "--try HEX (CPU/host verify)", "", 0, 1)
        self.mk_limit = self._entry(self.mk_more, "Limit -n", "", 1, 0)

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
        self._mk_gpu_visible = True
        self._sync_mk_gpu_panel()

    def _mk_use_gpu(self) -> bool:
        g = (self.mk_gpu.get() if hasattr(self, "mk_gpu") else "cuda") or "cuda"
        return g.strip().lower() not in ("none", "cpu", "")

    def _on_mk_gpu(self, _value: str | None = None) -> None:
        self._sync_mk_gpu_panel()
        if hasattr(self, "tc_gpu") and hasattr(self, "mk_gpu"):
            try:
                self.tc_gpu.set(self.mk_gpu.get())
            except Exception:
                pass
        if hasattr(self, "set_gpu") and hasattr(self, "mk_gpu"):
            try:
                self.set_gpu.set(self.mk_gpu.get())
            except Exception:
                pass
        g = (self.mk_gpu.get() if hasattr(self, "mk_gpu") else "cuda") or "cuda"
        g = g.strip().lower()
        if g in ("none", "cpu", ""):
            kind = "CPU / host"
        elif g == "both":
            kind = "CPU + GPU"
        else:
            kind = f"GPU ({g})"
        self._set_status(f"TrueMkey compute: {kind}")

    def _sync_mk_gpu_panel(self) -> None:
        if not hasattr(self, "mk_gpu_opts") or not hasattr(self, "mk_more"):
            return
        show = self._mk_use_gpu()
        if show and not getattr(self, "_mk_gpu_visible", False):
            self.mk_gpu_opts.pack(fill="x", pady=4, before=self.mk_more)
            self._mk_gpu_visible = True
        elif not show and getattr(self, "_mk_gpu_visible", True):
            self.mk_gpu_opts.pack_forget()
            self._mk_gpu_visible = False

    def _preview_mkey(self) -> None:
        cfg = MkeyConfig(
            exe=self.mk_exe.get().strip() or "TrueMkeyCollider.exe",
            ckeys=self.mk_ckeys.get().strip(),
            mkeys=self.mk_mkeys.get().strip(),
            pubkeys=self.mk_pubs.get().strip(),
            mode=self.mk_mode.get(),
            gpu=self.mk_gpu.get() if hasattr(self, "mk_gpu") else "cuda",
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
        if not self._mk_use_gpu() and not self.mk_try.get().strip() and not self.mk_selftest.get():
            if not messagebox.askokcancel(
                "TrueMkey — CPU selected",
                "Compute is set to none (CPU only).\n\n"
                "AES key search still needs CUDA in TrueMkeyCollider.\n"
                "Use --try HEX for host verify, or switch to cuda / both.\n\n"
                "Launch anyway?",
            ):
                return
        self.settings["truemkey_exe"] = self.mk_exe.get().strip()
        if hasattr(self, "mk_gpu"):
            self.settings["default_gpu"] = self.mk_gpu.get()
        cwd = str(Path(self.mk_exe.get()).parent) if self.mk_exe.get() else None
        self.runner.start(cmd, cwd=cwd)

    # ── Wallet Lab (wallet.dat forensics → TrueMkey) ───────────────────
    def _build_wallet_lab(self) -> None:
        tab = self.tabs.tab("Wallet Lab")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "wallet.dat forensic inspector")
        self._label(
            f,
            "Breaks Bitcoin Core wallet.dat into mkey / ckey / pubkey pieces for TrueMkeyCollider.\n"
            "Does NOT crack passwords. Copy blobs or click Send → TrueMkey to prefill paths.",
            text_color=self.theme["muted"],
        ).pack(anchor="w")
        self.wl_path = ctk.StringVar()
        self._path_row(f, "wallet.dat", self.wl_path)
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", pady=6)
        ctk.CTkButton(row, text="Inspect", command=self._wallet_inspect).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Export files", command=self._wallet_export).pack(side="left", padx=4)
        ctk.CTkButton(
            row, text="Send → TrueMkey", fg_color=self.theme["accent"], text_color="#111",
            command=self._wallet_send_mkey,
        ).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Copy report", command=lambda: self._copy_text(self.wl_report.get("1.0", "end"))).pack(side="left", padx=4)
        self.wl_report = ctk.CTkTextbox(f, height=420, font=ctk.CTkFont(family="Consolas", size=12))
        self.wl_report.pack(fill="both", expand=True, pady=8)
        self._wallet_last = None
        self._wallet_export_paths = {}

    def _wallet_inspect(self) -> None:
        p = self.wl_path.get().strip()
        if not p:
            messagebox.showwarning("Wallet Lab", "Select a wallet.dat file first.")
            return
        try:
            rep = inspect_wallet_dat(p)
            self._wallet_last = rep
            self.wl_report.delete("1.0", "end")
            self.wl_report.insert("1.0", rep.summary_text())
            self._set_status(f"Wallet inspected: {len(rep.mkeys)} mkey, {len(rep.ckeys)} ckey, {len(rep.pubkeys)} pubs")
        except Exception as e:
            messagebox.showerror("Wallet Lab", str(e))

    def _wallet_export(self) -> None:
        if not self._wallet_last:
            self._wallet_inspect()
        if not self._wallet_last:
            return
        out = Path(self.settings.get("workdir") or ".") / "wallet_extract"
        try:
            paths = export_for_truemkey(self._wallet_last, out)
            self._wallet_export_paths = paths
            self.wl_report.insert("end", f"\n\nExported:\n" + "\n".join(f"  {k}: {v}" for k, v in paths.items()))
            self._set_status(f"Exported wallet blobs → {out}")
        except Exception as e:
            messagebox.showerror("Wallet Lab", str(e))

    def _wallet_send_mkey(self) -> None:
        self._wallet_export()
        paths = self._wallet_export_paths or {}
        if not paths:
            return
        if hasattr(self, "mk_mkeys") and paths.get("mkeys"):
            self.mk_mkeys.set(paths["mkeys"])
        if hasattr(self, "mk_ckeys") and paths.get("ckeys"):
            self.mk_ckeys.set(paths["ckeys"])
        if hasattr(self, "mk_pubs") and paths.get("pubkeys"):
            self.mk_pubs.set(paths["pubkeys"])
        self.tabs.set("TrueMkey")
        if hasattr(self, "_preview_mkey"):
            self._preview_mkey()
        self._set_status("Prefilled TrueMkey from wallet.dat extract — review and Launch")
        messagebox.showinfo(
            "Sent to TrueMkey",
            "mkey / ckey / pubkey files prefilling TrueMkey tab.\n"
            "Open TrueMkey, review Preview, then Launch.",
        )

    # ── Collider Lab (pp717 Collider.exe + TrueCollider bridge) ─────────
    def _build_collider_lab(self) -> None:
        tab = self.tabs.tab("Collider Lab")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Collider-bsgs Lab — native Collider.exe + TrueCollider bridge")
        self._label(
            f,
            "Bundled from github.com/pp717/Collider-bsgs. Run the original CUDA Collider,\n"
            "or map --pb/--pk/--pke/--infile into TrueCollider BSGS (same puzzles).",
            text_color=self.theme["muted"],
        ).pack(anchor="w")
        tools = Path(__file__).resolve().parents[1] / "tools" / "Collider-bsgs"
        default_exe = str(tools / "Collider.exe") if (tools / "Collider.exe").is_file() else ""
        self.col_exe = ctk.StringVar(value=default_exe)
        self._path_row(f, "Collider.exe", self.col_exe, exe=True)
        g = ctk.CTkFrame(f, fg_color="transparent")
        g.pack(fill="x")
        self.col_pb = self._entry(g, "Pubkey -pb / --pb", "", 0, 0)
        self.col_pk = self._entry(g, "Range start -pk", "", 0, 1)
        self.col_pke = self._entry(g, "Range end -pke", "", 1, 0)
        self.col_infile = self._entry(g, "Infile", "", 1, 1)
        self.col_w = self._entry(g, "Baby -w / --baby-bits", "22", 2, 0)
        self.col_htsz = self._entry(g, "HashTable -htsz", "26", 2, 1)
        self.col_dev = self._entry(g, "GPU -d", "0", 3, 0)
        self.col_engine = self._dropdown(
            g, "Engine",
            ["Collider.exe (original)", "TrueCollider bridge (keyhunt)"],
            "TrueCollider bridge (keyhunt)", 3, 1,
        )
        self.col_mode = self._dropdown(
            g, "Search mode",
            ["random", "sequential", "rseq (random→sequential chunk)"],
            "random", 4, 0,
        )
        self.col_walk = self._dropdown(
            g, "Rseq walk chunk (--walk)",
            ["1M (default)", "2M", "10M", "100M", "1B", "1T", "custom…"],
            "1M (default)", 4, 1,
        )
        self.col_walk_custom = self._entry(g, "Custom walk (keys)", "5000000", 5, 0)
        self.col_rbits = self._entry(g, "Collider.exe -r bits (random)", "120", 5, 1)
        self._label(
            f,
            "Modes: random = jump starts · sequential = linear giants · "
            "rseq = random key then walk chunk (1M/1B/1T) then reseed.",
            text_color=self.theme["muted"],
        ).pack(anchor="w", pady=(2, 0))
        self.col_preview = ctk.CTkTextbox(f, height=100, font=ctk.CTkFont(family="Consolas", size=13))
        self.col_preview.pack(fill="x", pady=6)
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkButton(row, text="Preview", command=self._collider_preview).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Launch", fg_color=self.theme["accent"], text_color="#111",
                      command=self._collider_launch).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Copy", command=lambda: self._copy_text(self.col_preview.get("1.0", "end"))).pack(side="left", padx=4)

    def _collider_walk_token(self) -> str:
        w = self.col_walk.get() if hasattr(self, "col_walk") else "1M (default)"
        if "custom" in w.lower():
            return (self.col_walk_custom.get().strip() if hasattr(self, "col_walk_custom") else "") or "5000000"
        # "1M (default)" → 1M, "1B" → 1B
        return w.split()[0] if w else "1M"

    def _collider_preview(self) -> None:
        eng = self.col_engine.get() if hasattr(self, "col_engine") else ""
        pb = self.col_pb.get().strip()
        pk = self.col_pk.get().strip()
        pke = self.col_pke.get().strip()
        infile = self.col_infile.get().strip()
        w = self.col_w.get().strip() or "22"
        htsz = self.col_htsz.get().strip() or "26"
        dev = self.col_dev.get().strip() or "0"
        mode_raw = self.col_mode.get() if hasattr(self, "col_mode") else "random"
        if mode_raw.startswith("rseq"):
            mode = "rseq"
        elif mode_raw.startswith("sequential"):
            mode = "sequential"
        else:
            mode = "random"
        walk = self._collider_walk_token()
        if "TrueCollider" in eng:
            exe = self.settings.get("truecollider_cuda") or self.settings.get("truecollider_exe") or "keyhunt_cuda.exe"
            parts = [f'"{exe}"', "-m", "bsgs", "-U", "cuda", "--mode", mode]
            if mode == "rseq":
                parts += ["--walk", walk]
            if pb:
                parts += ["--pb", pb]
            if infile:
                parts += ["--infile", f'"{infile}"']
            if pk:
                parts += ["--pk", pk]
            if pke:
                parts += ["--pke", pke]
            parts += ["--baby-bits", w, "--htsz", htsz, "-t", "4"]
            cmd = " ".join(parts)
        else:
            exe = self.col_exe.get().strip() or "Collider.exe"
            parts = [f'"{exe}"', "-d", dev, "-w", w, "-htsz", htsz]
            if pb:
                parts += ["-pb", pb]
            if infile:
                parts += ["-infile", f'"{infile}"']
            if pk:
                parts += ["-pk", pk]
            if pke:
                parts += ["-pke", pke]
            # Original Collider: -r BITS = random bit-space test (no native rseq)
            if mode == "random":
                rbits = self.col_rbits.get().strip() if hasattr(self, "col_rbits") else "120"
                if rbits:
                    parts += ["-r", rbits]
            cmd = " ".join(parts)
        self.col_preview.delete("1.0", "end")
        self.col_preview.insert("1.0", cmd)

    def _collider_launch(self) -> None:
        self._collider_preview()
        cmd = self.col_preview.get("1.0", "end").strip()
        eng = self.col_engine.get() if hasattr(self, "col_engine") else ""
        if "TrueCollider" in eng:
            exe = self.settings.get("truecollider_cuda") or self.settings.get("truecollider_exe") or ""
            cwd = str(Path(exe).parent) if exe else None
        else:
            cwd = str(Path(self.col_exe.get()).parent) if self.col_exe.get() else None
        self.runner.start(cmd, cwd=cwd)
        self._set_status("Collider Lab launched")

    # ── Ops Lab (job queue + competitor CLI translator) ─────────────────
    def _build_ops_lab(self) -> None:
        tab = self.tabs.tab("Ops Lab")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Ops Lab — job queue / farm + CLI translator")
        self._label(
            f,
            "Queue dry-run then launch. Translate RCKangaroo / Collider / BitCrack flags → TrueCollider.",
            text_color=self.theme["muted"],
        ).pack(anchor="w")
        g = ctk.CTkFrame(f, fg_color="transparent")
        g.pack(fill="x")
        self.ops_queue = ctk.CTkTextbox(g, height=140, font=ctk.CTkFont(family="Consolas", size=12))
        self.ops_queue.pack(fill="x", pady=4)
        self.ops_queue.insert("1.0", "# one command per line; Preview queues with -y dry-run first\n")
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkButton(row, text="Dry-run all", command=self._ops_dryrun_all).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Launch next", fg_color=self.theme["accent"], text_color="#111",
                      command=self._ops_launch_next).pack(side="left", padx=4)
        self._section(f, "Competitor CLI → TrueCollider recipe")
        self.ops_foreign = self._entry(f, "Paste foreign CLI", "", 0, 0) if False else None
        self.ops_foreign_box = ctk.CTkTextbox(f, height=80, font=ctk.CTkFont(family="Consolas", size=12))
        self.ops_foreign_box.pack(fill="x", pady=4)
        self.ops_translated = ctk.CTkTextbox(f, height=80, font=ctk.CTkFont(family="Consolas", size=12))
        self.ops_translated.pack(fill="x", pady=4)
        ctk.CTkButton(f, text="Translate", command=self._ops_translate).pack(anchor="w", pady=4)

    def _ops_dryrun_all(self) -> None:
        lines = [ln.strip() for ln in self.ops_queue.get("1.0", "end").splitlines()
                 if ln.strip() and not ln.strip().startswith("#")]
        for ln in lines:
            cmd = ln if " -y" in f" {ln} " or ln.endswith(" -y") else f"{ln} -y"
            self.runner.start(cmd)
            self._set_status(f"Ops dry-run: {cmd[:80]}")
            break  # one at a time in console
        if not lines:
            messagebox.showinfo("Ops Lab", "Queue is empty.")

    def _ops_launch_next(self) -> None:
        lines = [ln.strip() for ln in self.ops_queue.get("1.0", "end").splitlines()
                 if ln.strip() and not ln.strip().startswith("#")]
        if not lines:
            messagebox.showinfo("Ops Lab", "Queue is empty.")
            return
        cmd = lines[0]
        # rewrite queue without first line
        rest = "\n".join(lines[1:])
        self.ops_queue.delete("1.0", "end")
        self.ops_queue.insert("1.0", rest + ("\n" if rest else ""))
        self.runner.start(cmd)
        self._set_status("Ops launched next job")

    def _ops_translate(self) -> None:
        raw = self.ops_foreign_box.get("1.0", "end").strip()
        parts = raw.replace("=", " ").split()
        out = ['"keyhunt_cuda.exe"', "-m", "bsgs", "-U", "cuda", "-B", "random"]
        i = 0
        while i < len(parts):
            a = parts[i]
            def nxt() -> str:
                nonlocal i
                i += 1
                return parts[i] if i < len(parts) else ""
            if a in ("-pb", "--pb") and i + 1 < len(parts):
                out += ["--pb", nxt()]; i += 1; continue
            if a in ("-pk", "--pk") and i + 1 < len(parts):
                out += ["--pk", nxt()]; i += 1; continue
            if a in ("-pke", "--pke") and i + 1 < len(parts):
                out += ["--pke", nxt()]; i += 1; continue
            if a in ("-infile", "--infile", "-f") and i + 1 < len(parts):
                out += ["--infile", nxt()]; i += 1; continue
            if a in ("-w",) and i + 1 < len(parts):
                out += ["--baby-bits", nxt()]; i += 1; continue
            if a in ("-htsz", "--htsz") and i + 1 < len(parts):
                out += ["--htsz", nxt()]; i += 1; continue
            if a in ("-r",) and i + 1 < len(parts):
                # Collider random bits OR keyhunt range — if looks like bits, map mode random
                v = nxt(); i += 1
                if v.isdigit() and int(v) < 256:
                    out += ["--mode", "random"]
                else:
                    out += ["-r", v]
                continue
            if a in ("-d",) and i + 1 < len(parts):
                nxt(); i += 1
                continue
            if a.lower() in ("rckangaroo", "kangaroo.exe", "bitcrack"):
                out[out.index("-m") + 1] = "kangaroo"
                i += 1
                continue
            i += 1
        cmd = " ".join(out)
        self.ops_translated.delete("1.0", "end")
        self.ops_translated.insert("1.0", cmd)

    # ── Tools Arsenal (100+ registry) ───────────────────────────────────
    def _build_tools_arsenal(self) -> None:
        tab = self.tabs.tab("Tools Arsenal")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Tools Arsenal — every integrated capability")
        self._label(f, tools_stats(), text_color=self.theme["muted"]).pack(anchor="w")
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", pady=4)
        self.tools_q = ctk.StringVar()
        ctk.CTkEntry(row, textvariable=self.tools_q, placeholder_text="search tools…", width=280).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Search", command=self._tools_refresh).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Show all", command=lambda: (self.tools_q.set(""), self._tools_refresh())).pack(side="left", padx=4)
        self.tools_list = ctk.CTkTextbox(f, height=480, font=ctk.CTkFont(family="Consolas", size=12))
        self.tools_list.pack(fill="both", expand=True, pady=8)
        self._tools_refresh()

    def _tools_refresh(self) -> None:
        hits = search_tools(self.tools_q.get() if hasattr(self, "tools_q") else "")
        lines = [f"{len(hits)} tools\n"]
        for t in hits:
            gpu = " GPU" if t.get("gpu") else ""
            lines.append(
                f"[{t.get('status','?'):7}]{gpu:4}  {t.get('name','')}  |  {t.get('kind','')}  |  {t.get('cli','')}"
            )
        self.tools_list.delete("1.0", "end")
        self.tools_list.insert("1.0", "\n".join(lines))

    # ── Chain RPCs (chainid.network implant) ────────────────────────────
    def _build_chain_rpcs(self) -> None:
        tab = self.tabs.tab("Chain RPCs")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Public chain RPC catalog (chainid.network)")
        self._label(
            f,
            "Implanted from your chain-dev-download-rpc.py — downloads public HTTP RPCs\n"
            f"into {default_chains_dir()}. Use with -N node checks / multi-coin research.",
            text_color=self.theme["muted"],
        ).pack(anchor="w")
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", pady=6)
        ctk.CTkButton(row, text="Sync RPCs now", fg_color=self.theme["accent"], text_color="#111",
                      command=self._chain_rpc_sync).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Refresh main coins", command=self._chain_rpc_show).pack(side="left", padx=4)
        self.rpc_view = ctk.CTkTextbox(f, height=420, font=ctk.CTkFont(family="Consolas", size=12))
        self.rpc_view.pack(fill="both", expand=True, pady=8)
        self._chain_rpc_show()

    def _chain_rpc_sync(self) -> None:
        try:
            msg = sync_chain_rpcs()
            self.rpc_view.delete("1.0", "end")
            self.rpc_view.insert("1.0", msg + "\n\n")
            self._chain_rpc_show(append=True)
            self._set_status(msg)
        except Exception as e:
            messagebox.showerror("Chain RPCs", f"Sync failed:\n{e}")

    def _chain_rpc_show(self, append: bool = False) -> None:
        mains = list_main_rpcs()
        lines = ["Main coins (from last sync):\n"]
        if not mains:
            lines.append("(no index yet — click Sync RPCs now)\n")
        for row in mains:
            lines.append(
                f"  chainId={row.get('chainId')}  {row.get('name')}  "
                f"rpcs={row.get('rpc_count')}  file={row.get('file')}"
            )
        text = "\n".join(lines)
        if append:
            self.rpc_view.insert("end", text)
        else:
            self.rpc_view.delete("1.0", "end")
            self.rpc_view.insert("1.0", text)

    # ── Address Watch (lawful alert-only) ───────────────────────────────
    def _build_watch(self) -> None:
        tab = self.tabs.tab("Address Watch")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._watch_book = WatchBook()
        self._watch_job = None
        self._watch_running = False

        self._section(f, "Address Watch — alert only")
        self._label(
            f,
            "Monitor addresses YOU enter. Balance + last-tx alerts only.\n"
            "NO auto-withdraw · NO RBF race · NO key scraping.\n"
            "Lawful substitute for refused scraper / mempool-hijack ideas.",
            text_color=self.theme["danger"],
        ).pack(anchor="w", pady=(0, 8))

        self._label(f, "Addresses (one per line: address  or  address | label)").pack(anchor="w")
        self.watch_addrs = ctk.CTkTextbox(f, height=140, font=ctk.CTkFont(family="Consolas", size=13))
        self.watch_addrs.pack(fill="x", pady=4)
        self.watch_addrs.insert(
            "1.0",
            "# Example — replace with your own addresses\n"
            "# bc1q… | cold-storage\n",
        )

        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", pady=6)
        self._label(row, "Poll every").pack(side="left", padx=(0, 6))
        self.watch_interval = ctk.CTkOptionMenu(
            row, values=["15", "30", "60", "120", "300"], width=90,
        )
        self.watch_interval.set("60")
        self.watch_interval.pack(side="left", padx=4)
        self._label(row, "sec").pack(side="left", padx=(0, 12))
        self._label(row, "Explorer").pack(side="left", padx=(0, 6))
        self.watch_explorer = ctk.CTkOptionMenu(
            row, values=["mempool", "blockstream"], width=130,
        )
        self.watch_explorer.set("mempool")
        self.watch_explorer.pack(side="left", padx=4)
        self.watch_changes_only = ctk.CTkCheckBox(row, text="Changes only after first poll")
        self.watch_changes_only.select()
        self.watch_changes_only.pack(side="left", padx=12)

        btn = ctk.CTkFrame(f, fg_color="transparent")
        btn.pack(fill="x", pady=8)
        ctk.CTkButton(
            btn, text="Poll once", fg_color=self.theme["accent"], text_color="#111",
            command=self._watch_poll_once,
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            btn, text="Start watching", command=self._watch_start,
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            btn, text="Stop", fg_color=self.theme.get("danger", "#a33"),
            command=self._watch_stop,
        ).pack(side="left", padx=4)
        ctk.CTkButton(
            btn, text="Open Telegram", command=self._open_telegram,
        ).pack(side="left", padx=4)

        self._section(f, "Last results")
        self.watch_log = ctk.CTkTextbox(f, height=220, font=ctk.CTkFont(family="Consolas", size=12))
        self.watch_log.pack(fill="both", expand=True, pady=4)
        self.watch_status = ctk.CTkLabel(f, text="Idle — alert only", text_color=self.theme["muted"])
        self.watch_status.pack(anchor="w", pady=4)

    def _watch_append(self, msg: str) -> None:
        line = msg.rstrip() + "\n"
        if hasattr(self, "watch_log"):
            self.watch_log.insert("end", line)
            self.watch_log.see("end")
        self._append_console(line)
        if "CHANGE" in msg or "NEW" in msg:
            self._set_status(msg[:120])

    def _watch_poll_once(self) -> None:
        text = self.watch_addrs.get("1.0", "end") if hasattr(self, "watch_addrs") else ""
        addrs = parse_watch_lines(text)
        if not addrs:
            messagebox.showwarning("Address Watch", "Add at least one address to watch.")
            return
        prefer = self.watch_explorer.get() if hasattr(self, "watch_explorer") else "mempool"
        changes_only = bool(self.watch_changes_only.get()) if hasattr(self, "watch_changes_only") else False
        # First poll always shows everything so user sees baseline
        if not self._watch_book.entries:
            changes_only = False
        self.watch_status.configure(text=f"Polling {len(addrs)} address(es)…")
        self.update_idletasks()

        def run() -> None:
            try:
                msgs = poll_once(
                    text,
                    self._watch_book,
                    prefer=prefer,
                    changes_only=changes_only,
                )
                self.after(0, lambda: self._watch_finish_poll(msgs, len(addrs)))
            except Exception as e:
                self.after(0, lambda: self._watch_finish_poll([f"[WATCH ERR] {e}"], 0))

        import threading
        threading.Thread(target=run, daemon=True).start()

    def _watch_finish_poll(self, msgs: list[str], n: int) -> None:
        for m in msgs:
            self._watch_append(m)
        if not msgs:
            self._watch_append("[WATCH] No changes.")
        self.watch_status.configure(
            text=f"Last poll: {n} addr · tracked={len(self._watch_book.entries)} · alert-only"
        )

    def _watch_start(self) -> None:
        if self._watch_running:
            return
        text = self.watch_addrs.get("1.0", "end") if hasattr(self, "watch_addrs") else ""
        if not parse_watch_lines(text):
            messagebox.showwarning("Address Watch", "Add at least one address to watch.")
            return
        self._watch_running = True
        self.watch_status.configure(text="Watching… (alert only — no auto-spend)")
        self._watch_append("[WATCH] Started — alert only, no withdraw, no RBF.")
        self._watch_poll_once()
        self._watch_schedule_next()

    def _watch_schedule_next(self) -> None:
        if not self._watch_running:
            return
        try:
            sec = int(self.watch_interval.get())
        except Exception:
            sec = 60
        sec = max(15, sec)
        self._watch_job = self.after(sec * 1000, self._watch_tick)

    def _watch_tick(self) -> None:
        if not self._watch_running:
            return
        self._watch_poll_once()
        self._watch_schedule_next()

    def _watch_stop(self) -> None:
        self._watch_running = False
        if self._watch_job is not None:
            try:
                self.after_cancel(self._watch_job)
            except Exception:
                pass
            self._watch_job = None
        if hasattr(self, "watch_status"):
            self.watch_status.configure(text="Stopped — alert only")
        self._watch_append("[WATCH] Stopped.")

    # ── Ideas Matrix ────────────────────────────────────────────────────
    def _build_ideas(self) -> None:
        tab = self.tabs.tab("Ideas Matrix")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "EVERY idea — original README + Research 2026 wave")
        rep = ctk.CTkTextbox(f, height=90, font=ctk.CTkFont(family="Consolas", size=12))
        rep.pack(fill="x", pady=4)
        rep.insert("1.0", completeness_report())
        rep.configure(state="disabled")
        self._label(
            f,
            "Catalog is large — click Load to populate (keeps the app snappy).",
            text_color=self.theme["muted"],
        ).pack(anchor="w")

        filter_row = ctk.CTkFrame(f, fg_color="transparent")
        filter_row.pack(fill="x", pady=4)
        self.ideas_filter = ctk.CTkOptionMenu(
            filter_row,
            values=[
                "ALL", "live only", "gap only", "novel only",
                "research only", "anti only", "notes only",
            ],
            command=lambda _v: self._rebuild_idea_cards(self._ideas_host),
            width=160,
        )
        self.ideas_filter.set("gap only")
        self.ideas_filter.pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            filter_row, text="Load catalog", fg_color=self.theme["accent"], text_color="#111",
            command=lambda: self._rebuild_idea_cards(self._ideas_host),
        ).pack(side="left")

        ideas_host = ctk.CTkFrame(f, fg_color="transparent")
        ideas_host.pack(fill="both", expand=True)
        self._ideas_host = ideas_host
        ctk.CTkLabel(
            ideas_host, text="(not loaded yet)", text_color=self.theme["muted"]
        ).pack(anchor="w", pady=8)

        self._section(f, "Flag encyclopedia")
        for fl in ["-m", "-f", "-b", "-r", "-x", "-B", "-k", "-e", "-U", "-M", "-w", "-L", "-T", "-N", "--partial", "--selftest"]:
            self._label(f, f"{fl:12}  {explain_flag(fl)}", text_color=self.theme["muted"]).pack(anchor="w")

    def _rebuild_idea_cards(self, host: ctk.CTkFrame) -> None:
        for child in host.winfo_children():
            child.destroy()
        want = self.ideas_filter.get() if hasattr(self, "ideas_filter") else "ALL"
        for title, status, desc in all_idea_cards():
            if want == "live only" and status != "live":
                continue
            if want == "gap only" and status != "gap":
                continue
            if want == "novel only" and status != "novel":
                continue
            if want == "research only" and status not in ("research", "gap", "novel"):
                continue
            if want == "anti only" and status != "anti":
                continue
            if want == "notes only" and status not in ("note", "anti"):
                continue
            card = ctk.CTkFrame(host, fg_color=self.theme["fg"], corner_radius=8)
            card.pack(fill="x", pady=3)
            badge = {
                "live": "LIVE", "research": "RESEARCH", "note": "NOTE",
                "gap": "GAP", "novel": "NOVEL", "anti": "ANTI",
            }.get(status, status.upper())
            color = {
                "live": self.theme["success"],
                "research": self.theme["accent"],
                "gap": "#e6a817",
                "novel": "#7c5cff",
                "note": self.theme["muted"],
                "anti": self.theme.get("danger", "#c44"),
            }.get(status, self.theme["accent"])
            ctk.CTkLabel(
                card, text=f"{badge}  ·  {title}",
                font=ctk.CTkFont(size=13, weight="bold"), text_color=color,
            ).pack(anchor="w", padx=10, pady=(6, 0))
            ctk.CTkLabel(
                card, text=desc, text_color=self.theme["muted"], wraplength=640, justify="left",
            ).pack(anchor="w", padx=10, pady=(2, 8))


    # ── Roadmap ─────────────────────────────────────────────────────────
    def _build_roadmap(self) -> None:
        tab = self.tabs.tab("Roadmap")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Priority roadmap — every P0–P3 item")
        for title, items in (
            ("P0 — ship first", ROADMAP_P0),
            ("P1 — differentiators", ROADMAP_P1),
            ("P2 — research prestige", ROADMAP_P2),
            ("P3 — moonshots", ROADMAP_P3),
        ):
            self._section(f, title)
            for i, item in enumerate(items, 1):
                self._label(f, f"{i}. {item}", text_color=self.theme["muted"]).pack(anchor="w", pady=2)
        self._section(f, "Anti-ideas (explicit — nothing left out)")
        for name, _st, desc in ANTI_IDEAS:
            self._label(f, f"• {name}: {desc}", text_color=self.theme["danger"]).pack(anchor="w")
        self._section(f, "Sources consulted")
        for name, _st, desc in SOURCES:
            self._label(f, f"• {name} — {desc}", text_color=self.theme["muted"]).pack(anchor="w")

    # ── Recipes ─────────────────────────────────────────────────────────
    def _build_recipes(self) -> None:
        tab = self.tabs.tab("Recipes")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Help-table + CLI sketches from the ideas doc")
        self._label(
            f,
            "Pick a recipe → Apply fills TrueCollider fields with research intent.",
            text_color=self.theme["muted"],
        ).pack(anchor="w")
        self.recipe_menu = ctk.CTkOptionMenu(f, values=RECIPE_LABELS, width=640)
        self.recipe_menu.set(RECIPE_LABELS[0])
        self.recipe_menu.pack(anchor="w", pady=8)
        self.recipe_info = ctk.CTkTextbox(f, height=160)
        self.recipe_info.pack(fill="x", pady=4)
        for name, _st, desc in RECIPE_ITEMS:
            self.recipe_info.insert("end", f"{name}: {desc}\n")
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x", pady=8)
        ctk.CTkButton(row, text="Apply recipe → TrueCollider", command=self._apply_recipe).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Copy recipe list", command=lambda: self._copy_text(self.recipe_info.get("1.0", "end"))).pack(side="left", padx=4)

    def _apply_recipe(self) -> None:
        label = self.recipe_menu.get()
        key = label.split(" (")[0].lower()
        mapping = {
            "address + sobol": ("address", "sobol (research)"),
            "rmd160 prefix": ("rmd160", None),
            "rmd160 / shadow160": ("shadow160 (research)", None),
            "bsgs grumpy": ("bsgs", None),
            "bsgs orbit": ("bsgs", None),
            "bsgs handoff": ("bsgs", None),
            "kangaroo --mod": ("kangaroo-mod (research)", None),
            "weakrng milksad": ("weakrng (research)", None),
            "mnemonic mask": ("mnemonic", None),
            "mnemonic pass-*": ("mnemonic", None),
            "mnemonic electrum-v2": ("mnemonic", None),
            "mnemonic milksad": ("mnemonic", None),
            "mnemonic model": ("mnemonic", None),
        }
        for k, (mode, pattern) in mapping.items():
            if k in key:
                token = mode.split(" (")[0].strip().lower()
                self._set_tc_mode(token)
                if pattern and hasattr(self, "tc_pattern"):
                    try:
                        self.tc_pattern.set(pattern)
                    except Exception:
                        pass
                if "bsgs" in k and hasattr(self, "bsgs_strat"):
                    for v in ("grumpy", "orbit", "handoff"):
                        if v in k:
                            try:
                                self.bsgs_strat.set(f"{v} (research)")
                            except Exception:
                                for opt in getattr(self.bsgs_strat, "_values", []) or []:
                                    if opt.split(" (")[0].strip().lower() == v:
                                        self.bsgs_strat.set(opt)
                                        break
                if "mnemonic" in k and hasattr(self, "mn_sub"):
                    for mtoken in ("mask", "pass-dict", "electrum-v2", "milksad", "model"):
                        if mtoken.replace("pass-dict", "pass") in k or mtoken in k:
                            for v in MNEMONIC_SUBMODES:
                                if mtoken.split("-")[0] in v or mtoken in v:
                                    self.mn_sub.set(v)
                                    break
                if "weakrng" in k:
                    self.tabs.set("WeakRNG Lab")
                    self._set_status(f"Recipe applied: {label}")
                    return
                break
        self.tabs.set("TrueCollider")
        self._set_status(f"Recipe applied: {label}")

    # ── Full Ideas Doc ──────────────────────────────────────────────────
    def _build_ideas_doc(self) -> None:
        tab = self.tabs.tab("Full Ideas Doc")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Complete README_IDEAS_FOR_IMPROVEMENT")
        self._ideas_box = ctk.CTkTextbox(f, height=620, font=ctk.CTkFont(family="Consolas", size=12))
        self._ideas_box.pack(fill="both", expand=True, pady=6)
        self._ideas_box.insert("1.0", "Click Load to open the full ideas document (keeps startup fast).\n")
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(fill="x")
        ctk.CTkButton(row, text="Load ideas doc", fg_color=self.theme["accent"], text_color="#111",
                      command=self._load_ideas_doc).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Copy", command=lambda: self._copy_text(self._ideas_box.get("1.0", "end"))).pack(side="left", padx=4)
        ctk.CTkButton(row, text="Open docs folder", command=lambda: os.startfile(str(ROOT / "docs"))).pack(side="left", padx=4)

    def _load_ideas_doc(self) -> None:
        ideas_path = ROOT / "docs" / "README_IDEAS_FOR_IMPROVEMENT.md"
        self._ideas_box.delete("1.0", "end")
        if ideas_path.exists():
            self._ideas_box.insert("1.0", ideas_path.read_text(encoding="utf-8"))
        else:
            self._ideas_box.insert("1.0", completeness_report() + "\n\n(Full markdown missing from docs/)")

    # ── Settings ────────────────────────────────────────────────────────
    def _build_settings(self) -> None:
        tab = self.tabs.tab("Settings")
        f = self._scroll(tab)
        f.pack(fill="both", expand=True)
        self._section(f, "Paths & preferences (editable)")
        self._label(
            f,
            "Edit any path below, then Save. Values sync to TrueCollider / TrueMkey tabs and user_settings.json.",
            text_color=self.theme["muted"],
        ).pack(anchor="w")
        self.set_tc = ctk.StringVar(value=self.settings.get("truecollider_exe", ""))
        self.set_tcc = ctk.StringVar(value=self.settings.get("truecollider_cuda", ""))
        self.set_mk = ctk.StringVar(value=self.settings.get("truemkey_exe", ""))
        self.set_wd = ctk.StringVar(value=self.settings.get("workdir", ""))
        self.set_threads = ctk.StringVar(value=str(self.settings.get("default_threads", "8")))
        self.set_gpu = ctk.StringVar(value=str(self.settings.get("default_gpu", "none")))
        self.set_console_refresh = ctk.StringVar(value=f"{self._console_refresh_sec} sec")
        self._path_row(f, "TrueCollider CPU exe", self.set_tc, exe=True)
        self._path_row(f, "TrueCollider CUDA exe", self.set_tcc, exe=True)
        self._path_row(f, "TrueMkeyCollider exe", self.set_mk, exe=True)
        self._path_row(f, "Default workdir", self.set_wd, directory=True)

        g = ctk.CTkFrame(f, fg_color="transparent")
        g.pack(fill="x", pady=8)
        self._label(g, "Default threads (-t)", text_color=self.theme["muted"]).grid(row=0, column=0, sticky="w", padx=6)
        ctk.CTkEntry(g, textvariable=self.set_threads, width=100).grid(row=1, column=0, sticky="w", padx=6)
        self._label(g, "Default GPU (-U) none/cuda/opencl/both", text_color=self.theme["muted"]).grid(row=0, column=1, sticky="w", padx=6)
        ctk.CTkOptionMenu(g, variable=self.set_gpu, values=GPU, width=120).grid(row=1, column=1, sticky="w", padx=6)
        self._label(g, "Console refresh (GPU-safe)", text_color=self.theme["muted"]).grid(row=0, column=2, sticky="w", padx=6)
        ctk.CTkOptionMenu(
            g, variable=self.set_console_refresh,
            values=["5 sec", "10 sec", "15 sec", "20 sec"], width=100,
            command=self._on_console_refresh,
        ).grid(row=1, column=2, sticky="w", padx=6)

        brow = ctk.CTkFrame(f, fg_color="transparent")
        brow.pack(fill="x", pady=12)
        ctk.CTkButton(brow, text="Save Settings", fg_color=self.theme["accent"], text_color="#111",
                      command=self._persist_settings).pack(side="left", padx=4)
        ctk.CTkButton(brow, text="Reload from disk", command=self._reload_settings_ui).pack(side="left", padx=4)
        ctk.CTkButton(brow, text="Reset to auto-detect", command=self._reset_settings).pack(side="left", padx=4)
        ctk.CTkButton(brow, text="Open logs folder", command=lambda: os.startfile(str(LOG_DIR))).pack(side="left", padx=4)
        ctk.CTkButton(brow, text="Open settings JSON", command=lambda: os.startfile(str(CONFIG_PATH))).pack(side="left", padx=4)

    def _reload_settings_ui(self) -> None:
        self._load_settings()
        self.set_tc.set(self.settings.get("truecollider_exe", ""))
        self.set_tcc.set(self.settings.get("truecollider_cuda", ""))
        self.set_mk.set(self.settings.get("truemkey_exe", ""))
        self.set_wd.set(self.settings.get("workdir", ""))
        self.set_threads.set(str(self.settings.get("default_threads", "8")))
        self.set_gpu.set(str(self.settings.get("default_gpu", "none")))
        sec = int(self.settings.get("console_refresh_sec", 10) or 10)
        if sec not in (5, 10, 15, 20):
            sec = 10
        self._console_refresh_sec = sec
        self.set_console_refresh.set(f"{sec} sec")
        if hasattr(self, "console_refresh"):
            self.console_refresh.set(f"{sec} sec")
        self._set_status("Settings reloaded from disk")

    def _reset_settings(self) -> None:
        self.settings.update(_default_paths())
        self._reload_settings_ui()
        self._persist_settings()

    def _persist_settings(self) -> None:
        self.settings["truecollider_exe"] = self.set_tc.get().strip()
        self.settings["truecollider_cuda"] = self.set_tcc.get().strip()
        self.settings["truemkey_exe"] = self.set_mk.get().strip()
        self.settings["workdir"] = self.set_wd.get().strip()
        self.settings["default_threads"] = self.set_threads.get().strip() or "8"
        self.settings["default_gpu"] = self.set_gpu.get().strip() or "none"
        self._on_console_refresh(self.set_console_refresh.get())
        self.settings["console_refresh_sec"] = self._console_refresh_sec
        self.settings["theme"] = self.theme_name
        # Sync live widgets
        if hasattr(self, "tc_exe"):
            self.tc_exe.set(self.settings["truecollider_exe"])
        if hasattr(self, "tc_cwd"):
            self.tc_cwd.set(self.settings["workdir"])
        if hasattr(self, "mk_exe"):
            self.mk_exe.set(self.settings["truemkey_exe"])
        if hasattr(self, "tc_threads"):
            self.tc_threads.set(self.settings["default_threads"])
        if hasattr(self, "tc_gpu"):
            try:
                self.tc_gpu.set(self.settings["default_gpu"])
            except Exception:
                pass
        if hasattr(self, "mk_gpu"):
            try:
                self.mk_gpu.set(self.settings["default_gpu"])
                self._sync_mk_gpu_panel()
            except Exception:
                pass
        if hasattr(self, "console_refresh"):
            self.console_refresh.set(f"{self._console_refresh_sec} sec")
        CONFIG_PATH.write_text(json.dumps(self.settings, indent=2), encoding="utf-8")
        self._set_status(f"Settings saved → {CONFIG_PATH}")
        messagebox.showinfo("Saved", f"Settings written to\n{CONFIG_PATH}")

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
    def _on_console_refresh(self, value: str) -> None:
        try:
            sec = int(str(value).split()[0])
        except Exception:
            sec = 10
        if sec not in (5, 10, 15, 20):
            sec = 10
        self._console_refresh_sec = sec
        self.settings["console_refresh_sec"] = sec
        try:
            CONFIG_PATH.write_text(json.dumps(self.settings, indent=2), encoding="utf-8")
        except Exception:
            pass
        if hasattr(self, "set_console_refresh"):
            self.set_console_refresh.set(f"{sec} sec")
        if hasattr(self, "console_refresh"):
            self.console_refresh.set(f"{sec} sec")
        self._set_status(f"Console refresh set to {sec}s (buffered — safer for GPU)")

    def _refresh_console_now(self) -> None:
        pending = self._console_pending_bytes
        self._console_force_flush = True
        self._flush_console()
        self._set_status(
            f"Console refreshed ({pending // 1024} KB were buffered)" if pending else "Console refreshed"
        )

    def _stop_and_flush(self) -> None:
        self.runner.stop()
        self._console_force_flush = True
        self._flush_console()

    def _ui_tick(self) -> None:
        """Main-thread pump — status often; console only on chosen interval."""
        try:
            now = time.monotonic()
            if self._console_force_flush or (now - self._console_last_flush) >= float(self._console_refresh_sec):
                self._flush_console()
            if self._status_q:
                msg = self._status_q[-1]
                self._status_q.clear()
                self._set_status(msg)
            # Show buffered size so user knows output is waiting
            if self._console_pending_bytes > 0 and self.runner.running:
                kb = self._console_pending_bytes // 1024
                self.status.configure(
                    text=f"Running… console buffer {kb} KB — refresh in "
                         f"{max(0, int(self._console_refresh_sec - (now - self._console_last_flush)))}s "
                         f"(or click Refresh now)"
                )
        finally:
            try:
                self.after(250, self._ui_tick)
            except Exception:
                pass

    def _append_console(self, text: str) -> None:
        # Worker threads only enqueue — main thread flushes on interval
        if not text:
            return
        self._console_q.append(text)
        self._console_pending_bytes += len(text)
        # Cap buffer so a 20s GPU flood cannot OOM the GUI
        max_buf = 256_000
        while self._console_pending_bytes > max_buf and self._console_q:
            dropped = self._console_q.pop(0)
            self._console_pending_bytes -= len(dropped)
            if not hasattr(self, "_console_dropped_note") or not self._console_dropped_note:
                self._console_q.insert(0, "[TrueNexus] (console buffer capped — older lines dropped)\n")
                self._console_pending_bytes += 60
                self._console_dropped_note = True

    def _flush_console(self) -> None:
        self._console_force_flush = False
        self._console_last_flush = time.monotonic()
        self._console_dropped_note = False
        if not self._console_q:
            self._console_pending_bytes = 0
            return
        chunk = "".join(self._console_q)
        self._console_q.clear()
        self._console_pending_bytes = 0
        try:
            # Hard-cap each flush so one paste cannot freeze Tk
            if len(chunk) > 120_000:
                chunk = (
                    "[TrueNexus] (flush truncated to last 120 KB for GUI safety)\n"
                    + chunk[-120_000:]
                )
            self.console.insert("end", chunk)
            self.console.see("end")
            content = self.console.get("1.0", "end")
            if len(content) > 300_000:
                self.console.delete("1.0", "end-200000c")
        except Exception:
            pass

    def _clear_console(self) -> None:
        self._console_q.clear()
        self._console_pending_bytes = 0
        self._console_dropped_note = False
        self.console.delete("1.0", "end")

    def _copy_console(self) -> None:
        self._console_force_flush = True
        self._flush_console()
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
            self._append_console("[TrueNexus] Type a command first, then press Run / Enter.\n")
            return
        cwd = ""
        if hasattr(self, "tc_cwd"):
            cwd = self.tc_cwd.get().strip()
        if not cwd:
            cwd = self.settings.get("workdir", "") or str(ROOT)
        if not Path(cwd).is_dir():
            self._append_console(f"[TrueNexus] Invalid workdir: {cwd}\n")
            messagebox.showerror("Run", f"Working directory does not exist:\n{cwd}\n\nFix it in Settings.")
            return
        self.cmd_entry.delete(0, "end")
        self._set_status(f"Running: {cmd[:80]}")
        self.runner.start(cmd, cwd=cwd)

    def _on_proc_done(self, code: int) -> None:
        self._status_q.append(f"Process finished ({code})")
        # Pull remaining buffered lines when the job ends
        self._console_force_flush = True

    def _set_status(self, text: str) -> None:
        try:
            self.status.configure(text=text)
        except Exception:
            pass

    def _on_theme(self, name: str) -> None:
        self.settings["theme"] = name
        self.theme_name = name
        CONFIG_PATH.write_text(json.dumps(self.settings, indent=2), encoding="utf-8")
        messagebox.showinfo(
            "Theme",
            f"Theme '{name}' saved. Restart TrueNexus to fully re-skin all panels.",
        )


def main() -> None:
    # Allow `python -m truenexus.app` from TrueNexus root
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
    app = TrueNexusApp()
    app.mainloop()


if __name__ == "__main__":
    main()
