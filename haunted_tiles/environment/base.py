from gym import Env, spaces
import numpy as np
from haunted_tiles.emulator.game import Game, Winner
from haunted_tiles.agent.base import ReinforcementAgent


class HauntedTilesEnvironment(Env):

    def __init__(self, agents, board, observation_space=None):
        """
        Initialize a Haunted Tiles environment

        Params
        ======
        :param agents: List of agents that will be controlling monsters (supports reinforcement and procedural)
        :param board: The board that the game should begin with
        :param observation_space :
                    Shape/metadata about the provided agents' observable space
                    By default, agents observe the whole board where 0-3 are empty tiles with their damage amount,
                                                  4 denotes friendly player locations, and 5 for enemy player
        """

        # Save reinforcement learning agents used in the environment
        self.rl_agents = [agent for agent in agents if isinstance(agent, ReinforcementAgent)]
        # TODO fix should other agents be
        # Save other agents used in the environment
        self.other_agents = [agent for agent in agents if not isinstance(agent, ReinforcementAgent)]

        # Save board and original_board
        self.board = board
        self.original_board = self.board.copy()

        if observation_space is None:
            # By default, observe the whole board 0-3 are empty tiles with their damage amount,
            #                                     4 for friendlies, 5 for enemies
            board_size = self.board.board_size
            observation_space = spaces.Box(low=0, high=6, shape=(board_size[0], board_size[1]), dtype=np.uint8)

        # Set observation space
        self.observation_space = observation_space

        # Create game
        self.game = Game(self.board, True)

        # Action spaces for all agents
        self.action_spaces = [agent.action_space for agent in self.rl_agents]

        # Call this only after game is up to date
        self.agents_obs = self._retrieve_agents_obs()

    def reset(self):
        self.board = self.original_board
        self.game = Game(self.board, True)

        # Call this only after game is up to date
        self.agents_obs = self._retrieve_agents_obs()

        return self.agents_obs

    def step(self, action_n):
        """
        Determine how good every rl_agents' moves are

        Parameters
        ----------
        action_n : List of actions each rl_agent made

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

        rewards_n = [0] * len(self.rl_agents)

        # Its best to create a wrapper and add to info rather than modifying info here directly
        # More info on wrappers:
        # https://github.com/araffin/rl-tutorial-jnrr19/blob/sb3/2_gym_wrappers_saving_loading.ipynb
        info_n = [None] * len(self.rl_agents)

        for i, action in enumerate(action_n):
            agent = self.rl_agents[i]

            formatted_action = agent.format_action(action)

            rewards_n[i] = agent.calc_reward(self.game, formatted_action)

            agent.update_game(self.game, formatted_action)

        for i, agent in enumerate(self.other_agents):
            move = agent.move(self.game.get_game_state(include_dead_state=True))
            agent.update_game(self.game, move)  # TODO figure out what this does

        self.game.update_board()
        self.game.update_dead()

        self.agents_obs = self._retrieve_agents_obs()

        episode_over = self.game.get_winner() is not Winner.NONE

        return self.agents_obs, rewards_n, [episode_over] * len(self.rl_agents), info_n

    def render(self, mode='human', close=False):
        print(self.game.get_game_state())

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
            agents = self.rl_agents

        agents_obs = []
        for agent in agents:
            agents_obs.append(agent.interpret_game_state(self.game.get_game_state(include_dead_state=True)))

        return np.array([agents_obs])
