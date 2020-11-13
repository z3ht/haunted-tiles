from gym import spaces

import time

from ray.rllib.env.multi_agent_env import MultiAgentEnv

from haunted_tiles.emulator.game import Game, Winner
from haunted_tiles.strategies import Still
from haunted_tiles.environment.mock import mock_obs, mock_format_actions


class HauntedTilesEnvironment(MultiAgentEnv):

    metadata = {'render.modes': ['human', 'rgb_array']}

    def __init__(self, env_config):
        """
        Initialize a Haunted Tiles environment

        Params
        ======
        :param env_config : Environment configuration
                Parameters:
                    rl_agents : List of reinforcement agents that will be controlling monsters
                    proc_agents : List of procedural agents that will be controlling monsters
                    board : The board that the game should begin with
                    original_board : (optional) copy of the board to pass in
                    observation_space : (optional)
                            Shape/metadata about the provided agents' observable space
                            By default, agents observe the whole board where 0-3 are empty tiles with their damage
                                                    amount, 4 denotes friendly player locations, and 5 for enemy player
                    action_space :
                            Shape of the number of actions an agent can take. This must be uniform for all agents
        """
        rl_agents = env_config["rl_agents"]
        proc_agents = env_config["proc_agents"]
        board = env_config["board"]
        original_board = env_config["original_board"]
        action_space = env_config["action_space"]

        # Save reinforcement learning agents used in the environment
        self.agents = rl_agents
        self.num_agents = len(self.agents)

        # Save other agents used in the environment
        self.other_agents = proc_agents

        # Save board and original_board
        self.board = board
        self.original_board = original_board

        # Set action space
        self.action_space = action_space

        if "observation_space" in env_config:
            self.observation_space = env_config["observation_space"]
        else:
            # By default, observe the whole board 0-3 are empty tiles with their damage amount,
            #                                     4 for friendlies, 5 for enemies
            board_size = self.board.board_size
            self.observation_space = spaces.Box(low=0, high=6, shape=(board_size[0], board_size[1]))

        # Create game
        self.game = Game(self.board, Still(side="home"), Still(side="away"), True)

        # Call this only after game is up to date
        self.agents_obs = self._retrieve_agents_obs()

    def reset(self):
        self.board = self.original_board
        self.game = Game(self.board, Still(side="home"), Still(side="away"), True)

        # Call this only after game is up to date
        self.agents_obs = self._retrieve_agents_obs()

        # print("Initial Board: ")
        # for row in self.game.board.board:
        #     print(row)
        # print("--------------")
        # print("Initial Agent obs: ")
        # for agent, view in self.agents_obs.items():
        #     print("Agent: " + agent)
        #     for row in view:
        #         print(row)
        # print("--------------")
        # time.sleep(4)

        return self.agents_obs

    def step(self, actions_dict):
        """
        Determine how good every agents' moves are

        Parameters
        ----------
        :param actions_dict : Dictionary where keys are agent names and values are their corresponding action

        Returns
        -------
        obs_n, reward_n, done_n, info_n : tuple
            obs_n (dict[agent.name] = int) :
                dict containing all agents' observation of the environment
            reward_n (dict[agent.name] = float) :
                dict of rewards achieved by each previous action.
                Note: The scale varies between environments, but the goal is always to increase
                    total reward.
            done_n (dict[agent.name] = bool) :
                dict denoting whether or not each agent should be reset.
                Note: if the environment should be reset for one agent, then every agent's
                    environment must also be reset
            info_n (dict) :
                 dict of diagnostic information (useful for debugging).
                 Note: This can sometimes be useful for learning (for example, it might contain the raw
                        probabilities behind the environment's last state change).
                        However, official evaluations of your agent are not allowed to use this for learning.
        """
        rewards_dict = {}
        for name, agent in self.agents.items():
            rewards_dict[name] = 0

        # Its best to create a wrapper and add to info rather than modifying info here directly
        # More info on wrappers:
        # https://github.com/araffin/rl-tutorial-jnrr19/blob/sb3/2_gym_wrappers_saving_loading.ipynb
        info_n = {}

        formatted_actions = mock_format_actions(self.agents, actions_dict)

        for agent_name, action in actions_dict.items():
            agent = self.agents[agent_name]

            formatted_action = formatted_actions[agent_name]

            rewards_dict[agent_name] = agent.calc_reward(self.game, formatted_action)

            for player_ind, move in formatted_action.items():
                # print(f"Agent: {agent_name}     Player ind: {player_ind}        Move: {move}")
                self.game.move_player(side=agent.side, player_index=player_ind, direction=move)

        for i, agent in enumerate(self.other_agents):
            formatted_action = agent.calc_moves(self.game.get_game_state())
            for player_ind, move in formatted_action.items():
                self.game.move_player(side=agent.side, player_index=player_ind, direction=move)

        self.game.update_board()
        self.game.update_dead()

        self.agents_obs = self._retrieve_agents_obs()

        episode_over = self.game.get_winner() is not Winner.NONE

        done_dict = {
            '__all__': episode_over
        }

        for agent_name, agent in self.agents.items():
            if episode_over:
                rewards_dict[agent_name] += agent.game_end_reward(self.game)
            done_dict[agent_name] = episode_over

        # print("Board: ")
        # for row in self.game.board.board:
        #     print(row)
        # print("--------------")
        # print("Agent obs: ")
        # for agent, view in self.agents_obs.items():
        #     print("Agent: " + agent)
        #     for row in view:
        #         print(row)
        # print("--------------")
        # print("Rewards dict: ")
        # print(rewards_dict)
        # print("--------------")
        # print("Done dict: ")
        # print(done_dict)
        # print("--------------")
        # time.sleep(4)

        return self.agents_obs, rewards_dict, done_dict, info_n

    def render(self):
        print(self.game.get_game_state())

    def _retrieve_agents_obs(self, agents=None, game_state=None):
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

        if game_state is None:
            game_state = self.game.get_game_state()

        return mock_obs(agents, game_state)
