from gym.spaces import Discrete

import ray
from ray.rllib.agents import ppo, dqn, marwil
from ray.tune.logger import pretty_print

import copy
import pickle
import os

from haunted_tiles.agent.base import MonsterReinforcementAgent, StrategyAgent
from haunted_tiles.environment.base import HauntedTilesEnvironment
from haunted_tiles.emulator.board import Board, BoardType
from haunted_tiles.emulator.game import Game, Winner
from haunted_tiles.strategies import RLModel, RandomAvoidDeath, Still


def calc_win_rate(home_strategy, away_strategy, board_type=BoardType.DEFAULT, n_trials=1000):
    wins = [0, 0]
    for _ in range(n_trials):
        board = Board(board_type=board_type)
        game = Game(board, home_strategy, away_strategy, True)
        winner = game.play_game()
        if winner == Winner.HOME:
            wins[0] += 1
        else:
            wins[1] += 1
    win_prob = [w / n_trials for w in wins]
    print(win_prob)


def train_ppo(save_dir, rl_agents, action_space, board, proc_agents=tuple(), total_timesteps=50000):
    config = dqn.DEFAULT_CONFIG.copy()
    config['env_config'] = {
        "rl_agents": rl_agents,
        "proc_agents": proc_agents,
        "board": board,
        "original_board": copy.deepcopy(board),
        "action_space": action_space
    }
    config["num_gpus"] = 1
    config["timesteps_per_iteration"] = total_timesteps
    config["num_workers"] = 24
    config["env"] = HauntedTilesEnvironment

    if os.path.isdir(save_dir):
        ans = str(input("Model already exists. Overwrite? (y/n) ")).lower()
        if not ans.startswith("y"):
            print("exiting...")
            return
    else:
        os.mkdir(save_dir)

    config_save_file = open(save_dir + "/config.pkl", "wb")
    pickle.dump(config, config_save_file)
    config_save_file.close()

    print("Config pickle saved at " + save_dir + "/config.pkl")

    trainer = dqn.DQNTrainer(config=config)
    for i in range(100):
        result = trainer.train()
        print(pretty_print(result))

    save = trainer.save(save_dir)
    print("model saved at: ", save)


def basic():
    rl_agents = {
        "chad": MonsterReinforcementAgent(name="chad", side="home", controlled_player_ind=0),
    }

    board = Board(board_type=BoardType.DEFAULT)

    train_ppo(
        save_dir="./models/beta",
        rl_agents=rl_agents,
        proc_agents=tuple([
            StrategyAgent(side="away", strategy=RandomAvoidDeath),
            StrategyAgent(side="home", strategy=Still, controlled_player_inds=[1, 2])
        ]),
        action_space=Discrete(5),
        board=board,
        total_timesteps=10000
    )


def load():

    l = RLModel(side="home", model_class=dqn.DQNTrainer, model_dir="./models/beta/")

    calc_win_rate(l, RandomAvoidDeath(side="away"))


if __name__ == "__main__":
    ray.init(num_gpus=1)
    basic()
    load()
