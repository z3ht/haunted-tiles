from haunted_tiles.strategies import RandomAvoidDeath, Hourglass
from haunted_tiles.emulator.game import Game
from haunted_tiles.emulator.board import Board, BoardType

hrgls = Hourglass('home')
rad = RandomAvoidDeath('away')
board = Board(BoardType.HOURGLASS)
game = Game(board, hrgls, rad, True)

j = 0
while not all([i.is_dead for i in game.home_players]):
    game.move_players()
    game.update_board()
    game.update_dead()
    print([i.get_location() for i in game.home_players])
    j += 1
    print(j)

print(j)
#
#
# hrgls = Hourglass('away')
# rad = RandomAvoidDeath('home')
# board = Board(BoardType.HOURGLASS)
# game = Game(board, rad, hrgls, True)
#
# j = 0
# while not all([i.is_dead for i in game.away_players]):
#     game.move_players()
#     game.update_board()
#     game.update_dead()
#     j += 1
#     print(j)
#
# print(j)
#
#


