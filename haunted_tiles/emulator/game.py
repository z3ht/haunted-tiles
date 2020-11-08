from haunted_tiles.emulator.board import Board
from haunted_tiles.emulator.player import Player
from haunted_tiles.strategies import Strategy
from enum import Enum


class State(str, Enum):
    HOME = 'home'
    AWAY = 'away'
    TIE = 'tie'
    NONE = 'none'


class Game:
    def __init__(self, board, home_strategy, away_strategy):
        """
        :param board: board object
        :param home_strategy: Strategy object for home team
        :param away_strategy: Strategy object for away team
        """
        if not isinstance(board, Board):
            raise TypeError(f'Expected board to be type Board. Got type: {type(board)}')

        if not isinstance(home_strategy, Strategy):
            raise TypeError(f'Expected home_strategy to be type Strategy. Got type: {type(home_strategy)}')

        if not isinstance(away_strategy, Strategy):
            raise TypeError(f'Expected away_strategy to be type Strategy. Got type: {type(away_strategy)}')

        self.board = board
        self.home_strategy = home_strategy
        self.away_strategy = away_strategy
        self.home_players = [Player(y, x) for y, x in board.home_start_locations]
        self.away_players = [Player(y, x) for y, x in board.away_start_locations]

    def get_game_state(self, include_dead_state=False):
        """
        :param include_dead_state: include dead players and status in return or exclude dead players
        :return: same format as described in preprocessing.format_game_state
        """
        if not include_dead_state:
            return {'tileStatus' : self.board,
                    'home': [plyr.get_location() for plyr in self.home_players if not plyr.is_dead],
                    'away': [plyr.get_location() for plyr in self.away_players if not plyr.is_dead],
                    'boardSize': self.board.board_size}
        else:
            return {'tileStatus': self.board,
                    'home': [[*plyr.get_location(), plyr.is_dead] for plyr in self.home_players],
                    'away': [[*plyr.get_location(), plyr.is_dead] for plyr in self.away_players],
                    'boardSize': self.board.board_size}

    def take_turn(self):
        # move all players and update board
        self.home_strategy.update(self.get_game_state())
        self.away_strategy.update(self.get_game_state())
        # TODO get moves from strategies, update players, update board

    def play_game(self):
        pass
        # TODO implement, game loops calling take turn, update_dead, and get_winner until there is a winner

    def update_dead(self):
        broken_tiles = self.board.get_broken_tiles()
        for home, away in zip(self.home_players, self.away_players):
            if home.get_location() in broken_tiles:
                home.is_dead = True
            if away.get_location() in broken_tiles:
                away.is_dead = True

    def get_winner(self):
        home_lost = all([home.is_dead for home in self.home_players])
        away_lost = all([away.is_dead for away in self.away_players])

        if home_lost and away_lost:
            return State.TIE
        if home_lost:
            return State.AWAY
        if away_lost:
            return State.HOME
        else:
            return State.NONE
