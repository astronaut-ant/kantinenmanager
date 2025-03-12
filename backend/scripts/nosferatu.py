#
#
#     @@@  @@@   @@@@@@    @@@@@@   @@@@@@@@  @@@@@@@@  @@@@@@@    @@@@@@   @@@@@@@  @@@  @@@
#     @@@@ @@@  @@@@@@@@  @@@@@@@   @@@@@@@@  @@@@@@@@  @@@@@@@@  @@@@@@@@  @@@@@@@  @@@  @@@
#     @@!@!@@@  @@!  @@@  !@@       @@!       @@!       @@!  @@@  @@!  @@@    @@!    @@!  @@@
#     @@!!@!@!  !@!  @!@  !@!       !@!       !@!       !@!  @!@  !@!  @!@    !@!    !@!  @!@
#     @!! !!@!  @!@  !@!  !!@@!!    @!!!:!    @!!!:!    @!@!!@!   @!@!@!@!    @!!    @!@  !@!
#     @@!  !!!  !@!  !!!   !!@!!!   !!!!!:    !!!!!:    !!@!@!    !!!@!!!!    !!!    !@!  !!!
#     :!:  !!!  !!:  !!!       !:!  !!:       !!:       !!: :!!   !!:  !!!    !!:    !!:  !!!
#     :!:  !:!  :!:  !:!      !:!   :!:       :!:       :!:  !:!  :!:  !:!    :!:    :!:  !:!
#      ::   ::  ::::: ::  :::: ::    ::        :: ::::  ::   :::  ::   :::     ::    ::::: ::
#     ::    :    : :  :   :: : :     :        : :: ::    :   : :   :   : :     :      : :  :
#
#
# This script is designed to generate a high volume of requests against the API server.
# Warning: This script is not intended for use in production environments. It will
# generate a significant number of requests and may cause performance issues. Once started,
# it will run ad infinitum. You have been warned.
#
# ```bash
# python -O backend/scripts/nosferatu.py
# ```
#

import os
import random
from time import sleep
import requests
import urllib3

urllib3.disable_warnings()

