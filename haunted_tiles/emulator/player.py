

class Player:
    def __init__(self, x, y):
        self.is_dead = False
        self.y = y
        self.x = x
        self._direction_to_move = {'south': (0, -1), 'north': (0, 1), 'east': (1, 0), 'west': (-1, 0), 'none': (0, 0)}

    def get_location(self):
        return self.x, self.y

    def move(self, direction):
        """
        :param direction: move direction or string
        :return:
        """
        if self.is_dead:
            return

        if isinstance(direction, tuple):
            if abs(direction[0]) + abs(direction[1]) not in range(0, 2):
                raise ValueError(f'Unexpected direction value passed into Player.move: {direction}')

            self.y += direction[1]
            self.x += direction[0]
        else:
            self.y += self._direction_to_move[direction][1]
            self.x += self._direction_to_move[direction][0]
