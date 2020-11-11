from enum import Enum
import random


class Side(str, Enum):
    HOME = 'home',
    AWAY = 'away'


class Strategy:

    def __init__(self, game_state, side):
        self.game_state = game_state
        self.side = side

        if self.side is None:
            raise ValueError("Incorrect side value provided")

    def update(self, game_state):
        self.game_state = game_state

    def move(self):
        pass

    def display(self):
        pass


class Basic(Strategy):

    def __init__(self, game_state, side):
        super().__init__(game_state, side)

    def update(self, game_state):
        pass

    def move(self):
        return ['north', 'none', 'south']


class Random(Strategy):
    def __init__(self, game_state, side):
        super().__init__(game_state, side)
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
    def __init__(self, game_state, side):
        super().__init__(game_state, side)

    def move(self):
        max_itr = 100
        itr = 0
        while True:
            actions = super().move()
            if self._is_good_moves(actions) or itr > max_itr:
                break
            itr += 1
        return actions

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


class Agent(Strategy):

    def __init__(self, game_state, agent, side):
        super().__init__(game_state, side)

        self.agent = agent

    def update(self, game_state):
        super().update(game_state)

    def move(self):
        self.agent.predict(self.game_state)

    def display(self):
        pass


class LoadModel(Strategy):
    
    def __init__(self, game_state, model, side):
        super().__init__(game_state, side)

        self.model = model

    def update(self, game_state):
        super().update(game_state)

    def move(self):
        pass

    def display(self):
        pass
