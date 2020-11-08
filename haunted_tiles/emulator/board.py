class Board:
    def __init__(self, board_type):
        self._board_types = {
            'default': [[3 for i in range(7)] for j in range(7)],
            'waffle_town': None,
            'jeff_bridges': None,
            'i(n)': None,
            'hourglass': None
        }

        self.board = self._board_types[board_type]
        self.home_start_locations = [(0, 0), (0, 3), (0, 6)]
        self.away_start_locations = [(6, 0), (6, 3), (6, 6)]
        self.board_size = (7, 7)
        self.broken_tiles = set()

    def update_board(self, player_locations):
        """
        :param player_locations: all player locations as a tuple (x, y)
        :param player_locations: iterable of all player locations
        """
        for y, x in player_locations:
            if self.board[y][x] > 0:
                self.board[y][x] -= 1
            if self.board[y][x] <= 0:
                self.broken_tiles.add((x, y))

    def get_broken_tiles(self):
        return self.broken_tiles
