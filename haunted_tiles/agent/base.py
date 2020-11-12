from haunted_tiles.strategies import Strategy


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

    ACTIONS = ['north', 'south', 'east', 'west', 'none']

    def __init__(self, side, controlled_player_inds, action_space):
        super().__init__(side, controlled_player_inds)

        self.action_space = action_space

    def format_action(self, raw_action):
        pass

    def interpret_game_state(self, game_state):
        pass

    def calc_reward(self, game, action):
        pass

    def _calc_location(self, cur_location, action):
        pass


class TeamReinforcementAgent(ReinforcementAgent):

    def __init__(self, side, controlled_player_inds, action_space):
        super().__init__(side, controlled_player_inds, action_space)

    def format_action(self, raw_action):
        pass

    def interpret_game_state(self, game_state):
        pass

    def calc_reward(self, game, action):
        pass


class MonsterReinforcementAgent(ReinforcementAgent):

    def __init__(self, side, controlled_player_inds, action_space):
        super().__init__(side, controlled_player_inds, action_space)

    def format_action(self, raw_action):
        pass

    def interpret_game_state(self, game_state):
        pass

    def calc_reward(self, game, action):
        pass


class ProceduralAgent(Agent):

    def __init__(self, side, controlled_player_inds):
        super().__init__(side, controlled_player_inds)

    def calc_action(self, game_state):
        pass


class StrategyAgent(ProceduralAgent):

    def __init__(self, side, strategy):
        super().__init__(side, [0, 1, 2])

        if not isinstance(self.strategy, Strategy):
            raise ValueError("strategy must be an instance of the Strategy class")

        self.strategy = strategy

    def calc_action(self, game_state):
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
