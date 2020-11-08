

class Player:
    def __init__(self, y, x):
        self.is_dead = False
        self.y = y
        self.x = x

    def get_location(self):
        return self.y, self.x

    def move(self, y, x):
        self.y, = y
        self.x = x