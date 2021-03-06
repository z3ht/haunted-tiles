import json


def format_game_state(game_state, include_dead_state=False):
    """
    :param game_state: gamestate json string data
    :param include_dead_state: if True then the formatted gamestate will include a boolean value to indicate if that
            player is dead as the third value of the player position list
    :return: dictionary with keys : tileStates - array in the shape of the game board, number for hp of each tile 3 = full hp, 0 = broken
                                    home - list of all three players on the home team [[x, y, is_dead], ...]
                                    away - list of all three players on away team [[x, y, is_dead], ...]
                                    boardSize - [h, w]
    """
    game_state = json.loads(game_state)
    if not include_dead_state:
        return {'tileStates': game_state['tileStates'],
                'home': [plyr['coord'] for plyr in game_state['teamStates']['home'] if not plyr['isDead']],
                'away': [plyr['coord'] for plyr in game_state['teamStates']['away'] if not plyr['isDead']],
                'boardSize': game_state['boardSize']}

    else:
        return {'tileStates': game_state['tilestates'],
                'home': [[*plyr['coord'], plyr['isdead']] for plyr in game_state['teamstates']['home']],
                'away': [[*plyr['coord'], plyr['isdead']] for plyr in game_state['teamstates']['away']],
                'boardSize': game_state['boardsize']}


def format_string(side):
    side = json.loads(side)
    return side.lower()
