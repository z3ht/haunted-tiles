from enum import Enum
import random
import numpy as np


class Side(str, Enum):
    HOME = 'home',
    AWAY = 'away'


class Strategy:

    def __init__(self, side):
        self.side = side
        self.game_state = None

        if self.side is None:
            raise ValueError("Incorrect side value provided")

    def update(self, game_state):
        self.game_state = game_state

    def move(self):
        pass

    def display(self):
        pass


class Basic(Strategy):

    def __init__(self, side):
        super().__init__(side)

    def update(self, game_state):
        pass

    def move(self):
        return ['west', 'none', 'south']


class Still(Strategy):
    def __init__(self, side):
        super().__init__(side)

    def update(self, game_state):
        pass

    def move(self):
        return ['none', 'none', 'none']


class Random(Strategy):
    def __init__(self, side):
        super().__init__(side)

        self.actions = ['north', 'south', 'east', 'west', 'none']

    def update(self, game_state):
        self.game_state = game_state

    def move(self):
        while True:
            rand_actions = random.choices(self.actions, k=3)
            if self._is_valid_moves(rand_actions):
                break
        return rand_actions

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


class RandomAvoidDeath(Random):
    def __init__(self, side):
        super().__init__(side)

    def move(self):
        max_itr = 100
        itr = 0
        while True:
            actions = super().move()
            if self._is_valid_moves(actions) or itr > max_itr:
                break
            itr += 1
        return actions


class ModelGotoBestValid(Strategy):

    ACTIONS = ['north', 'south', 'east', 'west', 'none']

    def __init__(self, side, model, move_player_inds=None):
        super().__init__(side)

        if move_player_inds is None:
            move_player_inds = [0, 1, 2]

        self.move_player_inds = move_player_inds
        self.model = model

    def update(self, game_state):
        self.game_state = game_state

    def move(self):
        predictions, _state = self.model.predict(self.game_state)
        return [predictions[i] for i in self.move_player_inds]
