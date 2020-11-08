
class Board:
    def __init__(self, board_type):
        self._board_types = {'basic': [[3 for i in range(7)] for j in range(7)]}
        self._starting_locations = {'basic': {'home': [(0, 0), (0, 3), (0, 6)], 'away': [(6, 0), (6, 3), (6, 6)]}}
        self._board_sizes = {'basic': (7, 7)}

        self.board = self._board_types[board_type]
        self.home_start_locations = self._starting_locations[board_type]
        self.away_start_locations = self._starting_locations[board_type]
        self.board_size = self._board_sizes[board_type]
        self.broken_tiles = set()

    def update_board(self, player_locations):
        """
        :param player_locations: iterable of all player locations
        """
        for y, x in player_locations:
            if self.board[y][x] > 0:
                self.board[y][x] -= 1
            if self.board[y][x] <= 0:
                self.broken_tiles.add((x, y))
