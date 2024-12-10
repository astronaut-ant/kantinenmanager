from datetime import datetime, timedelta

from src.models.maindish import MainDish

_BASE = datetime.now().date()
_DATE1 = _BASE + timedelta(days=2)
_DATE2 = _BASE + timedelta(days=3)
_DATE3 = _BASE + timedelta(days=5)
_DATE4 = _BASE + timedelta(days=7)

MOCK_ORDERS_USERS = [
    {
        "user": "linus_torvalds",
        "date": _DATE1,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "linus_torvalds",
        "date": _DATE2,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "linus_torvalds",
        "date": _DATE3,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "linus_torvalds",
        "date": _DATE4,
        "main_dish": None,
        "salad_option": False,
    },
    {
        "user": "ada_lovelace",
        "date": _DATE1,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "ada_lovelace",
        "date": _DATE2,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "charles_babbage",
        "date": _DATE1,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "charles_babbage",
        "date": _DATE3,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "standortleitung",
        "date": _DATE2,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "grace_hopper",
        "date": _DATE1,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "alan_turing",
        "date": _DATE3,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "donald_knuth",
        "date": _DATE4,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "gruppenleitung",
        "date": _DATE1,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "alan_kay",
        "date": _DATE2,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "denis_ritchie",
        "date": _DATE3,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "ken_thompson",
        "date": _DATE4,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "margaret_hamilton",
        "date": _DATE1,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "barbara_liskov",
        "date": _DATE2,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "brendan_eich",
        "date": _DATE3,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "haskell_curry",
        "date": _DATE4,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "john_von_neumann",
        "date": _DATE1,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "küchenpersonal",
        "date": _DATE2,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "bjarne_stroustrup",
        "date": _DATE3,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
    {
        "user": "tim_berners_lee",
        "date": _DATE4,
        "main_dish": MainDish.blau,
        "salad_option": False,
    },
    {
        "user": "edsger_dijkstra",
        "date": _DATE1,
        "main_dish": MainDish.rot,
        "salad_option": True,
    },
]
