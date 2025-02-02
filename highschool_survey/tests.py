from . import *


class PlayerBot(Bot):
    def play_round(self):
        yield Submission(Questionnaire, timeout_happened=True)
