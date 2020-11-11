from gym import Env, spaces
import numpy as np
from haunted_tiles.emulator.board import Board, BoardType
from haunted_tiles.emulator.game import Game, Winner
from stable_baselines3 import PPO


class HauntedTilesEnvironment(Env):

    ACTIONS = ['north', 'south', 'east', 'west', 'none']

    def __init__(self, agents, board, observation_space=None):
        """
        Initialize a Haunted Tiles environment

        Params
        ======
        :param agents: List of agents that will be controlling the monsters
        :param board: The board that the game should begin with
        :param observation_space :
                    Shape/metadata about the provided agents' observable space
                    By default, agents observe the whole board where 0-3 are empty tiles with their damage amount,
                                                  4 denotes friendly monster locations, and 5 for enemy monsters
        """

        # Save board and original_board
        self.board = board
        self.original_board = self.board.copy()

        # Save agents used in the environment
        self.agents = agents

        if observation_space is None:
            # By default, observe the whole board 0-3 are empty tiles with their damage amount,
            #                                     4 for friendlies, 5 for enemies

            board_size = self.board.board_size
            observation_space = spaces.Box(low=0, high=6, shape=(board_size[0], board_size[1]), dtype=np.uint8)

        self.observation_space = observation_space

        # Create game
        self.game = Game(self.board, True)

        # Action spaces for all agents
        self.action_spaces = [agent.action_space for agent in self.agents]

        # Call this only after game is up to date
        self.agents_obs = self._retrieve_agents_obs()

    def reset(self):
        self.board = self.original_board
        self.game = Game(self.board, True)

        # Call this only after game is up to date
        self.agents_obs = self._retrieve_agents_obs()

        return self.agents_obs

    def _retrieve_agents_obs(self, agents=None):
        """
        For each agent in agents, retrieve an interpretable numpy array of the game state

        Note: All agents must return a numpy array that matches the structure/metadata of self.observation_space

        Params
        ======
        :param agents: Agents to interpret the game state

        :return: List of interpretable views of the game state for every agent requested
        """

        if agents is None:
            agents = self.agents

        agent_obs = []
        for agent in agents:
            agent_obs.append(agent.interpret_game_state(self.game.get_game_state(include_dead_state=True)))

        return np.array([agent_obs])

    def step(self, action_n):
        """
        Determine how good every agents' moves were

        Parameters
        ----------
        action_n : List of actions each agent attempted

        Returns
        -------
        obs_n, reward_n, done_n, info_n : tuple
            obs_n (list[object]) :
                list of environment-specific objects representing all agents' observation of
                the environment.
            reward_n (float) :
                list of rewards achieved by each previous action.
                Note: The scale varies between environments, but the goal is always to increase
                    total reward.
            done_n (bool) :
                list denoting whether or not each agent should be reset.
                Note: if the environment should be reset for one agent, then every agent's
                    environment must also be reset
            info_n (dict) :
                 list of every agent's diagnostic information (useful for debugging).
                 Note: This can sometimes be useful for learning (for example, it might contain the raw
                        probabilities behind the environment's last state change).
                        However, official evaluations of your agent are not allowed to use this for learning.
        """

        rewards_n = [0] * len(self.agents)

        # Its best to create a wrapper and add to info rather than modifying info here directly
        # More info on wrappers:
        # https://github.com/araffin/rl-tutorial-jnrr19/blob/sb3/2_gym_wrappers_saving_loading.ipynb
        info_n = [None] * len(self.agents)

        for i, action in enumerate(action_n):
            agent = self.agents[i]

            formatted_action = agent.format_action(action)

            rewards_n[i] = agent.calc_reward(formatted_action)

            agent.update_game(formatted_action, self.game)

            self.agents_obs[i] = self._retrieve_agents_obs(agents=[agent])[0]

        # self.game.update_board()
        # self.game.update_dead()

        episode_over = self.game.get_winner() is not Winner.NONE

        return self.agents_obs, rewards_n, [episode_over] * len(self.agents), info_n

        direction = self.ACTIONS[action]
        agent = self.game.home_players[1]

        episode_over = False
        if self.game.get_winner() is not Winner.NONE or agent.is_dead:
            print("reseting...")
            episode_over = True

        if not self._valid_move(direction, agent.get_location()):
            return self.game_state, 5, episode_over, {}

        # move players according to strategies
        self.game.move_players()
        # move agent according to supplied action
        self.game.home_players[1].move(direction)

        self.game.update_board()
        self.game.update_dead()
        self.game_state = self._game_state_to_team_obs(self.game.get_game_state(include_dead_state=True))

        # self.status = self.env.step()
        # reward = self._get_reward()
        # ob = self.env.getState()
        # episode_over = self.status != hfo_py.IN_GAME
        # return ob, reward, episode_over, {}
        print(self.game_state)
        return self.game_state, 5, episode_over, {}

    def render(self, mode='human', close=False):
        print(self.game_state)

    # FIXME BELOW THIS LINE THE CODE SHOULD BE REFACTORED TO AGENT CLASS

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

    @staticmethod
    def _game_state_to_team_obs(game_state, side):
        """
        Convert game state into

        :param game_state: Current game state
        :param side: perspective of board ("home" or "away")

        :return: observable game_state from the provided side's perspective as numpy array
        """

        board = game_state['tileStatus'].board

        # team positions for living players
        home_positions = [(player[0], player[1]) for player in game_state['home'] if not player[2]]
        away_positions = [(player[0], player[1]) for player in game_state['away'] if not player[2]]

        obs = []
        for i, row in enumerate(board):
            obs_row = []
            for j, val in enumerate(row):
                if (i, j) in home_positions:
                    if side == "home":
                        obs_row.append(4)
                    else:
                        obs_row.append(5)
                elif (i, j) in away_positions:
                    if side == "away":
                        obs_row.append(4)
                    else:
                        obs_row.append(5)
                else:
                    obs_row.append(val)
            obs.append(obs_row)

        return np.array(obs)


env = HauntedTilesEnvironment(Agent, Board(BoardType.DEFAULT))

model = PPO('mlppolicy', env, verbose=2)
model.learn(total_timesteps=4000)

obs = env.reset()
for i in range(1000):
    action, _states = model.predict(obs)
    obs, rewards, dones, _ = env.step(action)
    if dones:
        break
    env.render()

