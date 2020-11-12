from gym.spaces import Discrete
from stable_baselines3 import PPO

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


def train(save_location, model=None, environment=None, total_timesteps=4000):
    if model is None:
        if environment is None:
            raise ValueError("Model or environment must be provided in order to train")
        model = PPO('MlpPolicy', environment, verbose=2)

    model.learn(total_timesteps=total_timesteps)

    calc_win_rate(model)

    model.save(save_location)

    del model


def basic():
    agents = [
        MonsterReinforcementAgent(side="home", controlled_player_ind=0, action_space=Discrete(5)),
        StrategyAgent(side="home", strategy=Still, controlled_player_inds=[1, 2]),
        StrategyAgent(side="away", strategy=RandomAvoidDeath)
    ]
    board = Board(board_type=BoardType.DEFAULT)

    hte = HauntedTilesEnvironment(agents=agents, board=board)

    train(save_location="./model/basic.zip", environment=hte)


if __name__ == "__main__":
    basic()

# env = HauntedTilesEnvironment([Agent], Board(BoardType.DEFAULT))
#
#
# model.learn(total_timesteps=4000)
#
# obs = env.reset()
# for i in range(1000):
#     action, _states = model.predict(obs)
#     obs, rewards, dones, _ = env.step(action)
#     if dones:
#         break
#     env.render()
