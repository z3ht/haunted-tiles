from haunted_tiles.emulator.board import Board
from haunted_tiles.emulator.player import Player
from enum import Enum


class Winner(str, Enum):
    HOME = 'home'
    AWAY = 'away'
    TIE = 'tie'
    NONE = 'none'


class Game:

    def __init__(self, board, home_strategy, away_strategy, return_dead=False):
        """
        :param board: board object
        :param home_strategy: Strategy object for home team (default: call move manually)
        :param away_strategy: Strategy object for away team (default: call move manually)
        """
        if not isinstance(board, Board):
            raise TypeError(f'Expected board to be type Board. Got type: {type(board)}')

        self.board = board
        self.home_players = [Player(x, y) for x, y in board.home_start_locations]
        self.away_players = [Player(x, y) for x, y in board.away_start_locations]
        self.return_dead = return_dead
        self.home_strategy = home_strategy
        self.away_strategy = away_strategy

    def play_game(self, verbose=False):
        """
        Run game loop and get winner
        :return: game winner enum
        """
        while self.get_winner() is Winner.NONE:
            self.move_players()
            self.update_board()
            self.update_dead()
            if verbose:
                self.display_board()

        return self.get_winner()

    def move_players(self):
        """
        Get moves of players and move players
        """
        game_state = self.get_game_state()
        self.home_strategy.update(game_state=game_state)
        self.away_strategy.update(game_state=self.get_game_state())
        home_1_move, home_2_move, home_3_move = self.home_strategy.move()
        away_1_move, away_2_move, away_3_move = self.away_strategy.move()
        self.home_players[0].move(home_1_move)
        self.home_players[1].move(home_2_move)
        self.home_players[2].move(home_3_move)
        self.away_players[0].move(away_1_move)
        self.away_players[1].move(away_2_move)
        self.away_players[2].move(away_3_move)

    def update_board(self):
        """
        Reduce tile health where players are
        """
        home_locations = [plyr.get_location() for plyr in self.home_players]
        away_locations = [plyr.get_location() for plyr in self.away_players]
        self.board.damage_tiles(home_locations, away_locations)

    def update_dead(self):
        """
        If players are in a position that results in death set the player to dead
        """
        broken_tiles = self.board.broken_tiles
        for player in self.home_players + self.away_players:
            # check if either on broken tiles they are dead
            if player.get_location() in broken_tiles:
                player.is_dead = True
            # if home player not on board they are dead
            # if away player not on board they are dead
            if 0 > player.get_location()[0] or player.get_location()[0] >= self.board.board_size[1]:
                player.is_dead = True
            if 0 > player.get_location()[1] or player.get_location()[1] >= self.board.board_size[0]:
                player.is_dead = True

    def get_winner(self):
        """
        Check if all players on either team have walked died
        :return: winner enum
        """
        home_lost = all([home.is_dead for home in self.home_players])
        away_lost = all([away.is_dead for away in self.away_players])
        # ties only occur if teams have broken the same number of tiles
        # TODO refactor to win based on most BROKEN tiles
        if home_lost and away_lost:
            if self.board.home_tile_damage > self.board.away_tile_damage:
                return Winner.HOME
            elif self.board.home_tile_damage < self.board.away_tile_damage:
                return Winner.AWAY
            else:
                return Winner.TIE
        if home_lost:
            return Winner.AWAY
        if away_lost:
            return Winner.HOME
        else:
            return Winner.NONE

    def move_player(self, side, player_index, direction):
        """
        This method moves the desired monster to a new location if that location is valid

        AFTER MOVING ALL PLAYERS THE BOARD MUST BE UPDATED WITH update_board() and update_dead(). This step must happen
        after ALL players move.

        Params
        ======
        :param side: string indicating the team the player(monster) is on
        :param player_index: what player should be moved (0 - 2 inclusive)
        :param location: tuple of new player location

        Returns
        =======
        :return: None
        """

        if side == 'home':
            self.home_players[player_index].move(direction)
        elif side == 'away':
            self.away_players[player_index].move(direction)
        else:
            raise ValueError('Unrecognized side: away / home')

    def get_game_state(self):
        """
        :return: same format as described in preprocessing.format_game_state
        """
        if not self.return_dead:
            return {'tileStatus': self.board.board,
                    'home': [plyr.get_location() for plyr in self.home_players if not plyr.is_dead],
                    'away': [plyr.get_location() for plyr in self.away_players if not plyr.is_dead],
                    'boardSize': self.board.board_size}
        else:
            return {'tileStatus': self.board.board,
                    'home': [[*plyr.get_location(), plyr.is_dead] for plyr in self.home_players],
                    'away': [[*plyr.get_location(), plyr.is_dead] for plyr in self.away_players],
                    'boardSize': self.board.board_size}

    def display_board(self):
        game_state = self.get_game_state()
        board = game_state["tileStatus"]

        # team positions for living players
        home_positions = []
        for player in game_state["home"]:
            if player[2]:
                home_positions.append(None)
            else:
                home_positions.append((player[0], player[1]))

        away_positions = [(player[0], player[1]) for player in game_state["away"] if not player[2]]

        obs = []
        for y in range(len(board)):
            health_row = []
            location_row = []
            for x in range(len(board[y])):
                health_data = board[y][x]
                location_data = 0

                if (x, y) == home_positions[0]:
                    location_data = 1
                elif (x, y) in home_positions:
                    location_data = 2
                elif (x, y) in away_positions:
                    location_data = 3

                health_row.append(health_data)
                location_row.append(location_data)

            obs.append(health_row + location_row)
        for row in obs:
            print(row)
        print("-------")
