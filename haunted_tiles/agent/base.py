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

    # x, y
    ACTIONS = [(0, 1), (1, 0), (-1, 0), (-1, 0), (0, 0)]

    def __init__(self, name, side, controlled_player_inds):
        super().__init__(side, controlled_player_inds)

        self.name = name

    def interpret_game_state(self, game_state):
        board = game_state['tileStatus'].board

        # team positions for living players
        foe_side = "away" if self.side == "home" else "home"
        friend_positions = [(player[0], player[1]) for player in game_state[self.side] if not player[2]]
        foe_positions = [(player[0], player[1]) for player in game_state[foe_side] if not player[2]]

        obs = []
        for y in range(len(board)):
            obs_row = []
            for x in range(len(board[y])):
                if (x, y) in friend_positions:
                    obs_row.append(4)
                elif (x, y) in foe_positions:
                    obs_row.append(5)
                else:
                    val = board[y][x]
                    obs_row.append(val)
            obs.append(obs_row)

        return obs

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
        return tuple([cur_location[i] + action[i] for i in range(len(cur_location))])


class TeamReinforcementAgent(ReinforcementAgent):

    def __init__(self, name, side, controlled_player_inds):
        super().__init__(name, side, controlled_player_inds)

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

    def __init__(self, name, side, controlled_player_ind):
        super().__init__(name, side, [controlled_player_ind])

    def format_action(self, raw_action):
        return {
            self.controlled_player_inds[0]: self._calc_action(raw_action)
        }


class ProceduralAgent(Agent):

    def __init__(self, side, controlled_player_inds):
        super().__init__(side, controlled_player_inds)

    def calc_moves(self, game_state):
        pass


class StrategyAgent(ProceduralAgent):

    def __init__(self, side, strategy, controlled_player_inds=None):
        if controlled_player_inds is None:
            controlled_player_inds = [0, 1, 2]

        super().__init__(side, controlled_player_inds)

        self.strategy = strategy(side=side)

    def calc_moves(self, game_state):
        self.strategy.update(game_state=game_state)

        moves = self.strategy.move()

        moves_dict = {}
        for player_ind in self.controlled_player_inds:
            moves_dict[player_ind] = moves[player_ind]

        return moves_dict
