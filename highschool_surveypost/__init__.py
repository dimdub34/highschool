import random

from otree.api import *

doc = """
Questionnaire Après jeu <br/>
Motivations études supérieures.
"""


class C(BaseConstants):
    NAME_IN_URL = 'highschoolsurveypost'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    motivation_etudes_superieures = models.IntegerField(
        label="Dans quelle mesure es-tu motivé(e) pour faire des études supérieures ?")
    motivation_transmission = models.LongStringField(
        label="Imagine que tu parles à un jeune qui hésite à poursuivre des études supérieures. "
              "Écris-lui un message pour partager ton avis sur l'importance de faire des études après le lycée."
    )


# PAGES
class MyPage(Page):
    @staticmethod
    def js_vars(player: Player):
        return dict(fill_auto=player.session.config.get("fill_auto", False))


class Questionnaire(MyPage):
    form_model = 'player'
    form_fields = ['motivation_etudes_superieures', 'motivation_transmission']

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.participant._is_bot = True
            player.motivation_etudes_superieures = random.randint(1, 5)
            player.motivation_transmission = "Message auto par bot"


page_sequence = [Questionnaire]
