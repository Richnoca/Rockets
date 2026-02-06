# Houston Rockets Performance Tracker

![Python](https://img.shields.io/badge/Python-3.13-blue)
![NBA](https://img.shields.io/badge/NBA-Stats-green)

---

## Overview
This Python program tracks the **Houston Rockets' performance** in the NBA.  
It fetches official game data, analyzes team trends, and displays results in a GUI.

The program focuses is to generate an in depth tracker of player stats and team stats throughout the year as the season progresses.

---

# List of upcoming features.

- Player stats and game by game analysis
- defensive metrics that show opponent scoring
- projection model for upcoming matchups?
- Home vs Away stats
- Rolling average options aside from just 5 games (10 / 15 games)
- Data range selector (choose between specific dates)
- GUI improvements
- Win/Loss trends
- Point differential
- season highlights for players/teams

---

## Features

- Fetches real NBA game data using [`nba_api`](https://github.com/swar/nba_api)
- Filters games starting from **October 21, 2025**
- Computes team-level statistics:
  - Games played
  - Wins and losses
  - Average points scored
  - Win percentage
- Displays results in a **Tkinter GUI**
- Shows scoring trends using rolling averages
- Modular design for easy future expansion

---

## Dependancies Used

- **Python 3**
- [`nba_api`](https://github.com/swar/nba_api) – NBA stats API
- [`pandas`](https://pandas.pydata.org/) – Data analysis
- [`matplotlib`](https://matplotlib.org/) – Visualizations
- [`tkinter`](https://docs.python.org/3/library/tkinter.html) – GUI

---


---

## How It Works

1. **Data Collection**  
   Retrieves Houston Rockets game logs for the 2025–26 NBA season using `nba_api`.

2. **Preprocessing**  
   - Converts game dates to a usable format.  
   - Filters games on or after the season starte date of **October 21, 2025**.  
   - Identifies wins, losses, and home games.

3. **Statistical Analysis**  
   - Computes season statistics like win percentage and average points scored.  
   - Calculates rolling averages to show scoring trends.

4. **GUI Display**  
   - Summary statistics are shown in a graphical window.  
   - A **“Show Scoring Trend”** button opens a line graph of points scored per game with a 5-game rolling average.

---

## Installation & Running

### 1. Install Dependencies
```bash
pip install nba_api pandas matplotlib

