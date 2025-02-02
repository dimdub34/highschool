from otree.api import *
from pathlib import Path
import random

app_name = Path(__file__).parent.name

doc = """
Survey with socio-demographics information and one question about self-efficacy.
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
    age = models.IntegerField(label='Age', min=18, max=120)
    sexe = models.StringField(
        label="Sexe à la naissance", choices=[("F", "Féminin"), ("M", "Masculin")],
        widget=widgets.RadioSelectHorizontal)
    education = models.BooleanField(
        label="L'un des membres de votre famille proche (parents, frères et soeurs) fait-il (a-t-il fait) des études "
              "supérieures ?", widget=widgets.RadioSelectHorizontal
    )
    self_eff_1 = models.IntegerField(
        label="Dans quelle mesure vos succès sont déterminés par la chance vs par vos actions : ")
    self_eff_2 = models.IntegerField(
        label="Je suis confiant dans ma capacité à résoudre les problèmes que je suis susceptible de rencontrer dans "
              "la vie.")


# PAGES
class Questionnaire(Page):
    form_model = 'player'
    form_fields = ['sexe', 'age', "education", 'self_eff_1', 'self_eff_2']

    @staticmethod
    def js_vars(player: Player):
        return dict(fill_auto=player.session.config["fill_auto"])

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            player.participant._is_bot = True
            player.age = random.randint(18, 120)
            player.sexe = random.choice(['F', 'M'])
            player.education = random.choice([True, False])
            player.self_eff_1 = random.randint(1, 10)
            player.self_eff_2 = random.randint(1, 10)


page_sequence = [Questionnaire]
