from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Submission(Final, check_html=False)
