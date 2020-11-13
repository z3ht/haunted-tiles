from enum import Enum
import random
import numpy as np
from haunted_tiles.dijkstras import dijkstras
import pickle

from haunted_tiles.environment.mock import mock_obs, mock_format_actions


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
        board = self.game_state['tileStatus']
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


class RLModel(Strategy):

    ACTIONS = {
        (0, 1): 'north',
        (1, 0): 'east',
        (0, -1): 'south',
        (-1, 0): 'west',
        (0, 0): 'none'
    }

    def __init__(self, side, model_class, model_dir, checkpoint="checkpoint_1/checkpoint-1", move_player_inds=None):
        super().__init__(side)

        if move_player_inds is None:
            move_player_inds = [0, 1, 2]
        self.move_player_inds = move_player_inds

        infile = open(model_dir + "config.pkl", 'rb')
        self.config = pickle.load(infile)
        infile.close()

        self.rl_agents = self.config["env_config"]["rl_agents"]

        self.model = model_class(self.config)
        self.model.restore(model_dir + checkpoint)

        self.obs = None

    def update(self, game_state):
        self.game_state = game_state

        self.obs = mock_obs(self.rl_agents, game_state)

    def move(self):
        raw_actions = self.model.compute_actions(self.obs)
        actions = mock_format_actions(self.rl_agents, raw_actions)

        moves = ['none', 'none', 'none']
        for agent_name, action in actions.items():
            if self.rl_agents[agent_name].side != self.side:
                continue
            for player_ind in action:
                moves[player_ind] = self.ACTIONS[action[player_ind]]

        return moves


class Wanderer(Strategy):
    def __init__(self, side, survivor_index=0):
        super().__init__(side)
        self.actions = ['north', 'south', 'east', 'west', 'none']
        self.survivor_index = survivor_index

    def update(self, game_state):
        self.game_state = game_state
        board = game_state['tileStates']
        survivor_position = game_state[self.side][self.survivor_index][:2]

        longest_path = []
        # find the point that has the largest path to the player
        for y in range(len(self.game_state['tileStates'][:])):
            for x in range(len(self.game_state['tileStates'][0])):
                if self._is_valid_move((x, y)):
                    new_path = self.find_longest_path((x, y))
                    end_x, end_y = new_path[-1]
                if len(new_path) > len(longest_path) and abs(survivor_position[0] - end_x) + abs(survivor_position[1] - end_y) == 1:
                    longest_path = new_path
        return longest_path

    def move(self):
        return ['none', 'none', 'none']

    # find the longest path from a point to the player
    def find_longest_path(self, end_point):
        def find_longest_path(end_point, visited, path):
            visited.add(end_point)
            if end_point[0] == self.game_state[self.side][self.survivor_index][0] and\
               end_point[1] == self.game_state[self.side][self.survivor_index][1]:
                return path
            path.append(end_point)
            longest_path = []
            for direction in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                next_move = end_point[0] + direction[0], end_point[1] + direction[1]
                if self._is_valid_move(next_move) and next_move not in visited:
                    new_path = find_longest_path(next_move, visited, path.copy())
                    if len(new_path) > len(path):
                        longest_path = new_path
            if len(longest_path):
                return longest_path
            return path

        visited = set()
        return find_longest_path(end_point, visited, [])

    def _is_valid_move(self, move):

        x, y = move
        if 0 > x or x >= len(self.game_state['tileStates'][0]):
            return False
        if 0 > y or y >= len(self.game_state['tileStates'][:]):
            return False
        if self.game_state['tileStates'][y][x] <= 1:
            return False
        return True


wndr = Wanderer(side=Side.HOME)
state = {'tileStates': [[3 for i in range(7)] for j in range(7)],
                   'home': [[0, 0, True]]}

state['tileStates'][0][5] = 0
state['tileStates'][1][5] = 0
state['tileStates'][2][5] = 0
state['tileStates'][3][5] = 0
state['tileStates'][4][5] = 0
state['tileStates'][5][5] = 0
state['tileStates'][6][5] = 0

wndr.game_state = state

print(wndr.find_longest_path((6, 6)))

# print(wndr.update(state))
#
