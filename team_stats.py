import pandas as pd

START_DATE = pd.Timestamp("2025-10-21")


def preprocess_games(df):
    df = df.copy()

    df["GAME_DATE"] = pd.to_datetime(
        df["GAME_DATE"],
        format="%b %d, %Y"
    )

    # filter by start date
    df = df[df["GAME_DATE"] >= START_DATE]

    df["HOME"] = df["MATCHUP"].str.contains("vs").astype(int)
    df["WIN"] = (df["WL"] == "W").astype(int)

    return df


def season_summary(df):
    return {
        "Games Played": len(df),
        "Wins": int(df["WIN"].sum()),
        "Losses": int(len(df) - df["WIN"].sum()),
        "Avg Points Scored": f"{df['PTS'].mean():.2f}",
        "Win Percentage": f"{df['WIN'].mean() * 100:.2f}"
    }
