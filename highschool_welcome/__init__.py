from otree.api import *
from pathlib import Path

from otree.models import subsession

app_name = Path(__file__).parent.name

doc = """
Welcome page, with consent, and presentation page.
"""


class C(BaseConstants):
    NAME_IN_URL = app_name.replace("_", "")
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass

# PAGES
class MyPage(Page):
    @staticmethod
    def js_vars(player: Player):
        return dict(fill_auto=player.session.config["fill_auto"])


class Welcome(MyPage):
    pass


class Presentation(MyPage):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(nb_paids=min(len(player.subsession.get_players()) // 2, player.session.config['nb_paids']))


page_sequence = [Welcome, Presentation]
