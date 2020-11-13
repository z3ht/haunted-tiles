from haunted_tiles.strategies import RandomAvoidDeath, Wanderer
from haunted_tiles.emulator.game import Game
from haunted_tiles.emulator.board import Board, BoardType

wanderer = Wanderer(side='home')
rad = RandomAvoidDeath(side='away')
board = Board(BoardType.HOURGLASS)

game = Game(board, wanderer, rad)
game.play_game(verbose=True)


