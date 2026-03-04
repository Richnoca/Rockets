from __future__ import annotations

from pathlib import Path
from datetime import date, timedelta
import time
import pandas as pd
import requests


CACHE_DIR = Path("data")
CACHE_DIR.mkdir(exist_ok=True)

CACHE_PLAYERS = CACHE_DIR / "rockets_players_espn.csv"

ESPN_SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"
ESPN_BOXSCORE_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/summary"

TEAM_ABBR = "HOU"
START_DATE = date(2025, 10, 21)


def _fmt_game_date(d: date) -> str:
    return pd.Timestamp(d).strftime("%b %d, %Y")


def _get_json(url: str, params: dict, timeout: int = 15) -> dict:
    r = requests.get(url, params=params, timeout=timeout)
    r.raise_for_status()
    return r.json()


def _safe_int(x) -> int:
    try:
        return int(x)
    except Exception:
        return 0


def _safe_float(x) -> float:
    try:
        return float(x)
    except Exception:
        return 0.0


def _parse_made_att(s: str) -> tuple[int, int]:
    # ESPN commonly returns "7-15" style strings
    if not s or "-" not in str(s):
        return 0, 0
    a, b = str(s).split("-", 1)
    return _safe_int(a), _safe_int(b)


def _parse_minutes(min_str) -> float:
    # ESPN often uses "34:12"
    if not min_str:
        return 0.0
    s = str(min_str)
    if ":" not in s:
        return _safe_float(s)
    mm, ss = s.split(":", 1)
    return _safe_int(mm) + (_safe_int(ss) / 60.0)


def _find_rockets_completed_event_ids(today: date) -> list[tuple[str, date]]:
    ids: list[tuple[str, date]] = []

    d = START_DATE
    while d <= today:
        data = _get_json(ESPN_SCOREBOARD_URL, {"dates": d.strftime("%Y%m%d")})
        for ev in data.get("events", []):
            comp = (ev.get("competitions") or [None])[0]
            if not comp:
                continue

            status_type = comp.get("status", {}).get("type", {})
            if status_type.get("state") != "post":
                continue

            competitors = comp.get("competitors", [])
            if len(competitors) != 2:
                continue

            abbr0 = competitors[0].get("team", {}).get("abbreviation")
            abbr1 = competitors[1].get("team", {}).get("abbreviation")

            if abbr0 == TEAM_ABBR or abbr1 == TEAM_ABBR:
                ev_id = ev.get("id")
                if ev_id:
                    ids.append((str(ev_id), d))
        d += timedelta(days=1)

    return ids


def _extract_team_player_table(summary_json: dict, team_abbr: str) -> pd.DataFrame:
    """
    ESPN summary JSON -> one row per player for the specified team.
    Uses boxscore->players groups. This structure can vary a bit, so this function
    is defensive and only extracts stats when present.
    """
    box = summary_json.get("boxscore", {})
    players_groups = box.get("players", [])
    if not players_groups:
        return pd.DataFrame()

    # each entry corresponds to a team
    for team_entry in players_groups:
        team = team_entry.get("team", {})
        abbr = team.get("abbreviation")
        if abbr != team_abbr:
            continue

        rows = []
        for stat_group in team_entry.get("statistics", []):
            athletes = stat_group.get("athletes", [])
            labels = stat_group.get("labels", [])
            # we want the "starters" and "bench" groups usually both have same labels
            for a in athletes:
                athlete = a.get("athlete", {})
                name = athlete.get("displayName", "Unknown")

                stats = a.get("stats", [])
                # map label -> value
                m = {}
                for i in range(min(len(labels), len(stats))):
                    m[labels[i]] = stats[i]

                # Common ESPN labels (but can vary): MIN, FG, 3PT, FT, REB, AST, STL, TO, PTS
                rows.append({
                    "Player": name,
                    "MIN_STR": m.get("MIN", ""),
                    "FG": m.get("FG", ""),
                    "3PT": m.get("3PT", m.get("3P", "")),
                    "FT": m.get("FT", ""),
                    "REB": m.get("REB", m.get("TRB", "")),
                    "AST": m.get("AST", ""),
                    "STL": m.get("STL", ""),
                    "TOV": m.get("TO", m.get("TOV", "")),
                    "PTS": m.get("PTS", ""),
                    "DNP": a.get("didNotPlay", False)
                })

        df = pd.DataFrame(rows)
        if df.empty:
            return df

        # drop DNP rows (no minutes)
        df["MIN"] = df["MIN_STR"].map(_parse_minutes)
        df = df[df["MIN"] > 0].copy()

        # parse shooting strings
        df["FGM"], df["FGA"] = zip(*df["FG"].map(_parse_made_att))
        df["3PM"], df["3PA"] = zip(*df["3PT"].map(_parse_made_att))
        df["FTM"], df["FTA"] = zip(*df["FT"].map(_parse_made_att))

        # numeric counting stats
        for c in ["REB", "AST", "STL", "TOV", "PTS"]:
            df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)

        return df

    return pd.DataFrame()


