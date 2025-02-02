# Strategy described in Nicky Case's "The Evolution of Trust"
# https://ncase.me/trust/
#
# SIMPLETON:
#   Hi! I try to start by cooperating. If you cooperate back, I do the same
#   thing as my last move, even if it was a mistake. If you cheat back, I do the
#   opposite thing as my last move, even if it was a mistake.

class Strategy:
    def move(self, self_history: list[bool], opponent_history: list[bool]):
        if len(self_history) == 0:
            return True # This is the first round. Start by cooperating.
        
        move = self_history[-1] # Our last move
        if not opponent_history[-1]:
            # If our opponent defected, do the opposite of what we did last time.
            move = not move

        return move
