from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Submission(Welcome, timeout_happened=True)
        yield Presentation
