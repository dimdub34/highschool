import random
import statistics
from pathlib import Path
from otree.api import *

app_name = Path(__file__).parent.name

doc = """
Number Line Estimation
"""


class C(BaseConstants):
    NAME_IN_URL = app_name.replace("_", "")
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1

    NLE_VALUES = [18.09, 85.03, 8.11, 77.09, 92.17, 14.64, 59.99, 93.17, 9.11, 17.76]
    NB_TARGETS = len(NLE_VALUES)
    NLE_TIME = 10
    CONSTANTE = 100  # gain si cible exacte
    FACTEUR_DISTANCE = 1  # donc gain = CONSTANTE - FACTEUR_DISTANCE x distance où distance = | cible - valeur sélectionnée |

    SCORE_CHOICES = [(10, "[95 - 100]"), (9, "[90 - 95)"), (8, "[85 - 90)"),
                     (7, "[80 - 85)"), (6, "[75 - 80)"), (5, "[70 - 75)"),
                     (4, "[65 - 70)"), (3, "[60 - 65)"), (2, "[55 - 60)"),
                     (1, "[50 - 55)"), (0, "[0 - 50)")]

    CLASSEMENT_CHOICES = [(10, '[1 - 10]'), (9, '[11 - 20]'), (8, '[21 - 30]'), (7, '[31 - 40]'), (6, '[41 - 50]'),
                          (5, '[51 - 60]'), (4, '[61 - 70]'), (3, '[71 - 80]'), (2, '[81 - 90]'), (1, '[91 - 100]')]


class Subsession(BaseSubsession):
    post_conf = models.BooleanField()
    nle_values = models.StringField()
    penalite_erreur_estim = models.FloatField()


def creating_session(subsession: Subsession):
    subsession.post_conf = subsession.session.config["post_conf"]
    subsession.nle_values = "-".join(list(map(str, C.NLE_VALUES)))
    subsession.penalite_erreur_estim = subsession.session.config["penalite_erreur_estim"]
    if "nle_score_choices" not in subsession.session.vars:
        subsession.session.vars["nle_score_choices"] = C.SCORE_CHOICES.copy()
        subsession.session.vars["nle_classement_choices"] = C.CLASSEMENT_CHOICES.copy()


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    nle_estimation_score_code = models.IntegerField(
        label="Veuillez sélectionner l'intervalle dans lequel vous pensez que votre score va se situer. <br>"
              "L'intervalle [95 - 100] signifie que vous pensez avoir une distance moyenne inférieure à 5, "
              "autrement dit être très précis(e). <br>"
              "A l'inverse l'intervalle [0 - 50) signifie que vous pensez avoir distance moyenne supérieure à 50, "
              "autrement dit ne pas être précis(e) du tout. ",
        choices=C.SCORE_CHOICES, doc="10 = score élevé, 1 = score faible"
    )
    nle_estimation_score_interval = models.StringField()
    nle_estimation_classement_code = models.IntegerField(
        label="Veuillez sélectionner maintenant la position dans laquelle vous pensez que votre score va se situer en "
              "comparaison avec 99 personnes sélectionnées au hasard parmi celles qui jouent en même temps. <br> "
              "Par exemple, si vous pensez vous situer dans les 10 premiers vous "
              "sélectionnez [1 - 10], si vous pensez vous situer entre la 11ème et la 20ème place vous "
              "sélectionnez [11 - 20] etc. : ",
        choices=C.CLASSEMENT_CHOICES, doc="10 = classement élevé, 1 = classement faible"
    )
    nle_estimation_classement_interval = models.StringField()
    nle_1 = models.FloatField()
    nle_2 = models.FloatField()
    nle_3 = models.FloatField()
    nle_4 = models.FloatField()
    nle_5 = models.FloatField()
    nle_6 = models.FloatField()
    nle_7 = models.FloatField()
    nle_8 = models.FloatField()
    nle_9 = models.FloatField()
    nle_10 = models.FloatField()
    nle_avg_distance = models.FloatField()
    nle_score = models.FloatField()

    def compute_nle_payoff(self):
        targets = C.NLE_VALUES
        differences = [abs(getattr(self, f"nle_{i}") - targets[i - 1]) for i in range(1, C.NB_TARGETS + 1)]
        self.nle_avg_distance = round(statistics.mean(differences), 2)
        self.nle_score = round(C.CONSTANTE - C.FACTEUR_DISTANCE * self.nle_avg_distance, 2)

        txt_final = (f"Votre distance moyenne entre la valeur cible et la position du curseur "
                     f"a été de {self.nle_avg_distance}. Votre gain est donc égal à "
                     f"{self.nle_score}.")
        self.participant.vars[app_name] = dict(
            txt_final=txt_final,
            nle_score=self.nle_score,
            nle_estimation_score_code=self.nle_estimation_score_code,
            nle_estimation_score_interval=self.nle_estimation_score_interval,
            nle_estimation_classement_code=self.nle_estimation_classement_code,
            nle_estimation_classement_interval=self.nle_estimation_classement_interval,
        )


# ======================================================================================================================
#
# -- PAGES
#
# ======================================================================================================================
class MyPage(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(
            estimation_error_percent=int(player.subsession.penalite_erreur_estim * 100),
        )

    @staticmethod
    def js_vars(player: Player):
        return dict(
            fill_auto=player.session.config["fill_auto"],
            **C.__dict__.copy(),
            estimation_error=player.subsession.penalite_erreur_estim,
            estimation_error_percent=int(player.subsession.penalite_erreur_estim * 100)
        )


class Instructions(MyPage):
    pass


class Estimation(MyPage):
    form_model = "player"
    form_fields = ["nle_estimation_score_code", "nle_estimation_classement_code"]

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.participant._is_bot = True
            player.nle_estimation_score_code = random.randint(0, 10)
            player.nle_estimation_classement_code = random.randint(1, 10)

        player.nle_estimation_score_interval = next(
            interval for code, interval in C.SCORE_CHOICES if code == player.nle_estimation_score_code)
        player.nle_estimation_classement_interval = next(
            interval for code, interval in C.CLASSEMENT_CHOICES if code == player.nle_estimation_classement_code)


class Decision(MyPage):
    form_model = "player"
    form_fields = [f"nle_{i}" for i in range(1, C.NB_TARGETS + 1)]

    @staticmethod
    def vars_for_template(player: Player):
        existing = MyPage.vars_for_template(player)
        existing["nle_values"] = player.subsession.nle_values.split("-")
        return existing

    @staticmethod
    def js_vars(player: Player):
        existing = MyPage.js_vars(player)
        existing["nle_values"] = player.subsession.nle_values.split("-")
        return existing

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        if timeout_happened:
            for i in range(1, C.NB_TARGETS + 1):
                setattr(player, f"nle_{i}", round(random.uniform(0, 100), 2))
            player.participant._is_bot = True
        player.compute_nle_payoff()


class Results(MyPage):
    @staticmethod
    def vars_for_template(player: Player):
        existing = MyPage.vars_for_template(player)
        targets = list(map(float, player.subsession.nle_values.split("-")))
        positions = [getattr(player, f"nle_{i}") for i in range(1, C.NB_TARGETS + 1)]
        distances = [round(abs(targets[i] - positions[i]), 2) for i in range(10)]
        targets_numbers = list(zip(targets, positions, distances))
        existing["targets_numbers"] = targets_numbers
        return existing


page_sequence = [
    Instructions,
    Estimation,
    Decision,
    Results
]
