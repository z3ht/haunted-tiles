from gym.spaces import Discrete

import copy

import ray
from ray.rllib.agents import ppo
from ray.tune.logger import pretty_print

from haunted_tiles.agent.base import MonsterReinforcementAgent, StrategyAgent
from haunted_tiles.environment.base import HauntedTilesEnvironment
from haunted_tiles.strategies import Still, RandomAvoidDeath, ModelGotoBestValid
from haunted_tiles.emulator.board import Board, BoardType
from haunted_tiles.emulator.game import Game, Winner


def calc_win_rate(model, board_type=BoardType.DEFAULT, n_trials=1000):
    wins = [0, 0]
    for _ in range(n_trials):
        board = Board(board_type=board_type)
        game = Game(board, ModelGotoBestValid(side="home", model=model), RandomAvoidDeath(side="away"), True)
        winner = game.play_game()
        if winner == Winner.HOME:
            wins[0] += 1
        else:
            wins[1] += 1
    win_prob = [w / n_trials for w in wins]
    print(win_prob)


def train(save_dir, agents, board, total_timesteps=50000):
    config = ppo.DEFAULT_CONFIG.copy()
    config['env_config'] = {
        "agents": agents,
        "board": board,
        "original_board": copy.deepcopy(board),
        "action_space": Discrete(5)
    }
    config["num_gpus"] = 1
    config["timesteps_per_iteration"] = total_timesteps

    trainer = ppo.PPOTrainer(config=config, env=HauntedTilesEnvironment)
    result = pretty_print(trainer.train())
    print(result)

    save = trainer.save(save_dir)
    print("model saved at: ", save)


def basic():
    agents = [
        MonsterReinforcementAgent(name="chad", side="home", controlled_player_ind=0),
        MonsterReinforcementAgent(name="brad", side="home", controlled_player_ind=1),
        MonsterReinforcementAgent(name="gamer", side="home", controlled_player_ind=2),
        MonsterReinforcementAgent(name="exksde", side="away", controlled_player_ind=0),
        MonsterReinforcementAgent(name="ligma", side="away", controlled_player_ind=1),
        MonsterReinforcementAgent(name="sugma", side="away", controlled_player_ind=2)
    ]
    board = Board(board_type=BoardType.DEFAULT)

    train(save_dir="./models/alpha", agents=agents, board=board)


if __name__ == "__main__":
    ray.init(num_gpus=1)
    basic()

