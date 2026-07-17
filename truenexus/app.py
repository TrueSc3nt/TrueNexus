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
from truenexus.puzzles import (
    KNOWN_ADDR,
    parse_puzzle_number,
    puzzle_label,
    puzzle_range_display,
    puzzle_range_hex,
    puzzle_status,
    recommend_mode,
    write_puzzle_target_file,
)
from truenexus.runner import ProcessRunner
from truenexus.themes import DEFAULT_THEME, THEMES

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
        nav_names = (
            "Home", "TrueCollider", "Puzzles", "Mnemonic Lab", "BSGS Lab",
            "Address / RMD160", "WeakRNG Lab", "TrueMkey", "Ideas Matrix",
            "Roadmap", "Recipes", "Full Ideas Doc", "Settings", "About",
        )
        sidebar = ctk.CTkFrame(body, fg_color=self.theme["card"], width=200, corner_radius=10)
        sidebar.grid(row=0, column=0, sticky="nsw", padx=(0, 8))
        sidebar.grid_propagate(False)
        ctk.CTkLabel(
            sidebar, text="NAV", font=ctk.CTkFont(size=12, weight="bold"),
            text_color=self.theme["muted"],
        ).pack(anchor="w", padx=14, pady=(12, 6))
        nav_scroll = ctk.CTkScrollableFrame(sidebar, fg_color="transparent", width=180)
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
        self._build_collider()
        self._build_puzzles()
        self._build_mnemonic()
        self._build_bsgs()
        self._build_address()
        self._build_weakrng()
        self._build_mkey()
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
            mnemonic_words=getattr(self, "mn_words", ctk.StringVar(value="12")).get()
            if hasattr(self, "mn_words") else "12",
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
            filter_strategy=self.addr_filter.get() if hasattr(self, "addr_filter") else "default fuse",
            address_sub=self.addr_sub.get() if hasattr(self, "addr_sub") else "default",
            rmd160_sub=self.rmd_sub.get() if hasattr(self, "rmd_sub") else "exact",
            weakrng_sub=self.wr_sub.get() if hasattr(self, "wr_sub") else "milksad",
            timestamp_window=self.wr_ts.get() if hasattr(self, "wr_ts") else "",
            residue_mr=self.bsgs_mod.get() if hasattr(self, "bsgs_mod") else "",
            collision_bits=self.shadow_bits.get() if hasattr(self, "shadow_bits") else "48",
            stride=self.addr_stride.get() if hasattr(self, "addr_stride") else "",
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
            "All 160 official addresses are built-in. Auto-write creates the -f target file.",
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

    def _refresh_puzzle(self) -> None:
        n = self._current_puzzle()
        try:
            self.puzzle_slider.set(n)
        except Exception:
            pass
        start, end = puzzle_range_hex(n)
        addr = KNOWN_ADDR.get(n, "(missing address)")
        st = puzzle_status(n)
        txt = (
            f"{puzzle_label(n)}\n"
            f"Source: https://privatekeys.pw/puzzles/bitcoin-puzzle-tx\n"
            f"Status: {st}\n"
            f"Bits: {n}   (keyspace 2^{n-1} .. 2^{n}-1)\n"
            f"Range: {puzzle_range_display(n)}\n"
            f"CLI:  -b {n}   or   -r {start}:{end}\n"
            f"Address: {addr}\n"
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
        # Prefer address grind; bsgs/kangaroo need a pubkey file
        try:
            self.tc_mode.set("address")
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
        if n not in KNOWN_ADDR:
            messagebox.showwarning("No address", "Puzzle address missing from catalog.")
            return
        # Default into workdir / presets without forcing a save dialog every time
        out_dir = Path(self.tc_cwd.get().strip() or ROOT / "presets")
        out_dir.mkdir(parents=True, exist_ok=True)
        path = str(out_dir / f"puzzle_{n}.txt")
        write_puzzle_target_file(n, path)
        self.tc_target.set(path)
        self._append_console(f"[TrueNexus] Wrote puzzle target: {path}\n")
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

        tips = (
            "Live: sequential · backward · both · random · dance\n"
            "Research: grumpy · interleave · orbit · residue · dual-range · nested/fractal ·\n"
            "async-resolve · multi-target · negmap · handoff · gravity/chaos/sobol-giant ·\n"
            "freeze-table · compact-dp\n"
            "RAM guide: 8G→-k512 | 16G→-k1024 | 32G→-k2048 | Prefer kangaroo when N is huge.\n"
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
        self.tc_mode.set(mode if mode in MODES_LIVE else "rmd160")
        if hasattr(self, "addr_stride") and self.addr_stride.get().strip():
            # stash into extra if numeric
            pass
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
        # Pick exact dropdown value (live or annotated)
        chosen = "weakrng"
        for v in MODES_ALL:
            if v.split(" (")[0].strip().lower() == "weakrng":
                chosen = v
                break
        try:
            self.tc_mode.set(chosen)
        except Exception:
            pass
        self.tabs.set("TrueCollider")
        self._set_status(f"WeakRNG {self.wr_sub.get()} applied")

    def _apply_mn_milksad(self) -> None:
        self.tc_mode.set("mnemonic")
        if hasattr(self, "mn_sub"):
            # find milksad in list
            for v in MNEMONIC_SUBMODES:
                if "milksad" in v:
                    self.mn_sub.set(v)
                    break
        self.tabs.set("Mnemonic Lab")
        self._set_status("Mnemonic Milk Sad / EntropyTimeline selected")

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
        self._section(f, "EVERY idea from README_IDEAS_FOR_IMPROVEMENT")
        self._label(
            f,
            "Catalog is large — click Load to populate (keeps the app snappy).",
            text_color=self.theme["muted"],
        ).pack(anchor="w")

        filter_row = ctk.CTkFrame(f, fg_color="transparent")
        filter_row.pack(fill="x", pady=4)
        self.ideas_filter = ctk.CTkOptionMenu(
            filter_row,
            values=["ALL", "live only", "research only", "notes only"],
            command=lambda _v: self._rebuild_idea_cards(self._ideas_host),
            width=180,
        )
        self.ideas_filter.set("live only")
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
            if want == "research only" and status != "research":
                continue
            if want == "notes only" and status != "note":
                continue
            card = ctk.CTkFrame(host, fg_color=self.theme["fg"], corner_radius=8)
            card.pack(fill="x", pady=3)
            badge = {"live": "LIVE", "research": "RESEARCH", "note": "NOTE"}.get(status, status.upper())
            color = {
                "live": self.theme["success"],
                "research": self.theme["accent"],
                "note": self.theme["muted"],
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
                self.tc_mode.set(mode)
                if pattern and hasattr(self, "tc_pattern"):
                    # try set pattern if exists in menu values
                    try:
                        self.tc_pattern.set(pattern)
                    except Exception:
                        pass
                if "bsgs" in k and hasattr(self, "bsgs_strat"):
                    for v in ("grumpy", "orbit", "handoff"):
                        if v in k:
                            for opt in self.bsgs_strat._values if hasattr(self.bsgs_strat, "_values") else []:
                                pass
                            try:
                                self.bsgs_strat.set(f"{v} (research)")
                            except Exception:
                                pass
                if "mnemonic" in k and hasattr(self, "mn_sub"):
                    for token in ("mask", "pass-dict", "electrum-v2", "milksad", "model"):
                        if token.replace("pass-dict", "pass") in k or token in k:
                            for v in MNEMONIC_SUBMODES:
                                if token.split("-")[0] in v or token in v:
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
        self._label(g, "Default GPU (-U)", text_color=self.theme["muted"]).grid(row=0, column=1, sticky="w", padx=6)
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
