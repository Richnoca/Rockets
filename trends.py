def add_rolling_averages(df, window=5):
    df = df.sort_values("GAME_DATE")
    df[f"PTS_ROLL_{window}"] = df["PTS"].rolling(window).mean()
    df[f"WIN_ROLL_{window}"] = df["WIN"].rolling(window).mean()
    return df
