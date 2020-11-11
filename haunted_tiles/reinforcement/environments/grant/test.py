from stable_baselines import deepq

from haunted_tiles.emulator.board import Board, BoardType
from haunted_tiles.emulator.game import Game, Winner
from haunted_tiles.reinforcement.environments.grant.environment import TestEnvironment
from haunted_tiles.strategies import Strategy, RandomAvoidDeath
import numpy as np

model = deepq.DQN.load("model1.zip")

class DQN(Strategy):
    ACTIONS = ['north', 'south', 'east', 'west', 'none']

    def __init__(self, game_state, side):
        super().__init__(game_state, side)
        self.model = model

    def update(self, game_state):
        self.game_state = game_state
        self.state = TestEnvironment._get_state(self.game_state)

    def _is_valid_moves(self, moves):
        locations = self.game_state[self.side]
        if len(moves) != 3:
            return False
        board = self.game_state['tileStatus'].board
        for move, location in zip(moves, locations):
            y = location[0]
            x = location[1]
            if move == 'north' and (y + 1) >= len(board):
                return False
            elif move == 'south' and (y - 1) < 0:
                return False
            elif move == 'east' and (x + 1) >= len(board[0]):
                return False
            elif move == 'west' and (x - 1) < 0:
                return False
        return True

    def _is_good_moves(self, moves):
        locations = self.game_state[self.side]
        if len(moves) != 3:
            return False
        board = self.game_state['tileStatus'].board
        for move, location in zip(moves, locations):
            y = location[0]
            x = location[1]
            alive = not location[2]
            if alive and move == 'north' and board[y+1][x] <= 1:
                return False
            elif alive and move == 'south' and board[y-1][x] <= 1:
                return False
            elif alive and move == 'east' and board[y][x+1] <= 1:
                return False
            elif alive and move == 'west' and board[y][x-1] <= 1:
                return False
            elif alive and move == 'none' and board[y][x] <= 1:
                return False
        return True

    def move(self):
        moves = ['none', 'none', 'none']

        # Try to make the highest reward valid and good move. If there are none, make the highest reward valid move
        for i in range(1, len(self.ACTIONS)*2):
            probs = self.model.action_probability(self.state)
            i_largest = np.sort(probs)[-(i%len(self.ACTIONS))]
            idx = np.where(probs == i_largest)[0][0]
            moves = ['none', self.ACTIONS[idx], 'none']
            if self._is_valid_moves(moves) and self._is_good_moves(moves):
                break
            elif self._is_valid_moves(moves) and i > len(self.ACTIONS):
                break
        return moves

wins = [0, 0]
n_trials = 1000
for _ in range(n_trials):
    board = Board(BoardType.DEFAULT)
    board.board = [[3 for _ in range(7)] for _ in range(7)]
    game = Game(board, DQN, RandomAvoidDeath, True)
    winner = game.play_game()
    if winner == Winner.HOME:
        wins[0] += 1
    else:
        wins[1] += 1

win_prob = [w/n_trials for w in wins]
print(f"DQN won {win_prob[0]*100}% \nRandomAvoidDeath won {win_prob[1]*100}%")