from datetime import datetime, timedelta, time
from typing import List, Optional
from uuid import UUID
import pytz

from src.repositories.employees_repository import EmployeesRepository
from src.repositories.groups_repository import GroupsRepository
from src.repositories.users_repository import UsersRepository
from src.schemas.pre_orders_schemas import PreOrderFullSchema, PreOrdersByGroupLeaderSchema
from src.models.preorder import PreOrder
from src.models.maindish import MainDish
from src.models.user import UserGroup
from src.repositories.orders_repository import OrdersFilters, OrdersRepository
from src.utils.exceptions import NotFoundError, ActionNotPossibleError, AccessDeniedError, BadValueError, AlreadyExistsError

timezone = pytz.timezone("Europe/Berlin")


class PreOrdersService:
    """
    Service class for orders
    """

    @staticmethod
    def get_pre_order_by_id(id: int) -> Optional[PreOrderFullSchema]:
        """
        Get pre order by id
        """

        preorder = OrdersRepository.get_pre_order_by_id(id)

        if not preorder:
            return None

        return PreOrderFullSchema().dump(preorder)

    @staticmethod
    def get_pre_orders_by_group_leader(
        person_id: UUID, request_user_id: UUID, request_user_group: UserGroup
    ):
        """
        Get pre orders by person id of th group leader
        """

        group_leader = UsersRepository.get_user_by_id(person_id)

        if not group_leader:
            raise NotFoundError(f"Gruppenleitung mit ID {person_id}")

        if group_leader.user_group != UserGroup.gruppenleitung:
            raise AccessDeniedError("Gruppen, da keine Gruppenleitung")

        groups = GroupsRepository.get_groups_by_group_leader(person_id)

        def add_orders_to_group(group):
            group = dict(group)
            group["employees"] = EmployeesRepository.get_employees_by_user_scope(
                user_group=request_user_group,
                user_id=request_user_id,
                group_id=group["id"],
            )
            group["orders"] = OrdersRepository.get_pre_orders(
                OrdersFilters(group_id=group["id"])
            )
            return group

        groups = list(map(add_orders_to_group, groups))

        group_leader = group_leader.to_dict_without_pw_hash()
        group_leader["groups"] = groups

        return PreOrdersByGroupLeaderSchema().dump(group_leader)

    @staticmethod
    def get_pre_orders(filters: OrdersFilters) -> List[PreOrderFullSchema]:
        """
        Get orders
        :param filters: Filters for orders
        :return: List of orders
        """

        preorders = OrdersRepository.get_pre_orders(filters)
        return PreOrderFullSchema(many=True).dump(preorders)

    @staticmethod
    def create_update_bulk_preorders(orders: List[dict], user_id: UUID):
        """
        Create orders for employees in bulk

        :param orders: List of orders
        :param group_id: Group id of the user

        :return: List of order ids
        """

        bulk_orders = []
        employee_ids = OrdersRepository.get_employees_to_order_for(user_id)

        today = datetime.now(timezone).date()
        current_time = datetime.now(timezone).time()

        for order in orders:
            if order["date"] < today:
                raise BadValueError(f"Datum {order['date']} liegt in der Vergangenheit.")

            if order["date"] > today + timedelta(days=14):
                raise BadValueError(
                    f"Datum {order['date']} liegt mehr als 14 Tage in der Zukunft."
                )

            if order["date"] == today and current_time >= time(8, 0):
                raise BadValueError(
                    f"Es ist nach 8 Uhr. Bestellungen sind nicht mehr möglich."
                )

            if order["date"].weekday() >= 5:  # 0 = Montag, 6 = Sonntag
                raise BadValueError(f"Datum {order['date']} ist kein Werktag.")

            if order["person_id"] not in employee_ids:
                raise ActionNotPossibleError(
                    f"Mitarbeiter:in {order["person_id"]} gehört zu keiner der Gruppen von {user_id}"
                )

            if not OrdersRepository.employee_in_location(
                order["person_id"], order["location_id"]
            ):
                raise ActionNotPossibleError(
                    f"Person {order["person_id"]} gehört nicht zum Standort {order["location_id"]}"
                )

            if order["nothing"] == True and (
                order["main_dish"] or order["salad_option"]
            ):
                raise BadValueError(
                    "Wenn 'nichts' ausgewählt ist, dürfen keine Essensoptionen ausgewählt werden."
                )

            # Überprüfen, ob die Bestellung bereits existiert. Falls ja, aktualisiere oder lösche diese
            order_exists = OrdersRepository.preorder_already_exists(
                order["person_id"], order["date"]
            )

            if order_exists:
                order_exists.nothing = order["nothing"]
                order_exists.main_dish = order["main_dish"]
                order_exists.salad_option = order["salad_option"]
                order_exists.location_id = order["location_id"]
                OrdersRepository.update_order()
            else:
                bulk_orders.append(PreOrder(**order))

        OrdersRepository.create_bulk_orders(bulk_orders)

    @staticmethod
    def create_preorder_user(order: dict, user_id: UUID) -> PreOrderFullSchema:
        """
        Create preorder for user

        :param order: Order
        :param group_id: Group id of the user

        :return: New order
        """

        today = datetime.now(timezone).date()
        current_time = datetime.now(timezone).time()

        if OrdersRepository.preorder_already_exists(order["person_id"], order["date"]):
            raise AlreadyExistsError(
                f"Bestellung für {order['person_id']} am {order['date']}"
            )

        if order["date"] < today:
            raise BadValueError(f"Das Datum {order['date']} liegt in der Vergangenheit.")

        if order["date"] > today + timedelta(days=14):
            raise BadValueError(
                f"Das Datum {order['date']} liegt mehr als 14 Tage in der Zukunft."
            )

        if order["date"] == today and current_time >= time(8, 0):
            raise BadValueError(
                f"Es ist nach 8 Uhr. Bestellungen sind nicht mehr möglich."
            )

        if order["date"].weekday() >= 5:  # 0 = Montag, 6 = Sonntag
            raise BadValueError(f"Das Datum {order['date']} ist kein Werktag.")

        if user_id != order["person_id"]:
            raise AccessDeniedError(f"Person {order['person_id']}'")

        if order["nothing"] == True and (order["main_dish"] or order["salad_option"]):
            raise BadValueError(
                "Wenn 'nichts' ausgewählt ist, dürfen keine Essensoptionen ausgewählt werden."
            )

        order = OrdersRepository.create_single_order(PreOrder(**order))

        return PreOrderFullSchema().dump(order)

    @staticmethod
    def update_preorder_user(
        new_order: dict, preorder_id: UUID, user_id: UUID
    ) -> PreOrderFullSchema:
        """
        Update preorder for user

        :param new_order: dict
        :param preorder_id: new_order id
        :param user_id: User id

        :return: Order id
        """

        today = datetime.now(timezone).date()
        current_time = datetime.now(timezone).time()

        if new_order["date"] < today:
            raise BadValueError(
                f"Das Datum {new_order['date']} liegt in der Vergangenheit."
            )

        if new_order["date"] > today + timedelta(days=14):
            raise BadValueError(
                f"Das Datum {new_order['date']} liegt mehr als 14 Tage in der Zukunft."
            )

        if new_order["date"].weekday() >= 5:
            raise BadValueError(f"Das Datum {new_order['date']} ist kein Werktag.")

        if new_order["date"] == today and current_time >= time(8, 0):
            raise BadValueError(
                f"Es ist nach 8 Uhr. Bestellungen sind nicht mehr möglich."
            )

        if user_id != new_order["person_id"]:
            raise AccessDeniedError(f"Person'{new_order['person_id']}'")

        if new_order["nothing"] == True and (
            new_order["main_dish"] or new_order["salad_option"]
        ):
            raise BadValueError(
                "Wenn 'nichts' ausgewählt ist, dürfen keine Essensoptionen ausgewählt werden."
            )

        old_order = OrdersRepository.get_pre_order_by_id(preorder_id)
        if not old_order:
            raise NotFoundError(f"Bestellung {preorder_id}")

        old_order.nothing = new_order["nothing"]
        old_order.date = new_order["date"]
        old_order.main_dish = new_order["main_dish"]
        old_order.salad_option = new_order["salad_option"]
        OrdersRepository.update_order()

        return PreOrderFullSchema().dump(old_order)

    @staticmethod
    def delete_preorder_user(preorder_id: UUID, user_id: UUID):
        """
        Delete preorder for user

        :param preorder_id: Preorder id
        :param user_id: User id
        """
        preorder = OrdersRepository.get_pre_order_by_id(preorder_id)
        if not preorder:
            raise NotFoundError(f"Bestellung {preorder_id}")
        if user_id != preorder.person_id:
            raise AccessDeniedError(f"Person {preorder.person_id}")
        OrdersRepository.delete_order(preorder)
