from enum import Enum
import random
import copy
import pickle
import os

from ray.rllib.agents.ppo import ppo

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
        actions = []
        is_done = False
        for one in self.actions:
            for two in self.actions:
                for three in self.actions:
                    actions = [one, two, three]
                    if self._is_valid_moves(actions):
                        is_done = True
                        break
                if is_done:
                    break
            if is_done:
                break
        return actions

    def _is_valid_moves(self, moves):
        locations = self.game_state[self.side]
        if len(moves) != 3:
            return False
        board = self.game_state['tileStates']
        for move, location in zip(moves, locations):
            x = location[0]
            y = location[1]
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

    def _is_good_moves(self, moves):
        locations = self.game_state[self.side]
        if len(moves) != 3:
            return False
        board = copy.deepcopy(self.game_state['tileStates'])
        for move, location in zip(moves, locations):
            x = location[0]
            y = location[1]
            alive = not location[2]
            if alive and move == 'north' and board[y+1][x] <= 1:
                board[y+1][x] -= 1
                return False
            elif alive and move == 'south' and board[y-1][x] <= 1:
                board[y - 1][x] -= 1
                return False
            elif alive and move == 'east' and board[y][x+1] <= 1:
                board[y][x + 1] -= 1
                return False
            elif alive and move == 'west' and board[y][x-1] <= 1:
                board[y][x - 1] -= 1
                return False
            elif alive and move == 'none' and board[y][x] <= 1:
                board[y][x] -= 1
                return False
        return True

    def move(self):
        actions = []
        is_done = False
        for one in random.sample(self.actions, k=len(self.actions)):
            for two in random.sample(self.actions, k=len(self.actions)):
                for three in random.sample(self.actions, k=len(self.actions)):
                    actions = [one, two, three]
                    if self._is_valid_moves(actions) and self._is_good_moves(actions):
                        is_done = True
                        break
                if is_done:
                    break
            if is_done:
                break
        return actions


class Hourglass(Strategy):
    START_SEQUENCE = {'away': [['east', 'north', 'east', 'north', 'east', 'south'],
                               ['north', 'north', 'west', 'north', 'north', 'north'],
                               ['west', 'north', 'west', 'north', 'none', 'north']],
                      'home': [['east', 'south', 'east', 'south', 'east', 'north'],
                               ['south', 'south', 'west', 'south', 'south', 'south'],
                               ['west', 'south', 'west', 'south', 'none', 'south']]}

    SURVIVOR_PATH = {'away': ['east', 'east', 'south', 'west', 'west', 'west', 'north', 'west', 'south', 'west'],
                     'home': ['west', 'west', 'north', 'east', 'east', 'east', 'south', 'east', 'north', 'east']}

    def __init__(self, side):
        self.side = side
        self.finished_start_sequence = False
        self.start_sequence_initialized = False
        self.start_sequence_iter = None
        self.rad = RandomAvoidDeath(side)

    def update(self, game_state):
        self.rad.update(game_state)
        self.game_state = game_state
        if not self.start_sequence_initialized:
            self.start_sequence_iter = zip(self.START_SEQUENCE[self.side][0], self.START_SEQUENCE[self.side][1], self.START_SEQUENCE[self.side][2])
            self.start_sequence_initialized = True
            self.survivor_path_iter = None

    def move(self):
        if not self.finished_start_sequence:
            try:
                player1, player2, player3 = next(self.start_sequence_iter)
                return [player1, player2, player3]
            except:
                self.finished_start_sequence = True
                self.survivor_path_iter = iter(self.SURVIVOR_PATH[self.side])

        move = self.rad.move()
        return [self.get_survivor_move(), move[1], move[2]]

    def get_survivor_move(self):
        surv_x, surv_y = self.game_state[self.side][0][:2]
        survivor_move = 'none'
        if self.game_state['tileStates'][surv_y][surv_x] <= 1:
            try:
                survivor_move = next(self.survivor_path_iter)
            except:
                pass
        return survivor_move


class RLModel(Strategy):

    # Jank but might work.... we're running out of time here
    HOME_ACTIONS = {
        (0, 1): 'north',
        (1, 0): 'east',
        (0, -1): 'south',
        (-1, 0): 'west',
        (0, 0): 'none'
    }

    AWAY_ACTIONS = {
        (0, -1): 'north',
        (1, 0): 'east',
        (0, 1): 'south',
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

        if self.side == "away":
            self.game_state = self.game_state.reverse()

        self.obs = mock_obs(self.rl_agents, self.game_state)

    def move(self):
        raw_actions = self.model.compute_actions(self.obs)
        actions = mock_format_actions(self.rl_agents, raw_actions)

        moves = ['none', 'none', 'none']
        for agent_name, action in actions.items():
            if self.rl_agents[agent_name].side != self.side:
                continue
            for player_ind in action:
                moves[player_ind] = self.HOME_ACTIONS[action[player_ind]]

        return moves


class DeepMindV2(RLModel):

    def __init__(self, side):
        super().__init__(side=side, model_class=ppo.PPOTrainer, model_dir="./models/alpha/",
                         checkpoint="checkpoint_2/checkpoint-2")


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


# wndr = Wanderer(side=Side.HOME)
# state = {'tileStates': [[3 for i in range(7)] for j in range(7)],
#                    'home': [[0, 0, True]]}
#
# state['tileStates'][0][5] = 0
# state['tileStates'][1][5] = 0
# state['tileStates'][2][5] = 0
# state['tileStates'][3][5] = 0
# state['tileStates'][4][5] = 0
# state['tileStates'][5][5] = 0
# state['tileStates'][6][5] = 0
#
# wndr.game_state = state
#
# print(wndr.find_longest_path((6, 6)))
#
# # print(wndr.update(state))
# #
