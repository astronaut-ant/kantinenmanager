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


BASE_URL = os.getenv("BASE_URL") or "http://localhost:4200/"
VERWALTUNG_USERNAME, VERWALTUNG_PASSWORD = (
    os.getenv("VERWALTUNG_USERNAME") or "verwaltung",
    os.getenv("VERWALTUNG_PASSWORD") or "password",
)
STANDORT_USERNAME, STANDORT_PASSWORD = (
    os.getenv("STANDORTLEITUNG_USERNAME") or "standortleitung",
    os.getenv("STANDORTLEITUNG_PASSWORD") or "password",
)
GRUPPENLEITUNG_USERNAME, GRUPPENLEITUNG_PASSWORD = os.getenv(
    "GRUPPENLEITUNG_USERNAME"
), os.getenv("GRUPPENLEITUNG_PASSWORD")
KUECHENPERSONAL_USERNAME, KUECHENPERSONAL_PASSWORD = os.getenv(
    "KUECHENPERSONAL_USERNAME"
), os.getenv("KUECHENPERSONAL_PASSWORD")


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.cookies = None

    def login(self):
        res = requests.post(
            BASE_URL + "api/login",
            json={"username": self.username, "password": self.password},
        )
        if res.status_code != 200:
            print(res.json())
            assert False
        self.cookies = res.cookies
        print(f"{self.username}: Logged in with status code {res.status_code}")

    def is_logged_in(self):
        if not self.cookies:
            self.login()
        res = requests.get(BASE_URL + "api/is-logged-in", cookies=self.cookies)
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Is logged in with status code {res.status_code}")

    def logout(self):
        if not self.cookies:
            self.login()
        res = requests.post(BASE_URL + "api/logout", cookies=self.cookies)
        if res.status_code != 204:
            print(res.json())
            assert False
        print(f"{self.username}: Logged out with status code {res.status_code}")
        self.cookies = None


class Verwaltung(User):
    def __init__(self):
        super().__init__(VERWALTUNG_USERNAME, VERWALTUNG_PASSWORD)

    def get_users(self):
        if not self.cookies:
            self.login()
        res = requests.get(BASE_URL + "api/users", cookies=self.cookies)
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} users")
        return res.json()

    def get_group_leaders(self):
        if not self.cookies:
            self.login()
        res = requests.get(BASE_URL + "api/users/group-leaders", cookies=self.cookies)
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} group leaders")

    def get_location_leaders(self):
        if not self.cookies:
            self.login()
        res = requests.get(
            BASE_URL + "api/users/location-leaders", cookies=self.cookies
        )
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} location leaders")

    def create_user(self):
        if not self.cookies:
            self.login()
        username = f"nosferatu{random.randint(0, 100)}"
        res = requests.post(
            BASE_URL + "api/users",
            json={
                "first_name": username.capitalize(),
                "last_name": username.capitalize(),
                "username": username,
                "user_group": "kuechenpersonal",
            },
            cookies=self.cookies,
        )
        if res.status_code == 200:
            # user may already exist
            print(f"{self.username}: Created user {username}")
        return username

    def delete_user(self):
        if not self.cookies:
            self.login()
        username = self.create_user()

        users = self.get_users()
        user = next(u for u in users if u["username"] == username)

        requests.delete(
            BASE_URL + f"api/users/{user['id']}",
            cookies=self.cookies,
        )
        print(f"{self.username}: Deleted user {user['username']}")

    def block_and_unblock_user(self):
        if not self.cookies:
            self.login()
        username = self.create_user()

        users = self.get_users()
        user = next(u for u in users if u["username"] == username)

        res = requests.put(
            BASE_URL + f"api/users/{user['id']}/block",
            cookies=self.cookies,
        )
        print(f"{self.username}: Blocked user {user['username']}")
        if res.status_code != 200:
            print(res.json())
            assert False

        res = requests.put(
            BASE_URL + f"api/users/{user['id']}/unblock",
            cookies=self.cookies,
        )
        print(f"{self.username}: Unblocked user {user['username']}")
        if res.status_code != 200:
            print(res.json())
            assert False

    def get_locations(self):
        if not self.cookies:
            self.login()
        res = requests.get(BASE_URL + "api/locations", cookies=self.cookies)
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} locations")
        return res.json()

    def create_location(self, name: str):
        if not self.cookies:
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
        res = requests.post(
            BASE_URL + "api/locations",
            json={
                "location_name": name,
                "user_id_location_leader": location_leader["id"],
            },
            cookies=self.cookies,
        )
        if res.status_code != 201:
            print(res.json())
            assert False
        print(f"{self.username}: Created location {name}")
        return res.json().get("id")

    def get_groups(self):
        if not self.cookies:
            self.login()
        res = requests.get(BASE_URL + "api/groups", cookies=self.cookies)
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} groups")
        return res.json()

    def get_groups_with_location(self):
        if not self.cookies:
            self.login()
        res = requests.get(BASE_URL + "api/groups/with-locations", cookies=self.cookies)
        if res.status_code != 200:
            print(res.json())
            assert False
        print(f"{self.username}: Got {len(res.json())} groups with location")
        return res.json()

    def create_group(self, name: str, leader: str):
        if not self.cookies:
            self.login()
        groups = self.get_groups()
        group = next((g for g in groups if g["group_name"] == name), None)
        if group:
            print(f"{self.username}: Group {name} already exists")
            return group.get("id")
        location_id = self.create_location("Transsylvanien")
        users = self.get_users()
        leader = next(u for u in users if u["username"] == leader)
        res = requests.post(
            BASE_URL + "api/groups",
            json={
                "group_name": name,
                "group_number": random.randint(1000, 10000),
                "location_id": location_id,
                "user_id_group_leader": leader["id"],
            },
            cookies=self.cookies,
        )
        if res.status_code != 201:
            print(res.json())
            assert False
        print(f"{self.username}: Created group {name}")
        return res.json().get("id")


v = Verwaltung()
v.create_location("Transsylvanien")
v.create_group("Nosferatus Gruppe", "gruppenleitung")

# call a random method on v
while True:
    random.choice(
        [
            v.get_users,
            v.get_group_leaders,
            v.get_location_leaders,
            v.create_user,
            v.delete_user,
            v.block_and_unblock_user,
            v.get_locations,
            v.get_groups,
            v.get_groups_with_location,
        ]
    )()
    sleep(0.1)
