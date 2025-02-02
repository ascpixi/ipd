import random

# Joss is similar to Tit For Tat, but we randomly defect to try and take advantage
# of the opponent.

class Strategy:
    def move(self, self_history: list[bool], opponent_history: list[bool]):
        if random.random() < 0.10:
            # Try to take advantage!!
            return False

        if len(self_history) == 0:
            # If this is our first move, play nice, and cooperate.
            return True

        # Otherwise, mirror the move of the opponent.
        return opponent_history[-1]
