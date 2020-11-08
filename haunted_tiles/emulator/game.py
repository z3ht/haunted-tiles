from haunted_tiles.emulator.board import Board
from haunted_tiles.emulator.player import Player
from haunted_tiles.strategies import Strategy
from enum import Enum


class Winner(str, Enum):
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

    def play_game(self):
        """
        Run game loop and get winner
        :return: game winner enum
        """
        while self.get_winner() is Winner.NONE:
            self.move_players()
            self.update_board()
            self.update_dead()
        return self.get_winner()

    def move_players(self):
        """
        Get moves of players and move players
        """
        self.home_strategy.update(self.get_game_state())
        self.away_strategy.update(self.get_game_state())
        home_1_move, home_2_move, home_3_move = self.home_strategy.move()
        away_1_move, away_2_move, away_3_move = self.away_strategy.move()
        self.home_players[0].move(*home_1_move)
        self.home_players[1].move(*home_2_move)
        self.home_players[2].move(*home_3_move)
        self.away_players[0].move(*away_1_move)
        self.away_players[1].move(*away_2_move)
        self.away_players[2].move(*away_3_move)


    def update_board(self):
        """
        Reduce tile health where players are
        """
        home_locations = [plyr.get_location for plyr in self.home_players]
        away_locations = [plyr.get_location for plyr in self.away_players]
        all_locations = home_locations + away_locations
        self.board.update_board(all_locations)

    def update_dead(self):
        """
        If players are in a position that results in death set the player to dead
        """
        broken_tiles = self.board.broken_tiles
        for home, away in zip(self.home_players, self.away_players):
            # check if either on broken tiles they are dead
            if home.get_location() in broken_tiles:
                home.is_dead = True
            if away.get_location() in broken_tiles:
                away.is_dead = True
            # if home player not on board they are dead
            if home.get_location()[0] not in range(self.board.board_size[0]):
                home.is_dead = True
            if home.get_location()[1] not in range(self.board.board_size[1]):
                home.is_dead = True
            # if away player not on board they are dead
            if away.get_location()[0] not in range(self.board.board_size[0]):
                away.is_dead = True
            if away.get_location()[1] not in range(self.board.board_size[1]):
                away.is_dead = True


    def get_winner(self):
        """
        Check if all players on either team have walked died
        :return: winner enum
        """
        home_lost = all([home.is_dead for home in self.home_players])
        away_lost = all([away.is_dead for away in self.away_players])

        if home_lost and away_lost:
            return Winner.TIE
        if home_lost:
            return Winner.AWAY
        if away_lost:
            return Winner.HOME
        else:
            return Winner.NONE

    def get_game_state(self, include_dead_state=False):
        """
        :param include_dead_state: include dead players and status in return or exclude dead players
        :return: same format as described in preprocessing.format_game_state
        """
        if not include_dead_state:
            return {'tileStatus': self.board,
                    'home': [plyr.get_location() for plyr in self.home_players if not plyr.is_dead],
                    'away': [plyr.get_location() for plyr in self.away_players if not plyr.is_dead],
                    'boardSize': self.board.board_size}
        else:
            return {'tileStatus': self.board,
                    'home': [[*plyr.get_location(), plyr.is_dead] for plyr in self.home_players],
                    'away': [[*plyr.get_location(), plyr.is_dead] for plyr in self.away_players],
                    'boardSize': self.board.board_size}
