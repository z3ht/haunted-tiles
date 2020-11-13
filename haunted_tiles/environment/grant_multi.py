from gym import Env, spaces, register, make
import numpy as np
from stable_baselines import deepq

from haunted_tiles.emulator.board import Board, BoardType
from haunted_tiles.emulator.game import Game, Winner
from haunted_tiles.strategies import RandomAvoidDeath
import itertools

class Multi(Env):

    def __init__(self, enemy_strategy=RandomAvoidDeath):
        self.board = Board(BoardType.DEFAULT)
        self.board.board = [[3 for _ in range(7)] for _ in range(7)]
        self.game = Game(self.board, home_strategy=None, away_strategy=None, return_dead=True)

        self.enemy_strategy = enemy_strategy("away")
        board_size = self.board.board_size

        # observe the whole board 0-3 are empty tiles with damage 4 is home player 5 is away player
        self.observation_space = spaces.Box(low=0, high=3, shape=(board_size[0], board_size[1]*2), dtype=np.uint8)

        self.ACTIONS = list(itertools.permutations(['north', 'south', 'east', 'west', 'none'], 3))
        # 5 possible actions at a given state
        self.action_space = spaces.Discrete(len(self.ACTIONS))

        self.enemy_strategy.update(self.game.get_game_state())
        self.state = self._get_state(self.game.get_game_state())
        print(self.state)


    @staticmethod
    def _get_state(game_state):
        board = game_state['tileStatus']
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

    # def _give_reward(self, agents):
    #     dead_count = 0
    #     for a in agents:
    #         if a.is_dead:
    #             dead_count += 1
    #     forward = (agents[0].y + agents[2].y)*1/14
    #     if dead_count == 3:
    #         return -10
    #     else:
    #         return 3-dead_count + forward

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
        directions = self.ACTIONS[action]
        enemy_directions = self.enemy_strategy.move()

        agents = self.game.home_players
        alive_agents_before = len([a for a in agents if not a.is_dead])

        dead_count = 0
        for agent in agents:
            if agent.is_dead:
                dead_count += 1

        if self.game.get_winner() != Winner.NONE:
            return self.state, 0, True, {}

        # if any agent makes an invalid move no one gets a reward
        for agent, direction in zip(agents, directions):
            other_players = [a for a in self.game.home_players if a != agent]
            other_players += [p for p in self.game.away_players]
            if not agent.is_dead and (not self._valid_move(direction, agent.get_location()) or self._invalid_location(direction, agent.get_location(), other_players)):
                return self.state, 0, False, {}

        # move players according to action
        for i, d in enumerate(directions):
            self.game.home_players[i].move(d)

        for i, d in enumerate(enemy_directions):
            self.game.away_players[i].move(d)

        self.game.update_board()
        self.game.update_dead()


        self.enemy_strategy.update(self.game.get_game_state())
        self.state = self._get_state(self.game.get_game_state())

        agents = self.game.home_players
        alive_agents_after = len([a for a in agents if not a.is_dead])
        d_alive_agents = (alive_agents_before - alive_agents_after) * 2

        # give reward according to new state and agent location
        if d_alive_agents == 0:
            reward = alive_agents_after
        else:
            reward = -d_alive_agents

        return self.state, reward, False, {'reward': reward}

    def reset(self):
        self.board = Board(BoardType.DEFAULT)
        self.board.board = [[3 for _ in range(7)] for _ in range(7)]
        self.game = Game(self.board,home_strategy=None, away_strategy=None, return_dead=True)
        self.enemy_strategy.update(self.game.get_game_state())
        self.state = self._get_state(self.game.get_game_state())
        return self.state

    def render(self, mode='human', close=False):
        print(self.state)

def simple_train(n_steps):
    env = Multi(RandomAvoidDeath)
    model = deepq.DQN(deepq.policies.MlpPolicy, env, verbose=2)
    model.learn(total_timesteps=n_steps, log_interval=200)
    model.save("models/multi1.zip")