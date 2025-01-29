from typing import List
from uuid import UUID

from src.models.dailyorder import DailyOrder
from src.models.maindish import MainDish
from src.models.user import UserGroup
from src.repositories.groups_repository import GroupsRepository
from src.repositories.orders_repository import OrdersRepository
from src.repositories.users_repository import UsersRepository
from src.schemas.daily_orders_schema import DailyOrderFullSchema
from src.utils.exceptions import AccessDeniedError, NotFoundError, BadValueError


class DailyOrdersService:
    """Service to manage daily orders"""

    @staticmethod
    def get_daily_order(person_id: UUID, user_id: UUID) -> DailyOrder:
        """Get daily order for a person"""

        order = OrdersRepository.get_daily_order_by_person_id(person_id)
        if not order:
            raise NotFoundError(f"Bestellung für Person '{person_id}'")

        user = UsersRepository.get_user_by_id(user_id)

        if not user:
            raise NotFoundError(f"Nutzer:in {person_id}")

        if order.location_id != user.location_id:
            raise AccessDeniedError(
                resssource=f"Person {person_id}",
                details=f" auf Standort {user.location_id}",
            )

        return order

    @staticmethod
    def update_daily_order(
        daily_order_id: UUID, handed_out: bool, user_id: UUID
    ) -> DailyOrder:
        """Update daily order"""

        order = OrdersRepository.get_daily_order_by_id(daily_order_id)
        if not order:
            raise NotFoundError(f"Bestellung {daily_order_id}")

        user = UsersRepository.get_user_by_id(user_id)

        if not user:
            raise NotFoundError(f"Nutzer {order.person_id}")

        if order.location_id != user.location_id:
            raise AccessDeniedError(
                ressource=f"Person {order.person_id}",
                details=f" auf Standort {user.location_id}",
            )

        if order["nothing"] == True and (order["main_dish"] or order["salad_option"]):
            raise BadValueError(
                "Wenn 'nichts' ausgewählt ist, dürfen keine Essensoptionen ausgewählt werden."
            )

        order.handed_out = handed_out

        OrdersRepository.update_order()

        return order

    @staticmethod
    def get_daily_orders_filtered_by_user_scope(user_id: UUID) -> List[DailyOrder]:
        """Get daily orders filtered by user scope"""

        return OrdersRepository.get_daily_orders_filtered_by_user_scope(user_id)

    @staticmethod
    def get_daily_orders_for_group(group_id: UUID, user_id: UUID) -> List[DailyOrder]:
        """Get daily orders for a group

        :param group_id: UUID

        :return: Daily orders in a response schmea
        """

        group = GroupsRepository.get_group_by_id(group_id)

        if not group:
            raise NotFoundError(f"Gruppe mit ID {group_id}")
        if (
            user_id != group.user_id_group_leader
            and user_id != group.user_id_replacement
        ):
            raise AccessDeniedError(
                f"Zugriff verweigert. Gruppe {group_id} gehört nicht zu Nutzer {user_id}"
            )

        return OrdersRepository.get_daily_orders_for_group(group_id, user_id)

    @staticmethod
    def create_daily_orders(
        orders: List[DailyOrder],
    ) -> List[DailyOrderFullSchema]:
        """Create daily orders in bulk

        :param orders: List of orders

        :return: List of daily orders in a response schema
        """

        OrdersRepository.create_daily_orders(orders)
        return DailyOrderFullSchema(many=True).dump(orders)

    ##################### test method  #####################

    @staticmethod
    def get_all_daily_orders() -> List[DailyOrder]:
        return OrdersRepository.get_all_daily_orders()