def load_rockets_player_stats_espn(use_cache=True, timeout=15, sleep_seconds=0.2) -> pd.DataFrame:
    """
    Returns one row per Rockets player with:
    GP, MPG, PPG, RPG, APG, SPG, TOV, FG%, 3P%, FT%
    """
    if use_cache and CACHE_PLAYERS.exists():
        df = pd.read_csv(CACHE_PLAYERS)
        if not df.empty:
            return df

    today = date.today()
    event_ids = _find_rockets_completed_event_ids(today)

    if not event_ids:
        raise RuntimeError("No completed Rockets games found to build player stats.")

    # aggregate totals
    totals = {}

    for ev_id, _d in event_ids:
        summary = _get_json(ESPN_BOXSCORE_URL, {"event": ev_id}, timeout=timeout)
        df_game = _extract_team_player_table(summary, TEAM_ABBR)
        if df_game.empty:
            continue

        for _, r in df_game.iterrows():
            name = r["Player"]
            t = totals.get(name)
            if t is None:
                t = {
                    "GP": 0,
                    "MIN": 0.0,
                    "PTS": 0.0,
                    "REB": 0.0,
                    "AST": 0.0,
                    "STL": 0.0,
                    "TOV": 0.0,
                    "FGM": 0, "FGA": 0,
                    "3PM": 0, "3PA": 0,
                    "FTM": 0, "FTA": 0,
                }
                totals[name] = t

            t["GP"] += 1
            t["MIN"] += float(r["MIN"])
            t["PTS"] += float(r["PTS"])
            t["REB"] += float(r["REB"])
            t["AST"] += float(r["AST"])
            t["STL"] += float(r["STL"])
            t["TOV"] += float(r["TOV"])
            t["FGM"] += int(r["FGM"]); t["FGA"] += int(r["FGA"])
            t["3PM"] += int(r["3PM"]); t["3PA"] += int(r["3PA"])
            t["FTM"] += int(r["FTM"]); t["FTA"] += int(r["FTA"])

        time.sleep(sleep_seconds)

    out_rows = []
    for name, t in totals.items():
        gp = max(int(t["GP"]), 1)

        fg_pct = (t["FGM"] / t["FGA"]) if t["FGA"] > 0 else 0.0
        fg3_pct = (t["3PM"] / t["3PA"]) if t["3PA"] > 0 else 0.0
        ft_pct = (t["FTM"] / t["FTA"]) if t["FTA"] > 0 else 0.0

        out_rows.append({
            "Player": name,
            "GP": int(t["GP"]),
            "MPG": t["MIN"] / gp,
            "PPG": t["PTS"] / gp,
            "RPG": t["REB"] / gp,
            "APG": t["AST"] / gp,
            "SPG": t["STL"] / gp,
            "TOV": t["TOV"] / gp,
            "FG%": fg_pct,
            "3P%": fg3_pct,
            "FT%": ft_pct,
        })

    df_out = pd.DataFrame(out_rows).sort_values("PPG", ascending=False).reset_index(drop=True)
    df_out.to_csv(CACHE_PLAYERS, index=False)
    return df_out
