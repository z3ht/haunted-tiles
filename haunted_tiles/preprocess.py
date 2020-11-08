import json

def format_game_state(game_state):
    return None


def format_side(side):
    side = json.loads(side)
    return side.lower()
