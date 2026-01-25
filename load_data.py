from nba_api.stats.endpoints import teamgamelog
from nba_api.stats.static import teams
import pandas as pd


def get_rockets_team_id():
    nba_teams = teams.get_teams()
    for team in nba_teams:
        if team["full_name"] == "Houston Rockets":
            return team["id"]
    return None


def load_team_games(season="2023-24"):
    team_id = get_rockets_team_id()
    gamelog = teamgamelog.TeamGameLog(
        team_id=team_id,
        season=season
    )
    df = gamelog.get_data_frames()[0]
    return df


if __name__ == "__main__":
    df = load_team_games()
    print(df.head())
