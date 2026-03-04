import requests
import pandas as pd

URL = "https://site.web.api.espn.com/apis/v2/sports/basketball/nba/standings"


def load_nba_standings():
    r = requests.get(URL, timeout=10)
    r.raise_for_status()
    data = r.json()

    east_rows = []
    west_rows = []

    for conf in data.get("children", []):
        conf_name = conf.get("name", "")

        entries = conf.get("standings", {}).get("entries", [])

        for entry in entries:
            team = entry.get("team", {})
            team_name = team.get("displayName") or team.get("shortDisplayName") or "Team"

            stats_list = entry.get("stats", [])

            # map stat name -> dict with both value and displayValue
            stats = {}
            for s in stats_list:
                name = s.get("name")
                if name:
                    stats[name] = {
                        "value": s.get("value"),
                        "displayValue": s.get("displayValue")
                    }

            w = int((stats.get("wins", {}).get("value") or 0))
            l = int((stats.get("losses", {}).get("value") or 0))
            pct = float((stats.get("winPercent", {}).get("value") or 0))

            # try to use ESPN displayValue first (often correct)
            gb = stats.get("gamesBack", {}).get("displayValue")
            if gb is None:
                gb = stats.get("gamesBack", {}).get("value")

            strk = stats.get("streak", {}).get("displayValue")
            if strk is None:
                strk = stats.get("streak", {}).get("value")
            if strk is None:
                strk = ""

            row = {
                "Team": team_name,
                "W": w,
                "L": l,
                "PCT": pct,
                "GB": gb if gb is not None else "",
                "STRK": strk
            }

            if "Eastern" in conf_name:
                east_rows.append(row)
            else:
                west_rows.append(row)

    east = pd.DataFrame(east_rows)
    west = pd.DataFrame(west_rows)

    # If ESPN's GB came back blank/zero-y, compute GB from conference leader
    def compute_gb(df):
        if df.empty:
            return df

        df = df.copy()
        df["PCT"] = pd.to_numeric(df["PCT"], errors="coerce").fillna(0.0)

        df = df.sort_values("PCT", ascending=False).reset_index(drop=True)

        leader_w = int(df.loc[0, "W"])
        leader_l = int(df.loc[0, "L"])

        def gb_calc(w, l):
            # standard GB formula
            return ((leader_w - w) + (l - leader_l)) / 2

        # overwrite GB with computed values (more reliable)
        df["GB"] = df.apply(lambda r: gb_calc(int(r["W"]), int(r["L"])), axis=1)
        df["GB"] = df["GB"].map(lambda x: f"{x:.1f}" if x != 0 else "0.0")

        # assign Seed based on conference order
        df.insert(0, "Seed", [i + 1 for i in range(len(df))])

        return df

    east = compute_gb(east)
    west = compute_gb(west)

    return east, west
