from otree.api import *
from pathlib import Path
import random
import pandas as pd

app_name = Path(__file__).parent.name

doc = """
Ecran final. <br/>
Place les participants en attente, puis lorsque tous arrivent à cette application effectue les calculs de scores. <br/>
Détermine ensuite les gagnants.
"""


class C(BaseConstants):
    NAME_IN_URL = 'highschool_final'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    nb_paids = models.IntegerField()

    def compute_payoffs(self):
        if self.session.config.get("test", False):
            players = self.get_players()
        else:
            players = [p for p in self.get_players() if not p.participant._is_bot]

        for p in players:
            others = [o for o in players if o != p]
            others_for_comparison = random.sample(others, min(99, len(others)))
            p.compute_payoff(others_for_comparison)

        # maintenant on détermine les nb_paids premiers
        sorted_scores = sorted([(p, p.nle_score_final) for p in players], key=lambda x: x[1], reverse=True)
        paid_players = [p for p, _ in sorted_scores[:self.nb_paids]]
        for p in players:
            p.paid = p in paid_players
            p.participant.vars["highschool_final"]["txt_paid"] = (
                f"Votre score final fait partie des {self.nb_paids} meilleurs, vous allez donc recevoir un cadeau."
                if p.paid else f"Votre score final ne fait pas partie des {self.nb_paids} meilleurs."
            )

def vars_for_admin_report(subsession: Subsession):
    infos_players = []
    players = subsession.get_players() if subsession.session.config.get("test", False) else \
        [p for p in subsession.get_players() if not p.participant._is_bot]
    for p in players:
        infos_players.append(
            dict(
                code=p.participant.code,
                label=p.participant.label,
                nle_score_final=round(p.nle_score_final, 2),
                paid=p.paid,
            )
        )
    return dict(infos_players=infos_players)


def creating_session(subsession: Subsession):
    subsession.nb_paids = min(len(subsession.get_players()) // 2, subsession.session.config['nb_paids'])


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    nle_score_effectif_code = models.IntegerField()
    nle_score_effectif_interval = models.StringField()
    nle_diff_score = models.FloatField()
    nle_classement_effectif_code = models.IntegerField()
    nle_classement_effectif_interval = models.StringField()
    nle_diff_classement = models.IntegerField()
    nle_score_final = models.FloatField(initial=0)
    paid = models.BooleanField(initial=False)

    def compute_payoff(self, others_for_comparison):
        self.participant.vars["highschool_final"] = dict()

        score_effectif = float(self.participant.vars["highschool_nle"]["nle_score"])
        self.participant.vars["highschool_final"]["txt_score"] = f"Votre score au jeu a été de {score_effectif:.2f}."

        # différence entre intervalle de score estimé et intervalle de score réel --------------------------------------
        estimation_score_code = self.participant.vars["highschool_nle"]['nle_estimation_score_code']
        estimation_score_interval = self.participant.vars["highschool_nle"]['nle_estimation_score_interval']
        bins_scores = [0, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 101]  # Bornes des intervalles
        labels_scores = list(range(0, 11))  # Codes associés à chaque intervalle
        df_score = pd.DataFrame({'score_effectif': [score_effectif]})
        df_score['interval_name'] = pd.cut(df_score['score_effectif'], bins=bins_scores, right=False).astype(object)
        df_score['interval_code'] = pd.cut(df_score['score_effectif'], bins=bins_scores, labels=labels_scores,
                                           right=False).astype(float)
        self.nle_score_effectif_code = int(df_score['interval_code'].iloc[0])
        self.nle_score_effectif_interval = str(df_score['interval_name'].iloc[0])
        self.nle_diff_score = abs(estimation_score_code - self.nle_score_effectif_code)
        self.nle_score_final = max(0, score_effectif - (score_effectif * self.session.config["penalite_erreur_estim"] *
                                                        self.nle_diff_score))
        self.participant.vars["highschool_final"]["txt_estim_abs"] = (
            f"Vous aviez estimé un score compris dans l'intervalle {estimation_score_interval}. "
            f"Votre score effectif est dans l'intervalle "
            f"{self.nle_score_effectif_interval}, soit une "
            f"différence de {self.nle_diff_score} intervalle(s). "
            f"Votre score a donc été diminué de {self.nle_diff_score} x "
            f"{int(self.session.config['penalite_erreur_estim'] * 100)} %.")

        # différence entre intervalle de classement estimé et intervalle de classement réel ----------------------------
        estimation_classement_code = self.participant.vars["highschool_nle"]['nle_estimation_classement_code']
        estimation_classement_choices = [(10 - i, (e, e + 9)) for i, e in enumerate(range(1, 100, 10))]
        estimation_classement_interval = self.participant.vars["highschool_nle"]['nle_estimation_classement_interval']
        others_scores = sorted(
            [float(o.participant.vars["highschool_nle"]["nle_score"]) for o in others_for_comparison] + [
                score_effectif], reverse=True)
        player_rank = others_scores.index(score_effectif) + 1  # 1 = premier, 100 = dernier
        df_rank = pd.DataFrame({'rank': [player_rank]})
        rank_bins = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]  # 102 car rang 101 possible
        rank_labels = list(range(10, 0, -1))  # Les codes des intervalles (de 10 à 1)
        df_rank['rank_code'] = pd.cut(df_rank['rank'], bins=rank_bins, labels=rank_labels, right=True,
                                      include_lowest=True).astype(float)
        df_rank['rank_name'] = pd.cut(df_rank['rank'], bins=rank_bins, right=True, include_lowest=True).astype(object)
        self.nle_classement_effectif_code = int(df_rank['rank_code'].iloc[0])
        classement_intervalle_effectif_values = next(
            (min_val, max_val) for code, (min_val, max_val) in estimation_classement_choices if
            code == self.nle_classement_effectif_code)
        self.nle_classement_effectif_interval = f"[{classement_intervalle_effectif_values[0]} - {classement_intervalle_effectif_values[1]}]"
        self.nle_diff_classement = abs(estimation_classement_code - self.nle_classement_effectif_code)
        self.nle_score_final = max(0, self.nle_score_final - (self.nle_score_final * self.session.config[
            "penalite_erreur_estim"] * self.nle_diff_classement))

        self.participant.vars["highschool_final"]["txt_estim_rel"] = (
            f"Vous aviez estimé un classement compris dans l'intervalle "
            f"{estimation_classement_interval}. "
            f"Votre classement effectif est dans l'intervalle "
            f"{self.nle_classement_effectif_interval}, soit une "
            f"différence de {self.nle_diff_classement} intervalle(s). "
            f"Votre score a donc été diminué de {self.nle_diff_classement} x "
            f"{int(self.session.config['penalite_erreur_estim'] * 100)} %.")

        self.participant.vars["highschool_final"][
            "txt_score_final"] = f"Votre score final est de {self.nle_score_final:.2f}."


# PAGES
class MyPage(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict()

    @staticmethod
    def js_vars(player: Player):
        return dict(**C.__dict__.copy())


class FinalWaitForAll(WaitPage):
    wait_for_all_groups = True
    body_text = ("Le programme informatique attend que tous les participants aient terminé, pour faire les "
                 "classements et calculer le score final de chacun.")

    @staticmethod
    def after_all_players_arrive(subsession: Subsession):
        subsession.compute_payoffs()


class Final(MyPage):
    pass


page_sequence = [FinalWaitForAll, Final]
