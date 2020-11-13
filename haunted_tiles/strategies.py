from enum import Enum
import random
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

        return actions
