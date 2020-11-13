from gym.spaces import Discrete

import ray
from ray.rllib.agents import ppo
from ray.tune.logger import pretty_print

import copy
import pickle
import os

from haunted_tiles.agent.base import MonsterReinforcementAgent, StrategyAgent
from haunted_tiles.environment.base import HauntedTilesEnvironment
from haunted_tiles.emulator.board import Board, BoardType
from haunted_tiles.emulator.game import Game, Winner
from haunted_tiles.strategies import RLModel, RandomAvoidDeath, Still


def calc_win_rate(home_strategy, away_strategy, board_type=BoardType.DEFAULT, n_trials=100):
    wins = [0, 0, 0]
    original_board = Board(board_type=board_type)
    for _ in range(n_trials):
        board = copy.deepcopy(original_board)
        game = Game(board, home_strategy, away_strategy, True)

        winner = game.play_game(verbose=True)
        print(winner)

        if winner == Winner.HOME:
            wins[0] += 1
        elif winner == Winner.AWAY:
            wins[1] += 1
        elif winner == winner.TIE:
            wins[2] += 1
    win_prob = [w / n_trials for w in wins]
    print(win_prob)


def train_ppo(save_dir, rl_agents, action_space, board, proc_agents=tuple(), total_timesteps=50000):
    config = ppo.DEFAULT_CONFIG.copy()
    config['env_config'] = {
        "rl_agents": rl_agents,
        "proc_agents": proc_agents,
        "board": board,
        "original_board": copy.deepcopy(board),
        "action_space": action_space
    }
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

    trainer = ppo.PPOTrainer(config=config)
    result = trainer.train()
    print(pretty_print(result))

    save = trainer.save(save_dir)
    print("model saved at: ", save)


def load_train(model_dir, model_class, total_timesteps, checkpoint="/checkpoint_1/checkpoint-1"):
    infile = open(model_dir + "/config.pkl", 'rb')
    config = pickle.load(infile)
    infile.close()

    config["timesteps_per_iteration"] = total_timesteps

    config_save_file = open(model_dir + "/config.pkl", "wb")
    pickle.dump(config, config_save_file)
    config_save_file.close()

    print("Config pickle saved at " + model_dir + "/config.pkl")

    model = model_class(config)
    model.restore(model_dir + checkpoint)

    result = model.train()
    print(pretty_print(result))

    save = model.save(model_dir)
    print("model saved at: ", save)


def basic():
    rl_agents = {
        "chad": MonsterReinforcementAgent(name="chad", side="home", controlled_player_ind=0),
        "brad": MonsterReinforcementAgent(name="brad", side="home", controlled_player_ind=1),
        "rad": MonsterReinforcementAgent(name="rad", side="home", controlled_player_ind=2),
    }

    board = Board(board_type=BoardType.DEFAULT)

    train_ppo(
        save_dir="./models/beta",
        rl_agents=rl_agents,
        proc_agents=tuple([
            StrategyAgent(side="away", strategy=RandomAvoidDeath)
        ]),
        action_space=Discrete(5),
        board=board,
        total_timesteps=10000000
    )


def load():
    l = RLModel(side="home", model_class=ppo.PPOTrainer, model_dir="./models/alpha/")

    calc_win_rate(l, RandomAvoidDeath(side="away"))


if __name__ == "__main__":
    ray.init(num_gpus=1)
    basic()
    # load_train(model_dir="./models/alpha", model_class=ppo.PPOTrainer, total_timesteps=20000000)
    load()
