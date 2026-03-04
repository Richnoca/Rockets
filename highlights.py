import webbrowser

def open_game_highlights(event_id: str):
    # ESPN game page (usually has recap/video/highlights)
    url = f"https://www.espn.com/nba/game/_/gameId/{event_id}"
    webbrowser.open(url)
