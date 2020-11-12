from haunted_tiles.strategies import Strategy

import numpy as np


class Agent:

    def __init__(self, side, controlled_player_inds):
        self.side = side
        self.controlled_player_inds = controlled_player_inds

    @staticmethod
    def _valid_move(board, new_location):
        for i in [0, 1]:
            if len(board.board_size[i]) <= new_location[i] < 0:
                return False
        return True


class ReinforcementAgent(Agent):

    ACTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0), (0, 0)]

    def __init__(self, side, controlled_player_inds, action_space):
        super().__init__(side, controlled_player_inds)

        self.action_space = action_space

    def interpret_game_state(self, game_state):
        board = game_state['tileStatus'].board

        # team positions for living players
        foe_side = "away" if self.side == "home" else "home"
        friend_positions = [(player[0], player[1]) for player in game_state[self.side] if not player[2]]
        foe_positions = [(player[0], player[1]) for player in game_state[foe_side] if not player[2]]

        obs = []
        for i, row in enumerate(board):
            obs_row = []
            for j, val in enumerate(row):
                if (i, j) in friend_positions:
                    obs_row.append(4)
                elif (i, j) in foe_positions:
                    obs_row.append(5)
                else:
                    obs_row.append(val)
            obs.append(obs_row)

        return np.array(obs)

    def calc_reward(self, game, action):
        return 0

    def game_end_reward(self, game):
        if game.get_winner().value == self.side:
            return 1000
        else:
            return -1000

    def format_action(self, raw_action):
        pass

    def _calc_action(self, raw_action):
        return self.ACTIONS[raw_action]

    @staticmethod
    def calc_location(cur_location, action):
        return tuple([cur_location[i] + action[i] for i in range(cur_location)])


class TeamReinforcementAgent(ReinforcementAgent):

    def __init__(self, side, controlled_player_inds, action_space):
        super().__init__(side, controlled_player_inds, action_space)

    def format_action(self, raw_action):
        actions = []
        while (cur_action := raw_action % 5) > 0:
            actions.append(self._calc_action(cur_action))
            raw_action //= 5

        actions_dict = {}
        for i, action in enumerate(actions):
            actions_dict[self.controlled_player_inds[i]] = action

        return actions_dict


class MonsterReinforcementAgent(ReinforcementAgent):

    def __init__(self, side, controlled_player_ind, action_space):
        super().__init__(side, [controlled_player_ind], action_space)

    def format_action(self, raw_action):
        return {
            self.controlled_player_inds[0]: self._calc_action(raw_action)
        }


class ProceduralAgent(Agent):

    def __init__(self, side, controlled_player_inds):
        super().__init__(side, controlled_player_inds)

    def calc_move(self, game_state):
        pass


class StrategyAgent(ProceduralAgent):

    def __init__(self, side, strategy):
        super().__init__(side, [0, 1, 2])

        if not isinstance(self.strategy, Strategy):
            raise ValueError("strategy must be an instance of the Strategy class")

        self.strategy = strategy

    def calc_move(self, game_state):
        self.strategy.update(game_state=game_state)

        moves = self.strategy.move()

        return {
            0: moves[0],
            1: moves[1],
            2: moves[2]
        }


# env = HauntedTilesEnvironment([Agent], Board(BoardType.DEFAULT))
#
# model = PPO('mlppolicy', env, verbose=2)
# model.learn(total_timesteps=4000)
#
# obs = env.reset()
# for i in range(1000):
#     action, _states = model.predict(obs)
#     obs, rewards, dones, _ = env.step(action)
#     if dones:
#         break
#     env.render()
