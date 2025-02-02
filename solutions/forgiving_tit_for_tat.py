class Strategy:
    def move(self, self_history: list[bool], opponent_history: list[bool]):
        if len(self_history) < 2:
            # We wait for the opponent to do at least two moves.
            return True
        
        # We cooperate if at least one of the last two moves of the opponent was a cooperation. 
        return (opponent_history[-1] == True) or (opponent_history[-2] == True)
