from gym import Env, spaces, register, make
import numpy as np
import random
from haunted_tiles.emulator.board import Board, BoardType
from haunted_tiles.emulator.game import Game, Winner
from haunted_tiles.strategies import Strategy, RandomAvoidDeath
from stable_baselines import common, PPO2

class TestEnvironment(Env):

    ACTIONS = ['north', 'south', 'east', 'west', 'none']

    def __init__(self):
        self.board = Board(BoardType.DEFAULT)
        self.board.board = [[3 for _ in range(7)] for _ in range(7)]
        self.game = Game(self.board, Agent, RandomAvoidDeath, True)

        board_size = self.board.board_size

        # observe the whole board 0-3 are empty tiles with damage 4 is home player 5 is away player
        self.observation_space = spaces.Box(low=0, high=6, shape=(board_size[0], board_size[1]), dtype=np.uint8)

        # 5 possible actions at a given state
        self.action_space = spaces.Discrete(5)
        self.state = self._get_action_space(self.game.get_game_state(include_dead_state=True))


    @staticmethod
    def _get_action_space(game_state):
        board = game_state['tileStatus'].board
        home = [(player[0], player[1]) for player in game_state['home'] if not player[2]]
        away = [(player[0], player[1]) for player in game_state['away'] if not player[2]]
        result = []
        for i, row in enumerate(board):
            row_list = []
            for j, val in enumerate(row):
                if (i, j) in home:
                    row_list.append(4)
                elif (i, j) in away:
                    row_list.append(5)
                else:
                    row_list.append(val)
            result.append(row_list)
        return np.array(result)

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


    def step(self, action):
        """

        Parameters
        ----------
        action :

        Returns
        -------
        ob, reward, episode_over, info : tuple
            ob (object) :
                an environment-specific object representing your observation of
                the environment.
            reward (float) :
                amount of reward achieved by the previous action. The scale
                varies between environments, but the goal is always to increase
                your total reward.
            episode_over (bool) :
                whether it's time to reset the environment again. Most (but not
                all) tasks are divided up into well-defined episodes, and done
                being True indicates the episode has terminated. (For example,
                perhaps the pole tipped too far, or you lost your last life.)
            info (dict) :
                 diagnostic information useful for debugging. It can sometimes
                 be useful for learning (for example, it might contain the raw
                 probabilities behind the environment's last state change).
                 However, official evaluations of your agent are not allowed to
                 use this for learning.
        """
        direction = self.ACTIONS[action]
        agent = self.game.home_players[1]

        episode_over = False
        if self.game.get_winner() is not Winner.NONE or agent.is_dead:
            print("reseting...")
            episode_over = True

        if not self._valid_move(direction, agent.get_location()):
            return self.state, 5, episode_over, {}

        # move players according to strategies
        self.game.move_players()
        # move agent according to supplied action
        self.game.home_players[1].move(direction)

        self.game.update_board()
        self.game.update_dead()
        self.state = self._get_action_space(self.game.get_game_state(include_dead_state=True))

        # self.status = self.env.step()
        # reward = self._get_reward()
        # ob = self.env.getState()
        # episode_over = self.status != hfo_py.IN_GAME
        # return ob, reward, episode_over, {}
        print(self.state)
        return self.state, 5, episode_over, {}

    def reset(self):
        self.board = Board(BoardType.DEFAULT)
        self.board.board = [[3 for _ in range(7)] for _ in range(7)]
        self.game = Game(self.board, Agent, RandomAvoidDeath, True)
        self.state = self._get_action_space(self.game.get_game_state(include_dead_state=True))
        return self.state

    def render(self, mode='human', close=False):
        print(self.state)

class Agent(Strategy):
    def __init__(self, game_state, side):
        super().__init__(game_state, side)
        self.action = 'none'

    def supply_action(self, action):
        self.action = action

    def update(self, game_state):
        pass

    def move(self):
        """
        :return: Array of none values. Values for the agent will be updated in the step function of the environment
        """
        return ['none', 'none', 'none']

env = TestEnvironment()

model = PPO2(common.policies.MlpPolicy, env, verbose=2)
model.learn(total_timesteps=4000)

obs = env.reset()
for i in range(1000):
    action, _states = model.predict(obs)
    obs, rewards, dones, _ = env.step(action)
    if dones:
        break
    env.render()

