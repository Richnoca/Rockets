import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import webbrowser

from visualize import plot_scoring_trend
from players_data import load_rockets_player_stats_espn
from standings_data import load_nba_standings


class RocketsApp(tk.Tk):

    def __init__(self, summary, df_completed, season):
        super().__init__()

        self._apply_dark_mode()

        self.title("Houston Rockets Performance Tracker")
        self.geometry("1050x600")

        self.season = season

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True)

        summary_tab = ttk.Frame(notebook)
        games_tab = ttk.Frame(notebook)
        players_tab = ttk.Frame(notebook)
        standings_tab = ttk.Frame(notebook)

        notebook.add(summary_tab, text="Summary")
        notebook.add(games_tab, text="Games Played")
        notebook.add(players_tab, text="Players")
        notebook.add(standings_tab, text="Standings")

        self._build_summary_tab(summary_tab, summary, df_completed)
        self._build_games_tab(games_tab, df_completed)
        self._build_players_tab(players_tab)
        self._build_standings_tab(standings_tab)

        self._load_players_async()
        self._load_standings_async()

    # -------------------- DARK MODE --------------------

    def _apply_dark_mode(self):
        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except Exception:
            pass

        bg = "#1e1e1e"
        fg = "#e6e6e6"
        panel = "#252526"
        accent = "#3a3a3a"

        self.configure(bg=bg)

        style.configure(".", background=bg, foreground=fg)
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("TLabelFrame", background=bg, foreground=fg)
        style.configure("TLabelFrame.Label", background=bg, foreground=fg)

        style.configure("TButton", background=panel, foreground=fg, padding=6)
        style.map("TButton", background=[("active", accent)])

        style.configure("TNotebook", background=bg, borderwidth=0)
        style.configure("TNotebook.Tab", background=panel, foreground=fg, padding=(10, 6))
        style.map("TNotebook.Tab", background=[("selected", accent)])

        style.configure(
            "Treeview",
            background=panel,
            fieldbackground=panel,
            foreground=fg,
            bordercolor=bg,
            rowheight=24
        )
        style.map(
            "Treeview",
            background=[("selected", "#0e639c")],
            foreground=[("selected", "#ffffff")]
        )
        style.configure("Treeview.Heading", background=bg, foreground=fg)
        style.map("Treeview.Heading", background=[("active", accent)])

    # -------------------- SUMMARY TAB --------------------

    def _build_summary_tab(self, parent, summary, df_completed):

        title = ttk.Label(
            parent,
            text="Houston Rockets Stats (2025-2026)",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=10)

        frame = ttk.Frame(parent)
        frame.pack(pady=10)

        for key, value in summary.items():
            row = ttk.Frame(frame)
            row.pack(fill="x", pady=2)

            ttk.Label(row, text=f"{key}:", width=22).pack(side="left")
            ttk.Label(row, text=str(value)).pack(side="left")

        ttk.Button(
            parent,
            text="Show Scoring Trend",
            command=lambda: plot_scoring_trend(df_completed)
        ).pack(pady=15)

    # -------------------- GAMES TAB --------------------

    def _build_games_tab(self, parent, df_completed):

        header = ttk.Label(parent, text="Completed Games", font=("Arial", 12, "bold"))
        header.pack(pady=8)

        table_frame = ttk.Frame(parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("GAME_DATE", "MATCHUP", "WL", "SCORE")

        self.games_tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        self.games_tree.heading("GAME_DATE", text="Date")
        self.games_tree.heading("MATCHUP", text="Matchup")
        self.games_tree.heading("WL", text="W/L")
        self.games_tree.heading("SCORE", text="Score")

        self.games_tree.column("GAME_DATE", width=120, anchor="w")
        self.games_tree.column("MATCHUP", width=360, anchor="w")
        self.games_tree.column("WL", width=60, anchor="center")
        self.games_tree.column("SCORE", width=120, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.games_tree.yview)
        self.games_tree.configure(yscrollcommand=vsb.set)

        self.games_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        df = df_completed.copy()
        df["__date"] = pd.to_datetime(df["GAME_DATE"], errors="coerce")
        df = df.sort_values("__date", ascending=False)

        self._event_id_by_item = {}

        for _, row in df.iterrows():
            score = f"{row.get('PTS','')}-{row.get('PTS_OPP','')}"
            item = self.games_tree.insert(
                "",
                "end",
                values=(
                    row.get("GAME_DATE", ""),
                    row.get("MATCHUP", ""),
                    row.get("WL", ""),
                    score
                )
            )
            self._event_id_by_item[item] = str(row.get("EVENT_ID", "")).strip()

        ttk.Button(parent, text="Open Highlights", command=self._open_highlights).pack(pady=5)

    def _open_highlights(self):

        sel = self.games_tree.selection()
        if not sel:
            messagebox.showinfo("Highlights", "Select a game first.")
            return

        event_id = self._event_id_by_item.get(sel[0], "")
        if not event_id:
            messagebox.showerror("Highlights", "No EVENT_ID found for that game.")
            return

        webbrowser.open(f"https://www.espn.com/nba/game/_/gameId/{event_id}")

    # -------------------- PLAYERS TAB --------------------

    def _build_players_tab(self, parent):

        top = ttk.Frame(parent)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(top, text="Rockets Player Season Averages", font=("Arial", 12, "bold")).pack(side="left")

        self.players_status = ttk.Label(top, text="Loading...")
        self.players_status.pack(side="right")

        table_frame = ttk.Frame(parent)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("Player", "GP", "MPG", "PPG", "RPG", "APG", "SPG", "TOV", "FG%", "3P%", "FT%")

        self.players_tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        for col in columns:
            self.players_tree.heading(col, text=col, command=lambda c=col: self._sort_treeview(self.players_tree, c, False))
            if col == "Player":
                self.players_tree.column(col, width=200, anchor="w")
            else:
                self.players_tree.column(col, width=85, anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.players_tree.yview)
        self.players_tree.configure(yscrollcommand=vsb.set)

        self.players_tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    def _load_players_async(self):
        import threading

        def worker():
            try:
                df = load_rockets_player_stats_espn(use_cache=True)
                self.after(0, lambda df=df: self._populate_players(df))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda msg=msg: self.players_status.config(text=f"Error: {msg}"))

        threading.Thread(target=worker, daemon=True).start()

    def _populate_players(self, df):

        for item in self.players_tree.get_children():
            self.players_tree.delete(item)

        df = df.copy()

        for col in ["MPG", "PPG", "RPG", "APG", "SPG", "TOV"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").map(lambda x: "" if pd.isna(x) else f"{x:.1f}")

        for col in ["FG%", "3P%", "FT%"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").map(lambda x: "" if pd.isna(x) else f"{x:.3f}")

        # sort by PPG (numeric) using a temp numeric column
        df["_ppg_num"] = pd.to_numeric(df["PPG"], errors="coerce").fillna(0)
        df = df.sort_values("_ppg_num", ascending=False).drop(columns=["_ppg_num"])

        for _, row in df.iterrows():
            self.players_tree.insert("", "end", values=tuple(row.get(c, "") for c in df.columns))

        self.players_status.config(text=f"{len(df)} players")

    # -------------------- STANDINGS TAB --------------------

    def _build_standings_tab(self, parent):

        top = ttk.Frame(parent)
        top.pack(fill="x", padx=10, pady=10)

        ttk.Label(top, text="NBA Standings", font=("Arial", 12, "bold")).pack(side="left")

        self.standings_status = ttk.Label(top, text="Loading...")
        self.standings_status.pack(side="right")

        body = ttk.Frame(parent)
        body.pack(fill="both", expand=True, padx=10, pady=10)

        left = ttk.LabelFrame(body, text="Eastern Conference")
        right = ttk.LabelFrame(body, text="Western Conference")
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))
        right.pack(side="left", fill="both", expand=True, padx=(8, 0))

        columns = ("Seed", "Team", "W", "L", "PCT", "GB", "STRK")

        self.east_tree = ttk.Treeview(left, columns=columns, show="headings")
        self.west_tree = ttk.Treeview(right, columns=columns, show="headings")

        for tree in (self.east_tree, self.west_tree):
            for col in columns:
                tree.heading(col, text=col, command=lambda t=tree, c=col: self._sort_treeview(t, c, False))
                if col == "Team":
                    tree.column(col, width=180, anchor="w")
                elif col == "Seed":
                    tree.column(col, width=50, anchor="center")
                else:
                    tree.column(col, width=70, anchor="center")

        east_scroll = ttk.Scrollbar(left, orient="vertical", command=self.east_tree.yview)
        west_scroll = ttk.Scrollbar(right, orient="vertical", command=self.west_tree.yview)

        self.east_tree.configure(yscrollcommand=east_scroll.set)
        self.west_tree.configure(yscrollcommand=west_scroll.set)

        self.east_tree.pack(side="left", fill="both", expand=True)
        east_scroll.pack(side="right", fill="y")

        self.west_tree.pack(side="left", fill="both", expand=True)
        west_scroll.pack(side="right", fill="y")

    def _load_standings_async(self):
        import threading

        def worker():
            try:
                east, west = load_nba_standings()
                self.after(0, lambda e=east, w=west: self._populate_standings(e, w))
            except Exception as e:
                msg = str(e)
                self.after(0, lambda msg=msg: self.standings_status.config(text=f"Error: {msg}"))

        threading.Thread(target=worker, daemon=True).start()

    def _populate_standings(self, east_df, west_df):

        for item in self.east_tree.get_children():
            self.east_tree.delete(item)
        for item in self.west_tree.get_children():
            self.west_tree.delete(item)

        east = east_df.copy()
        west = west_df.copy()

        for df in (east, west):
            df["PCT"] = pd.to_numeric(df["PCT"], errors="coerce").fillna(0).map(lambda x: f"{x:.3f}")

        for _, r in east.iterrows():
            self.east_tree.insert("", "end", values=tuple(r.values))

        for _, r in west.iterrows():
            self.west_tree.insert("", "end", values=tuple(r.values))

        self.standings_status.config(text="Updated")

    # -------------------- GENERIC SORT --------------------

    def _sort_treeview(self, tree, col, reverse):

        data = [(tree.set(k, col), k) for k in tree.get_children("")]

        def to_float(x):
            try:
                return float(x)
            except Exception:
                return None

        numeric = True
        converted = []
        for v, k in data:
            fv = to_float(v)
            if fv is None:
                numeric = False
                break
            converted.append((fv, k))

        if numeric:
            converted.sort(key=lambda t: t[0], reverse=reverse)
            ordered = converted
        else:
            data.sort(key=lambda t: t[0], reverse=reverse)
            ordered = data

        for i, (_, k) in enumerate(ordered):
            tree.move(k, "", i)

        tree.heading(col, command=lambda: self._sort_treeview(tree, col, not reverse))
