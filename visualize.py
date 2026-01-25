import matplotlib.pyplot as plt


def plot_scoring_trend(df):
    plt.figure()
    plt.plot(df["GAME_DATE"], df["PTS"], label="Points")
    plt.plot(df["GAME_DATE"], df["PTS_ROLL_5"], label="5-game avg")
    plt.xlabel("Date")
    plt.ylabel("Points Scored")
    plt.title("Houston Rockets Scoring Trend")
    plt.legend()
    plt.show()
