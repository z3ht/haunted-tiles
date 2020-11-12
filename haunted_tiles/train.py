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


def train(save_dir, agents, board, total_timesteps=4000):
    config = ppo.DEFAULT_CONFIG.copy()
    config['env_config'] = {
        "agents": agents,
        "board": board,
        "original_board": copy.deepcopy(board),
        "action_space": Discrete(5)
    }
    config["num_gpus"] = 1

    trainer = ppo.PPOTrainer(config=config, env=HauntedTilesEnvironment)
    for i in range(total_timesteps):
        result = trainer.train()
        if i % 100 == 0:
            print(pretty_print(result))

    save = trainer.save(save_dir)
    print("model saved at: ", save)

    # calc_win_rate(model)


def basic():
    agents = [
        MonsterReinforcementAgent(name="bob", side="home", controlled_player_ind=0),
        MonsterReinforcementAgent(name="fred", side="home", controlled_player_ind=1),
        StrategyAgent(side="home", strategy=Still, controlled_player_inds=[2]),
        StrategyAgent(side="away", strategy=RandomAvoidDeath)
    ]
    board = Board(board_type=BoardType.DEFAULT)

    train(save_dir="./models", agents=agents, board=board)


if __name__ == "__main__":
    ray.init(num_gpus=1)
    basic()

