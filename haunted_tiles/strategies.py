from enum import Enum


class Side(str, Enum):
    HOME = 'home',
    AWAY = 'away'


class Strategy:

    def __init__(self, game_state, side):
        self.game_state = game_state
        self.side = side

        if self.side is None:
            raise ValueError("Incorrect side value provided")

    def update(self, game_state):
        pass

    def move(self):
        pass


class Basic(Strategy):

    def __init__(self, game_state, side):
        super().__init__(game_state, side)

    def update(self, game_state):
        pass

    def move(self):
        return ['south', 'none', 'south']
