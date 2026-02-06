from load_data import load_team_games
from team_stats import preprocess_games, season_summary
from trends import add_rolling_averages
from gui import RocketsApp

//launches program and gui

def main():
    df = load_team_games(season="2025-26")
    df = preprocess_games(df)
    df = add_rolling_averages(df, window=5)

    summary = season_summary(df)

    app = RocketsApp(summary, df)
    app.mainloop()


if __name__ == "__main__":
    main()
