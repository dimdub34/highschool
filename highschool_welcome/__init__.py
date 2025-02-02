from otree.api import *
from pathlib import Path

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
    entered_id = models.StringField(
        label="Veuillez saisir un identifiant, ce que vous voulez, avec au minimum 6 caractères."
    )


# PAGES
class MyPage(Page):
    @staticmethod
    def js_vars(player: Player):
        return dict(fill_auto=player.session.config["fill_auto"])

class Welcome(MyPage):
    form_model = "player"
    form_fields = ["entered_id"]

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.participant._is_bot = True
            player.entered_id = "bot"
        player.participant.label = player.entered_id


class Presentation(MyPage):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(nb_paids=min(len(player.subsession.get_players()) // 2, player.session.config['nb_paids']))


page_sequence = [Welcome, Presentation]
