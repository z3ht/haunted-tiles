
class Agent:

    def __init__(self):
        pass

    def update_game(self, action, game):
        pass


class ReinforcementAgent(Agent):

    def __init__(self, action_space):
        super().__init__()

        self.action_space = action_space

    def format_action(self, raw_action):
        pass

    def interpret_game_state(self, game_state):
        pass

    def calc_reward(self, action):
        pass


class ProceduralAgent(Agent):

    def __init__(self):
        super().__init__()

    def move(self, game_state):
        pass

    #     # if not self._valid_move(direction, agent.get_location()):
    #     #     return self.game_state, 5, episode_over, {}
    # def _valid_move(self, move, location):
    #     x = location[1]
    #     y = location[0]
    #     if move == 'north' and (y + 1) >= len(self.board.board):
    #         return False
    #     elif move == 'south' and (y - 1) < 0:
    #         return False
    #     elif move == 'east' and (x + 1) >= len(self.board.board[0]):
    #         return False
    #     elif move == 'west' and (x - 1) < 0:
    #         return False
    #     return True
    #
    # @staticmethod
    # def _game_state_to_team_obs(game_state, side):
    #     """
    #     Convert game state into
    #
    #     :param game_state: Current game state
    #     :param side: perspective of board ("home" or "away")
    #
    #     :return: observable game_state from the provided side's perspective as numpy array
    #     """
    #
    #     board = game_state['tileStatus'].board
    #
    #     # team positions for living players
    #     home_positions = [(player[0], player[1]) for player in game_state['home'] if not player[2]]
    #     away_positions = [(player[0], player[1]) for player in game_state['away'] if not player[2]]
    #
    #     obs = []
    #     for i, row in enumerate(board):
    #         obs_row = []
    #         for j, val in enumerate(row):
    #             if (i, j) in home_positions:
    #                 if side == "home":
    #                     obs_row.append(4)
    #                 else:
    #                     obs_row.append(5)
    #             elif (i, j) in away_positions:
    #                 if side == "away":
    #                     obs_row.append(4)
    #                 else:
    #                     obs_row.append(5)
    #             else:
    #                 obs_row.append(val)
    #         obs.append(obs_row)
    #
    #     return np.array(obs)


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
