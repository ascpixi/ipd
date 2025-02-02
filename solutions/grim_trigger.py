class Strategy:
    def __init__(self):
        # The __init__ method will be called just before the match begins. We can
        # set up our "memory" here!
        self.grudge = False

    def move(self, self_history: list[bool], opponent_history: list[bool]):
        if self.grudge:
            return False # I still remember that!
        
        if len(self_history) == 0:
            return True # Play nice at the beginning

        if opponent_history[-1] == False:
            # Hey, the opponent defected! Time to hold a grudge now.
            self.grudge = True
            return False
        
        return True
