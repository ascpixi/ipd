class Strategy:
    def move(self, self_history: list[bool], opponent_history: list[bool]):
        if len(self_history) == 0:
            # If this is our first move, play nice, and cooperate.
            return True
        
        # Otherwise, mirror the move of the opponent.
        return opponent_history[-1]
