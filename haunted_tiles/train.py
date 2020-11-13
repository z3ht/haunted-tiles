from gym.spaces import Discrete

import ray
from ray.rllib.agents import ppo
from ray.tune.logger import pretty_print

import copy
import pickle
import os

from haunted_tiles.agent.base import MonsterReinforcementAgent
from haunted_tiles.environment.base import HauntedTilesEnvironment
from haunted_tiles.emulator.board import Board, BoardType
from haunted_tiles.emulator.game import Game, Winner
from haunted_tiles.strategies import RLModel


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


def train_ppo(save_dir, rl_agents, action_space, board, total_timesteps=50000):
    config = ppo.DEFAULT_CONFIG.copy()
    config['env_config'] = {
        "rl_agents": rl_agents,
        "proc_agents": [],
        "board": board,
        "original_board": copy.deepcopy(board),
        "action_space": action_space
    }
    config["num_gpus"] = 1
    config["timesteps_per_iteration"] = total_timesteps
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


def basic():
    rl_agents = {
        "chad": MonsterReinforcementAgent(name="chad", side="home", controlled_player_ind=0),
        "brad": MonsterReinforcementAgent(name="brad", side="home", controlled_player_ind=1),
        "gamer": MonsterReinforcementAgent(name="gamer", side="home", controlled_player_ind=2),
        "exksde": MonsterReinforcementAgent(name="exksde", side="away", controlled_player_ind=0),
        "ligma": MonsterReinforcementAgent(name="ligma", side="away", controlled_player_ind=1),
        "sugma": MonsterReinforcementAgent(name="sugma", side="away", controlled_player_ind=2)
    }
    board = Board(board_type=BoardType.DEFAULT)

    train_ppo(
        save_dir="./models/beta",
        rl_agents=rl_agents,
        action_space=Discrete(5),
        board=board,
        total_timesteps=1000000
    )


def load():
    l = RLModel(side="home", model_class=ppo.PPOTrainer, model_dir="./models/beta/")

    l.update(
        {
            'tileStatus': BoardType.DEFAULT.value[0],
            'home': [(0, 0, False), (3, 0, False), (6, 0, False)],
            'away': [(0, 6, False), (3, 6, False), (6, 6, False)],
            'boardSize': (7, 7)
        }
    )

    l.move()


if __name__ == "__main__":
    ray.init(num_gpus=1)
    # basic()
    load()
