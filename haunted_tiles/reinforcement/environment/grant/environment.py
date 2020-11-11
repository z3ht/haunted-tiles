from gym import Env, spaces, register, make
import numpy as np
import random
from haunted_tiles.emulator.board import Board, BoardType
from haunted_tiles.emulator.game import Game, Winner
from haunted_tiles.strategies import Strategy, RandomAvoidDeath, Random
from stable_baselines import common, PPO2, deepq, ACER

class TestEnvironment(Env):

    ACTIONS = ['north', 'south', 'east', 'west', 'none']

    def __init__(self):
        self.board = Board(BoardType.DEFAULT)
        self.board.board = [[3 for _ in range(7)] for _ in range(7)]
        self.game = Game(self.board, Agent, RandomAvoidDeath, True)

        board_size = self.board.board_size

        # observe the whole board 0-3 are empty tiles with damage 4 is home player 5 is away player
        self.observation_space = spaces.Box(low=0, high=3, shape=(board_size[0], board_size[1]*2), dtype=np.uint8)

        # 5 possible actions at a given state
        self.action_space = spaces.Discrete(5)

        self.state = self._get_state(self.game.get_game_state(include_dead_state=True))
        print(self.state)

    @staticmethod
    def _get_state(game_state):
        board = game_state['tileStatus'].board
        home = [(player[0], player[1]) for player in game_state['home'] if not player[2]]
        away = [(player[0], player[1]) for player in game_state['away'] if not player[2]]
        result = []
        for i, row in enumerate(board):
            row_list = []
            row_list_players = [0 for _ in range(len(board))]
            for j, val in enumerate(row):
                if (i, j) in home:
                    row_list_players[j] = 1
                elif (i, j) in away:
                    row_list_players[j] = 2
                row_list.append(val)
            result.append(row_list + row_list_players)
        return np.array(result)

    def _give_reward(self, agent):
        if agent.is_dead:
            return -1
        else:
            return 1

    def _valid_move(self, move, location):
        x = location[1]
        y = location[0]
        if move == 'north' and (y + 1) >= len(self.board.board):
            return False
        elif move == 'south' and (y - 1) < 0:
            return False
        elif move == 'east' and (x + 1) >= len(self.board.board[0]):
            return False
        elif move == 'west' and (x - 1) < 0:
            return False
        return True

    def _invalid_location(self, move, location, invalid_locations):
        x = location[1]
        y = location[0]
        if move == 'north' and (y + 1, x) in invalid_locations:
            return True
        elif move == 'south' and (y - 1, x) in invalid_locations:
            return True
        elif move == 'east' and (y, x + 1) in invalid_locations:
            return True
        elif move == 'west' and (y, x - 1) in invalid_locations:
            return True
        return False

    def step(self, action):
        direction = self.ACTIONS[action]
        agent = self.game.home_players[1]

        other_player_locations = [p for p in self.game.home_players if p != agent]
        other_player_locations += [p for p in self.game.away_players]

        episode_over = False
        if agent.is_dead:
            episode_over = True

        # if invalid move or agent is already dead, give no reward
        if not self._valid_move(direction, agent.get_location()) \
           or self._invalid_location(direction, agent.get_location(), other_player_locations) \
           or agent.is_dead:
            return self.state, 0, episode_over, {}

        # move players according to action
        self.game.move_players()
        self.game.home_players[1].move(direction)
        self.game.update_board()
        self.game.update_dead()
        agent = self.game.home_players[1]
        self.state = self._get_state(self.game.get_game_state(include_dead_state=True))

        # give reward according to new state and agent location
        reward = self._give_reward(agent)

        return self.state, reward, episode_over, {'reward': reward}

    def reset(self):
        self.board = Board(BoardType.DEFAULT)
        self.board.board = [[3 for _ in range(7)] for _ in range(7)]
        self.game = Game(self.board, Agent, RandomAvoidDeath, True)
        self.state = self._get_state(self.game.get_game_state(include_dead_state=True))
        return self.state

    def render(self, mode='human', close=False):
        print(self.state)

class Agent(Strategy):
    def __init__(self, game_state, side):
        super().__init__(game_state, side)

    def update(self, game_state):
        pass

    def move(self):
        """
        :return: Array of none values. Values for the agent will be updated in the step function of the environment
        """
        return ['none', 'none', 'none']

# env = TestEnvironment()


# model = deepq.DQN(deepq.policies.MlpPolicy, env, verbose=2)
# model.learn(total_timesteps=5000)
# model.save("model1")