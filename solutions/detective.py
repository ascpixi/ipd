# Strategy described in Nicky Case's "The Evolution of Trust": https://ncase.me/trust/
# Detective:
#   First: I analyze you. I start: Cooperate, Cheat, Cooperate, Cooperate.
#   If you cheat back, I'll act like "tit_for_tat".
#   If you never cheat back, I'll act like "always_defect".
#   to exploit you. Elementary, my dear Watson.

ANALYSIS_MOVES = [True, False, True, True]

class Strategy:
    def __init__(self):
        self.take_advantage = False

    def move(self, self_history: list[bool], opponent_history: list[bool]):
        if len(self_history) < len(ANALYSIS_MOVES):
            return ANALYSIS_MOVES[len(self_history)]
        
        if len(self_history) == len(ANALYSIS_MOVES):
            # We're done with our analysis moves - let's look at how the opponent responded...
            if not all(opponent_history):
                # Not all of the moves in our history are cooperations - let's play like tit for tat.
                self.take_advantage = False
            else:
                # The opponent hasn't defected once! Let's always defect.
                self.take_advantage = True
        
        if self.take_advantage:
            return False
        else:
            return opponent_history[-1] # tit-for-tat
