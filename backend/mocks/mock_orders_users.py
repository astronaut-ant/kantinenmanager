from datetime import timedelta

from src.models.maindish import MainDish

_TIME_DELTA_1 = timedelta(days=1)
_TIME_DELTA_2 = timedelta(days=2)
_TIME_DELTA_3 = timedelta(days=3)
_TIME_DELTA_4 = timedelta(days=4)

MOCK_ORDERS_USERS = [
    {
        "timedelta": _TIME_DELTA_1,
        "orders": [
            {
                "user": "verwaltung",
                "main_dish": MainDish.rot,
                "salad_option": True,
                "nothing": False,
            },
            {
                "user": "standortleitung",
                "main_dish": None,
                "salad_option": False,
                "nothing": True,
            },
            {
                "user": "gruppenleitung",
                "main_dish": MainDish.rot,
                "salad_option": False,
                "nothing": False,
            },
            {
                "user": "albus_dumbledore",
                "main_dish": MainDish.rot,
                "salad_option": True,
                "nothing": False,
            },
            {
                "user": "severus_snape",
                "main_dish": None,
                "salad_option": False,
                "nothing": True,
            },
            {
                "user": "minerva_mcgonagall",
                "main_dish": MainDish.blau,
                "salad_option": True,
                "nothing": False,
            },
            {
                "user": "pomona_sprout",
                "main_dish": None,
                "salad_option": False,
                "nothing": True,
            },
            {
                "user": "filius_flitwick",
                "main_dish": MainDish.blau,
                "salad_option": False,
                "nothing": False,
            },
            {
                "user": "argus_filch",
                "main_dish": MainDish.rot,
                "salad_option": True,
                "nothing": False,
            },
            {
                "user": "rubeus_hagrid",
                "main_dish": None,
                "salad_option": False,
                "nothing": True,
            },
            {
                "user": "vernon_dursley",
                "main_dish": MainDish.rot,
                "salad_option": False,
                "nothing": False,
            },
            {
                "user": "madam_rosmerta",
                "main_dish": None,
                "salad_option": True,
                "nothing": False,
            },
            {
                "user": "cornelius_fudge",
                "main_dish": MainDish.rot,
                "salad_option": False,
                "nothing": False,
            },
            {
                "user": "harry_potter",
                "main_dish": None,
                "salad_option": True,
                "nothing": False,
            },
        ],
    },
    {
        "timedelta": _TIME_DELTA_2,
        "orders": [
            {
                "user": "verwaltung",
                "main_dish": MainDish.rot,
                "salad_option": True,
                "nothing": False,
            },
            {
                "user": "standortleitung",
                "main_dish": None,
                "salad_option": False,
                "nothing": True,
            },
            {
                "user": "gruppenleitung",
                "main_dish": MainDish.blau,
                "salad_option": False,
                "nothing": False,
            },
            {
                "user": "albus_dumbledore",
                "main_dish": MainDish.rot,
                "salad_option": True,
                "nothing": False,
            },
            {
                "user": "severus_snape",
                "main_dish": None,
                "salad_option": False,
                "nothing": True,
            },
            {
                "user": "minerva_mcgonagall",
                "main_dish": MainDish.rot,
                "salad_option": True,
                "nothing": False,
            },
            {
                "user": "pomona_sprout",
                "main_dish": None,
                "salad_option": False,
                "nothing": True,
            },
            {
                "user": "filius_flitwick",
                "main_dish": MainDish.blau,
                "salad_option": False,
                "nothing": False,
            },
            {
                "user": "argus_filch",
                "main_dish": MainDish.rot,
                "salad_option": True,
                "nothing": False,
            },
            {
                "user": "rubeus_hagrid",
                "main_dish": None,
                "salad_option": False,
                "nothing": True,
            },
            {
                "user": "vernon_dursley",
                "main_dish": MainDish.blau,
                "salad_option": False,
                "nothing": False,
            },
            {
                "user": "madam_rosmerta",
                "main_dish": MainDish.blau,
                "salad_option": True,
                "nothing": False,
            },
            {
                "user": "bathilda_bagshot",
                "main_dish": MainDish.blau,
                "salad_option": True,
                "nothing": False,
            },
            {
                "user": "voldemort",
                "main_dish": None,
                "salad_option": False,
                "nothing": True,
            },
            {
                "user": "harry_potter",
                "main_dish": None,
                "salad_option": True,
                "nothing": False,
            },
        ],
    },
    {
        "timedelta": _TIME_DELTA_3,
        "orders": [
            {
                "user": "verwaltung",
                "main_dish": MainDish.rot,
                "salad_option": True,
                "nothing": False,
            },
            {
                "user": "standortleitung",
                "main_dish": None,
                "salad_option": False,
                "nothing": True,
            },
            {
                "user": "gruppenleitung",
                "main_dish": MainDish.blau,
                "salad_option": False,
                "nothing": False,
            },
            {
                "user": "albus_dumbledore",
                "main_dish": MainDish.rot,
                "salad_option": True,
                "nothing": False,
            },
            {
                "user": "severus_snape",
                "main_dish": None,
                "salad_option": False,
                "nothing": True,
            },
            {
                "user": "minerva_mcgonagall",
                "main_dish": MainDish.blau,
                "salad_option": True,
                "nothing": False,
            },
            {
                "user": "pomona_sprout",
                "main_dish": None,
                "salad_option": False,
                "nothing": True,
            },
            {
                "user": "filius_flitwick",
                "main_dish": MainDish.rot,
                "salad_option": False,
                "nothing": False,
            },
            {
                "user": "argus_filch",
                "main_dish": MainDish.blau,
                "salad_option": True,
                "nothing": False,
            },
            {
                "user": "rubeus_hagrid",
                "main_dish": None,
                "salad_option": False,
                "nothing": True,
            },
            {
                "user": "vernon_dursley",
                "main_dish": MainDish.rot,
                "salad_option": False,
                "nothing": False,
            },
            {
                "user": "madam_rosmerta",
                "main_dish": None,
                "salad_option": True,
                "nothing": False,
            },
            {
                "user": "bathilda_bagshot",
                "main_dish": MainDish.blau,
                "salad_option": True,
                "nothing": False,
            },
            {
                "user": "voldemort",
                "main_dish": None,
                "salad_option": False,
                "nothing": True,
            },
            {
                "user": "cornelius_fudge",
                "main_dish": MainDish.rot,
                "salad_option": False,
                "nothing": False,
            },
            {
                "user": "harry_potter",
                "main_dish": None,
                "salad_option": True,
                "nothing": False,
            },
        ],
    },
]
