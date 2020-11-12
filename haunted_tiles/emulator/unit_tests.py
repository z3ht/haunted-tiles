from haunted_tiles.emulator.game import Game
from haunted_tiles.emulator.board import Board
from haunted_tiles.strategies import Strategy
from haunted_tiles.emulator.game import Winner
from haunted_tiles.strategies import Side
from haunted_tiles.emulator.board import BoardType


def get_basic_board():
    basic_board = Board(BoardType.DEFAULT)
    basic_board.board = [[0 for _ in range(7)] for _ in range(7)]
    basic_board.board[0][0] = 3
    basic_board.board[6][0] = 3

    for y in range(basic_board.board_size[0]):
        for x in range(basic_board.board_size[1]):
            if basic_board.board[y][x] == 0:
                basic_board.broken_tiles.add((x, y))

    return basic_board


class Forward(Strategy):
    def __init__(self, side):
        super().__init__(side)

    def update(self, game_state):
        super().update(game_state)

    def move(self):
        if self.side is Side.AWAY:
            return ['south', 'south', 'south']
        else:
            return ['north', 'north', 'north']


class Still(Strategy):
    def __init__(self, side):
        super().__init__(side)

    def update(self, game_state):
        super().update(game_state)

    def move(self):
        return ['none', 'none', 'none']


# # check that correct side wins
# basic_board = get_basic_board()
# game = Game(basic_board, Still(side="home"), Forward(side="away"))
# assert game.play_game() is Winner.HOME

basic_board = get_basic_board()
game = Game(basic_board, Still(side="home"), Still(side="away"))
assert game.play_game() is Winner.TIE

basic_board = get_basic_board()
game = Game(basic_board, Forward(side="away"), Still(side="home"))
assert game.play_game() is Winner.AWAY


# check win condition when both teams all die in the same turn with DIFFERENT number of tiles broken by each team
# TODO: does below mean team that has dealt the most damage to tiles or fully broken the most tiles
# A round is over when all three monsters on one team have fallen to their death. The team that has any number of
# monsters still alive wins the round.
basic_board = get_basic_board()
basic_board.board[0][3] = 3
basic_board.board[0][6] = 3
# the away team immediately loses 2 players
# the home team keeps all 3 players for 3 turns
# the away team keeps one player for 3 turns
game = Game(basic_board, Still(side="home"), Still(side="home"))
assert game.play_game() is Winner.HOME

basic_board = get_basic_board()
basic_board.board[6][3] = 3
basic_board.board[6][6] = 3
game = Game(basic_board, Still(side="home"), Still(side="home"))
assert game.play_game() is Winner.AWAY
print('All tests passed')


basic_board = Board(board_type=BoardType.DEFAULT)
game = Game(basic_board, Still(side='home'), Forward(side='away'), return_dead=True)

for i in range(3):
    game.move_player('home', 0, (0, 1))
    game.move_player('home', 1, (0, 1))
    game.move_player('home', 2, (0, 1))
    game.update_board()
    game.update_dead()
    print(game.get_game_state()['home'])
    if game.get_winner():
        print(game.get_winner())
        break