BASE_URL = os.getenv("BASE_URL") or "http://localhost:4200/"
VERWALTUNG_USERNAME, VERWALTUNG_PASSWORD = (
    os.getenv("VERWALTUNG_USERNAME") or "verwaltung",
    os.getenv("VERWALTUNG_PASSWORD") or "password",
)
STANDORT_USERNAME, STANDORT_PASSWORD = (
    os.getenv("STANDORTLEITUNG_USERNAME") or "standortleitung",
    os.getenv("STANDORTLEITUNG_PASSWORD") or "password",
)
KUECHENPERSONAL_USERNAME, KUECHENPERSONAL_PASSWORD = (
    os.getenv("KUECHENPERSONAL_USERNAME") or "küchenpersonal",
    os.getenv("KUECHENPERSONAL_PASSWORD") or "password",
)


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session = requests.Session()
        self.session.verify = False

    def login(self):
        res = self.session.post(
            BASE_URL + "api/login",
            json={"username": self.username, "password": self.password},
        )
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Logged in with status code {res.status_code}")

    def is_logged_in(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(
            BASE_URL + "api/is-logged-in",
            cookies=self.session.cookies,
        )
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Is logged in with status code {res.status_code}")

    def logout(self):
        if not self.session.cookies:
            self.login()
        res = self.session.post(BASE_URL + "api/logout")
        if res.status_code != 204:
            print(res.json())
            assert False
        print(f"{self.username}: Logged out with status code {res.status_code}")


class Verwaltung(User):
    def __init__(self):
        super().__init__(VERWALTUNG_USERNAME, VERWALTUNG_PASSWORD)

    def get_users(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(BASE_URL + "api/users")
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} users")
        return res.json()

    def get_group_leaders(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(BASE_URL + "api/users/group-leaders")
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} group leaders")

    def get_location_leaders(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(BASE_URL + "api/users/location-leaders")
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} location leaders")

    def create_user(self):
        if not self.session.cookies:
            self.login()
        username = f"nosferatu{random.randint(0, 9)}"
        res = self.session.post(
            BASE_URL + "api/users",
            json={
                "first_name": username.capitalize(),
                "last_name": username.capitalize(),
                "username": username,
                "user_group": "kuechenpersonal",
            },
            cookies=self.session.cookies,
        )
        if res.status_code == 200:
            # user may already exist
            print(f"{self.username}: Created user {username}")
        return username

    def delete_user(self):
        if not self.session.cookies:
            self.login()
        username = self.create_user()

        users = self.get_users()
        user = next(u for u in users if u["username"] == username)

        self.session.delete(
            BASE_URL + f"api/users/{user['id']}",
            cookies=self.session.cookies,
        )
        print(f"{self.username}: Deleted user {user['username']}")

    def block_and_unblock_user(self):
        if not self.session.cookies:
            self.login()
        username = self.create_user()

        users = self.get_users()
        user = next(u for u in users if u["username"] == username)

        res = self.session.put(
            BASE_URL + f"api/users/{user['id']}/block",
            cookies=self.session.cookies,
        )
        print(f"{self.username}: Blocked user {user['username']}")
        if res.status_code != 200:
            print(res.json())
            assert False

        res = self.session.put(
            BASE_URL + f"api/users/{user['id']}/unblock",
            cookies=self.session.cookies,
        )
        print(f"{self.username}: Unblocked user {user['username']}")
        if res.status_code != 200:
            print(res.json())
            assert False

    def get_locations(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(BASE_URL + "api/locations")
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} locations")
        return res.json()

    def create_location(self, name: str):
        if not self.session.cookies:
            self.login()
        locations = self.get_locations()
        loc = next((l for l in locations if l["location_name"] == name), None)
        if loc:
            print(f"{self.username}: Location {name} already exists")
            return loc.get("id")
        users = self.get_users()
        location_leader = next(
            (u for u in users if u["username"] == STANDORT_USERNAME), None
        )
        res = self.session.post(
            BASE_URL + "api/locations",
            json={
                "location_name": name,
                "user_id_location_leader": location_leader["id"],
            },
            cookies=self.session.cookies,
        )
        if res.status_code != 201:
            print(res.json())
            assert False
        print(f"{self.username}: Created location {name}")
        return res.json().get("id")

    def get_groups(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(BASE_URL + "api/groups")
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} groups")
        return res.json()

    def get_groups_with_location(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(BASE_URL + "api/groups/with-locations")
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} groups with location")
        return res.json()

    def get_dish_prices(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(BASE_URL + "api/dish_prices")
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} dish prices")

    def get_employees(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(BASE_URL + "api/employees")
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} employees")

    def get_employee_qr_codes(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(BASE_URL + "api/employees/qr-codes")
        if res.status_code != 200 and res.status_code != 404:
            print(res.json())
            assert False
        assert res.headers["Content-Type"] == "application/pdf"
        print(f"{self.username}: Got employee qr codes")

    def get_health(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(BASE_URL + "api/health")
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got health")

    def get_preorders(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(BASE_URL + "api/pre-orders")
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} preorders")

    def get_daily_orders(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(BASE_URL + "api/daily-orders")
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} daily orders")

    def get_old_orders(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(BASE_URL + "api/old-orders")
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} old orders")


class Standortleitung(User):
    def __init__(self):
        super().__init__(STANDORT_USERNAME, STANDORT_PASSWORD)

    def get_preorders(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(BASE_URL + "api/pre-orders")
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} preorders")

    def get_daily_orders(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(BASE_URL + "api/daily-orders")
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} daily orders")


class Kuechenpersonal(User):
    def __init__(self):
        super().__init__(KUECHENPERSONAL_USERNAME, KUECHENPERSONAL_PASSWORD)

    def get_daily_orders(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(BASE_URL + "api/daily-orders")
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} daily orders")

    def get_daily_orders_counted(self):
        if not self.session.cookies:
            self.login()
        res = self.session.get(BASE_URL + "api/daily-orders/counted")
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} daily orders counted")


v = Verwaltung()
v.is_logged_in()

v.create_location("Transsylvanien")
s = Standortleitung()
k = Kuechenpersonal()


# call a random method on v
while True:
    random.choice(
        [
            v.is_logged_in,
            v.logout,
            v.get_users,
            v.get_group_leaders,
            v.get_location_leaders,
            v.create_user,
            v.delete_user,
            v.block_and_unblock_user,
            v.get_locations,
            v.get_groups,
            v.get_groups_with_location,
            v.get_dish_prices,
            v.get_employees,
            v.get_employee_qr_codes,
            v.get_health,
            v.get_preorders,
            v.get_daily_orders,
            v.get_old_orders,
            s.is_logged_in,
            s.logout,
            s.get_preorders,
            s.get_daily_orders,
            k.is_logged_in,
            k.logout,
            k.get_daily_orders,
            k.get_daily_orders_counted,
        ]
    )()
    sleep(0.1)
