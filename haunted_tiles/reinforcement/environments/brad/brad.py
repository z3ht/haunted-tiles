from gym import envs, spaces
import numpy as np
from haunted_tiles.emulator.game import Game, Winner
from haunted_tiles.dijkstras import dijkstras


class Brad(envs):
    ACTIONS = ['north', 'south', 'east', 'west', 'none']

    def __init__(self, game, board, board_type, agent, away_strategy, return_dead):
        self.board_type = board_type
        self.board = board
        self.agent = agent
        self.away_strategy = away_strategy
        self.return_dead = return_dead
        self.game = game(self.board, self.agent, self.away_strategy, self.return_dead)

        self.action_space = spaces.Discrete(125)
        self.observation_space = spaces.Box(low=0, high=np.inf, shape=(3, 7, 7), dtype=np.int16)
        self.current_episode = 0
        self.state = None

    def step(self, action):
        episode_over = False
        if self.game.get_winner() is not Winner.NONE:
            episode_over = True

        self.game.move_players()
        self.game.update_board()
        self.game.update_dead()

        self.state = self._update_state()
        reward = self._find_reward()

        return self.state, reward, episode_over, {}

    def _update_state(self):
        game_state = self.game.get_state()
        enemy_moves = [dijkstras(self.game.board, (y, x)) for y, x in game_state['away']]
        friendly_moves = [dijkstras(self.game.board, (y, x)) for y, x in game_state['home']]
        board = self.game.board
        return [board, enemy_moves, friendly_moves]

    def _find_reward(self):
        game_state = self.game.get_game_state()
        reward = 0
        reward += game_state['home'] - .5 * game_state['away']
        return reward

    def reset(self):
        self.board = self.board(self.board_type)
        self.game = self.game(self.board, self.agent, self.away_strategy, self.return_dead)

    def renderer(self):
        pass


def DQNAgent(Strategy):
    pass

