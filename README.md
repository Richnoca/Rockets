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

- Player stats and game by game analysis :heavy_check_mark:
- projection model for upcoming matchups? :x:
- Home vs Away stats :x:
- Rolling average options aside from just 5 games (10 / 15 games) :heavy_check_mark:
- Data range selector (choose between specific dates) :x:
- GUI improvements :heavy_check_mark:
- Win/Loss trends :heavy_check_mark:
- season highlights for players/teams :x:
- Playoff probability model :x:

---

## Features

* Fetches real NBA data using **ESPN public NBA endpoints**
* Tracks **Houston Rockets games starting October 21, 2025**
* Computes team-level statistics:

  * Games played
  * Wins and losses
  * Average points scored
  * Win percentage
* Displays results in a **Tkinter GUI dashboard**
* Shows scoring trends using rolling averages
* Displays **completed Rockets games with scores**
* Allows opening **game highlight pages via ESPN**
* Displays **Houston Rockets player statistics**
* Displays **full NBA standings (Eastern & Western Conference)**
* Sortable tables for players and standings
* Dark mode GUI interface
* Modular design for easy future expansion

---

## Dependencies Used

* **Python 3**
* [`requests`](https://pypi.org/project/requests/) – HTTP requests to ESPN APIs
* [`pandas`](https://pandas.pydata.org/) – Data analysis and dataframes
* [`matplotlib`](https://matplotlib.org/) – Visualizations
* [`tkinter`](https://docs.python.org/3/library/tkinter.html) – Desktop GUI

---

## How It Works

### 1. Data Collection

The program retrieves live NBA data using ESPN's public API endpoints.
This includes:

* Rockets game results
* NBA standings
* Rockets player statistics

### 2. Preprocessing

Game data is cleaned and formatted using **pandas**:

* Game dates are converted into datetime format
* Games are filtered starting from **October 21, 2025**
* Wins and losses are determined from game scores
* Rolling scoring averages are calculated

### 3. Statistical Analysis

Season metrics are calculated including:

* Total games played
* Wins and losses
* Win percentage
* Average points per game
* 5-game rolling scoring averages

### 4. GUI Dashboard

The application launches a **multi-tab desktop interface** built with Tkinter.

Tabs include:

**Summary**

* Rockets season statistics
* Scoring trend visualization

**Games Played**

* Scrollable table of completed Rockets games
* Date, matchup, win/loss, and score
* Button to open **ESPN highlight pages**

**Players**

* Rockets roster statistics
* Points, rebounds, assists, shooting percentages
* Clickable column sorting

**Standings**

* Full NBA standings
* Eastern and Western conferences
* Seed, record, games behind, and streak

---

## Installation & Running

### 1. Install Dependencies

```bash
pip install pandas matplotlib requests
```

### 2. Run the Program

```bash
py main.py
```

The **Houston Rockets Analytics Dashboard** GUI will launch.


