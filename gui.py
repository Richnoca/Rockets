import tkinter as tk
from tkinter import ttk
from visualize import plot_scoring_trend


class RocketsApp(tk.Tk):
    def __init__(self, summary, df):
        super().__init__()

        self.title("Houston Rockets Performance Tracker")
        self.geometry("600x300")

        title = ttk.Label(
            self,
            text="Houston Rockets Stats in the 2025-2026 season",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=10)

        frame = ttk.Frame(self)
        frame.pack(pady=10)

        for key, value in summary.items():
            row = ttk.Frame(frame)
            row.pack(fill="x", pady=2)

            ttk.Label(row, text=f"{key}:", width=20).pack(side="left")
            ttk.Label(row, text=str(value)).pack(side="left")

        plot_button = ttk.Button(
            self,
            text="Show Scoring Trend",
            command=lambda: plot_scoring_trend(df)
        )
        plot_button.pack(pady=15)
