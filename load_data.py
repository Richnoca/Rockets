from __future__ import annotations

from pathlib import Path
from datetime import date, timedelta
import pandas as pd
import requests


CACHE_DIR = Path("data")
CACHE_DIR.mkdir(exist_ok=True)

CACHE_FILE = CACHE_DIR / "rockets_games_completed.csv"

ESPN_SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard"

TEAM_ABBR = "HOU"
START_DATE = date(2025, 10, 21)


def _fmt_game_date(d: date) -> str:
    return pd.Timestamp(d).strftime("%b %d, %Y")


def _get_scoreboard(d: date, timeout: int = 15) -> dict:
    r = requests.get(
        ESPN_SCOREBOARD_URL,
        params={"dates": d.strftime("%Y%m%d")},
        timeout=timeout
    )
    r.raise_for_status()
    return r.json()


def load_team_games(season="2025-26", use_cache=True) -> pd.DataFrame:

    if use_cache and CACHE_FILE.exists():
        df = pd.read_csv(CACHE_FILE)
        if not df.empty:
            return df

    today = date.today()

    rows = []
    d = START_DATE

    while d <= today:

        data = _get_scoreboard(d)

        for ev in data.get("events", []):

            ev_id = ev.get("id")
            if not ev_id:
                continue

            comp = (ev.get("competitions") or [None])[0]
            if not comp:
                continue

            status_type = comp.get("status", {}).get("type", {})
            state = status_type.get("state")

            if state != "post":
                continue

            competitors = comp.get("competitors", [])
            if len(competitors) != 2:
                continue

            team0 = competitors[0]["team"]["abbreviation"]
            team1 = competitors[1]["team"]["abbreviation"]

            if team0 != TEAM_ABBR and team1 != TEAM_ABBR:
                continue

            try:
                score0 = int(float(competitors[0]["score"]))
                score1 = int(float(competitors[1]["score"]))
            except Exception:
                continue

            rockets_is_0 = team0 == TEAM_ABBR

            rockets = competitors[0] if rockets_is_0 else competitors[1]
            opp = competitors[1] if rockets_is_0 else competitors[0]

            rockets_score = score0 if rockets_is_0 else score1
            opp_score = score1 if rockets_is_0 else score0

            opp_abbr = opp["team"]["abbreviation"]

            homeaway = rockets.get("homeAway")

            matchup = (
                f"{TEAM_ABBR} vs {opp_abbr}"
                if homeaway == "home"
                else f"{TEAM_ABBR} @ {opp_abbr}"
            )

            wl = "W" if rockets_score > opp_score else "L"

            rows.append({
                "EVENT_ID": str(ev_id),
                "GAME_DATE": _fmt_game_date(d),
                "MATCHUP": matchup,
                "WL": wl,
                "PTS": rockets_score,
                "PTS_OPP": opp_score
            })

        d += timedelta(days=1)

    df = pd.DataFrame(rows)

    df.to_csv(CACHE_FILE, index=False)

    return df


def load_next_rockets_game(days_ahead=30, timeout=10):

    today = date.today()
    end = today + timedelta(days=days_ahead)

    best_dt = None
    best_str = None

    d = today

    while d <= end:

        data = _get_scoreboard(d, timeout=timeout)

        for ev in data.get("events", []):

            comp = (ev.get("competitions") or [None])[0]
            if not comp:
                continue

            competitors = comp.get("competitors", [])
            if len(competitors) != 2:
                continue

            abbr0 = competitors[0]["team"]["abbreviation"]
            abbr1 = competitors[1]["team"]["abbreviation"]

            if abbr0 != TEAM_ABBR and abbr1 != TEAM_ABBR:
                continue

            status_type = comp.get("status", {}).get("type", {})
            state = status_type.get("state")

            if state != "pre":
                continue

            rockets_is_0 = (abbr0 == TEAM_ABBR)

            rockets = competitors[0] if rockets_is_0 else competitors[1]
            opp = competitors[1] if rockets_is_0 else competitors[0]

            opp_abbr = opp["team"]["abbreviation"]

            homeaway = rockets.get("homeAway")

            matchup = (
                f"{TEAM_ABBR} vs {opp_abbr}"
                if homeaway == "home"
                else f"{TEAM_ABBR} @ {opp_abbr}"
            )

            iso = comp.get("date") or ev.get("date")

            dt = pd.to_datetime(iso, errors="coerce")

            if pd.isna(dt):
                continue

            try:
                if dt.tzinfo is None:
                    dt = dt.tz_localize("UTC")

                dt_local = dt.tz_convert("America/Los_Angeles")

                when = dt_local.strftime("%b %d, %Y %I:%M %p PT")

            except Exception:

                when = dt.strftime("%b %d, %Y %I:%M %p")

            candidate = f"{when} — {matchup}"

            if best_dt is None or dt < best_dt:
                best_dt = dt
                best_str = candidate

        d += timedelta(days=1)

    return best_str
