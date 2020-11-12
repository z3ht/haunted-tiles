

class Player:
    def __init__(self, y, x):
        self.is_dead = False
        self.y = y
        self.x = x
        self._direction_to_move = {'south': (-1, 0), 'north': (1, 0), 'east': (0, 1), 'west': (0, -1), 'none': (0, 0)}

    def get_location(self):
        return self.y, self.x

    def move(self, direction):
        if isinstance(direction, tuple):
            self.y += direction[0]
            self.x += direction[1]
        else:
            self.y += self._direction_to_move[direction][0]
            self.x += self._direction_to_move[direction][1]
