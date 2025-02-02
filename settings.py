from os import environ

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')
DEMO_PAGE_INTRO_HTML = """ """
SECRET_KEY = '2676806118113'

LANGUAGE_CODE = 'fr'
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = False
PARTICIPANT_FIELDS = []
SESSION_FIELDS = []

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00,
    participation_fee=0.00,
    fill_auto=False,
    test=False,
)

SESSION_CONFIGS = [
    dict(
        name='high_school_pre_conf',
        app_sequence=['highschool_welcome', 'highschool_nle', "highschool_survey", "highschool_final"],
        num_demo_participants=5,
        nb_paids=125,
        penalite_erreur_estim=0.1,
        test=True,
        post_conf=False
    ),
    dict(
        name='high_school_post_conf',
        app_sequence=['highschool_welcome', 'highschool_nle', "highschool_survey", "highschool_final"],
        num_demo_participants=5,
        nb_paids=125,
        penalite_erreur_estim=0.1,
        test=True,
        post_conf=True
    ),
]
