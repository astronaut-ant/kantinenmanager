from datetime import datetime, timedelta

from src.models.maindish import MainDish

_BASE = datetime.now().date()
_TIME_DELTA_1 = timedelta(days=0)
_TIME_DELTA_2 = timedelta(days=1)
_TIME_DELTA_3 = timedelta(days=3)
_TIME_DELTA_4 = timedelta(days=5)

MOCK_ORDERS_USERS = [
    {
        "user": "linus_torvalds",
        "timedelta": _TIME_DELTA_1,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "linus_torvalds",
        "timedelta": _TIME_DELTA_2,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "linus_torvalds",
        "timedelta": _TIME_DELTA_3,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "linus_torvalds",
        "timedelta": _TIME_DELTA_4,
        "main_dish": None,
        "salad_option": False,
    },
    {
        "user": "ada_lovelace",
        "timedelta": _TIME_DELTA_1,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "ada_lovelace",
        "timedelta": _TIME_DELTA_2,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "charles_babbage",
        "timedelta": _TIME_DELTA_1,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "charles_babbage",
        "timedelta": _TIME_DELTA_3,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "standortleitung",
        "timedelta": _TIME_DELTA_2,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "grace_hopper",
        "timedelta": _TIME_DELTA_1,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "alan_turing",
        "timedelta": _TIME_DELTA_3,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "donald_knuth",
        "timedelta": _TIME_DELTA_4,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "gruppenleitung",
        "timedelta": _TIME_DELTA_1,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "alan_kay",
        "timedelta": _TIME_DELTA_2,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "denis_ritchie",
        "timedelta": _TIME_DELTA_3,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "ken_thompson",
        "timedelta": _TIME_DELTA_4,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "margaret_hamilton",
        "timedelta": _TIME_DELTA_1,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "barbara_liskov",
        "timedelta": _TIME_DELTA_2,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "brendan_eich",
        "timedelta": _TIME_DELTA_3,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "haskell_curry",
        "timedelta": _TIME_DELTA_4,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "john_von_neumann",
        "timedelta": _TIME_DELTA_1,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "küchenpersonal",
        "timedelta": _TIME_DELTA_2,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "bjarne_stroustrup",
        "timedelta": _TIME_DELTA_3,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "tim_berners_lee",
        "timedelta": _TIME_DELTA_4,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "edsger_dijkstra",
        "timedelta": _TIME_DELTA_1,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
]
