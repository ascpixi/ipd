import random

class Strategy:
    def move(self, self_history: list[bool], opponent_history: list[bool]):
        return random.random() < 0.5
