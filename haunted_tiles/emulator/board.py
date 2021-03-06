from enum import Enum


class BoardType(Enum):
    DEFAULT = [[3 for _ in range(7)] for j in range(7)],
    WAFFLE_TOWN = [
        [3, 3, 0, 3, 0, 3, 3],
        [3, 3, 3, 3, 3, 3, 3],
        [0, 3, 0, 3, 0, 3, 0],
        [3, 3, 3, 3, 3, 3, 3],
        [0, 3, 0, 3, 0, 3, 0],
        [3, 3, 3, 3, 3, 3, 3],
        [3, 3, 0, 3, 0, 3, 3]
    ],
    JEFF_BRIDGES = [
        [3, 3, 3, 3, 3, 3, 3],
        [3, 3, 3, 3, 3, 3, 3],
        [3, 0, 3, 3, 3, 0, 3],
        [0, 3, 3, 0, 3, 3, 0],
        [3, 0, 3, 3, 3, 0, 3],
        [3, 3, 3, 3, 3, 3, 3],
        [3, 3, 3, 3, 3, 3, 3]
    ],
    IN = [
        [3, 3, 3, 3, 3, 3, 3],
        [3, 3, 3, 3, 3, 3, 3],
        [3, 3, 0, 0, 0, 3, 3],
        [3, 3, 3, 0, 3, 3, 3],
        [3, 3, 0, 0, 0, 3, 3],
        [3, 3, 3, 3, 3, 3, 3],
        [3, 3, 3, 3, 3, 3, 3]
    ],
    HOURGLASS = [
        [3, 3, 3, 3, 3, 3, 3],
        [0, 3, 3, 3, 3, 3, 0],
        [0, 0, 3, 3, 3, 0, 0],
        [0, 0, 3, 0, 3, 0, 0],
        [0, 0, 3, 3, 3, 0, 0],
        [0, 3, 3, 3, 3, 3, 0],
        [3, 3, 3, 3, 3, 3, 3]
    ]


class Board:
    def __init__(self, board_type):

        self.board = board_type.value[0]
        self.home_start_locations = [(0, 0), (3, 0), (6, 0)]
        self.away_start_locations = [(0, 6), (3, 6), (6, 6)]
        self.board_size = (7, 7)
        self.broken_tiles = set()
        self.home_tile_damage = 0
        self.away_tile_damage = 0

    def damage_tiles(self, home_player_locations, away_player_locations):
        """
        :param home_player_locations: all player locations as a tuple (x, y)
        :param away_player_locations: iterable of all player locations
        """
        for x, y in home_player_locations:
            if not (0 <= y < len(self.board)):
                continue
            if not (0 <= x < len(self.board[y])):
                continue
            if self.board[y][x] > 0:
                self.board[y][x] -= 1
                self.home_tile_damage += 1
            if self.board[y][x] <= 0:
                self.broken_tiles.add((x, y))

        for x, y in away_player_locations:
            if not (0 <= y < len(self.board)):
                continue
            if not (0 <= x < len(self.board[y])):
                continue
            if self.board[y][x] > 0:
                self.board[y][x] -= 1
                self.away_tile_damage += 1
            if self.board[y][x] <= 0:
                self.broken_tiles.add((x, y))

    def get_broken_tiles(self):
        return self.broken_tiles

