from typing import List
from uuid import UUID
from marshmallow import Schema, fields
from src.schemas.daily_orders_schema import DailyOrderFullSchema
from src.models.maindish import MainDish
from src.models.dailyorder import DailyOrder
from src.repositories.users_repository import UsersRepository
from src.repositories.orders_repository import OrdersRepository
from src.repositories.locations_repository import LocationsRepository
from src.utils.exceptions import NotFoundError, WrongLocationError


class DailyOrdersService:
    """Service to manage daily orders"""

    @staticmethod
    def get_daily_order(person_id: UUID, user_id: UUID) -> DailyOrderFullSchema:
        """Get daily order for a person"""

        order = OrdersRepository.get_daily_order_by_person_id(person_id)
        if not order:
            raise NotFoundError(f"Bestellung für Person '{person_id}' nicht gefunden.")

        user = UsersRepository.get_user_by_id(user_id)

        if not user:
            raise ValueError(f"Nutzer {person_id} existiert nicht.")

        if order.location_id != user.location_id:
            raise WrongLocationError(
                f"Person {person_id} gehört nicht zum Standort {user.location_id}"
            )

        return DailyOrderFullSchema().dump(order)

    @staticmethod
    def update_daily_order(
        daily_order_id: UUID, handed_out: bool, user_id: UUID
    ) -> DailyOrderFullSchema:
        """Update daily order"""

        order = OrdersRepository.get_daily_order_by_id(daily_order_id)
        if not order:
            raise NotFoundError(f"Bestellung '{daily_order_id}' nicht gefunden.")

        user = UsersRepository.get_user_by_id(user_id)

        if not user:
            raise ValueError(f"Nutzer {order.person_id} existiert nicht.")

        if order.location_id != user.location_id:
            raise WrongLocationError(
                f"Person {order.person_id} gehört nicht zum Standort {user.location_id}"
            )

        order.handed_out = handed_out

        OrdersRepository.update_order(order)

        return DailyOrderFullSchema().dump(order)

    @staticmethod
    def get_daily_orders_filtered_by_user_scope(user_id: UUID) -> List[DailyOrder]:
        return OrdersRepository.get_daily_orders_filtered_by_user_scope(user_id)

    class CountOrdersObject:
        def __init__(self, location_name: str, rot: int, blau: int, salad_option: int):
            self.location_name = location_name
            self.rot = rot
            self.blau = blau
            self.salad_option = salad_option

    class CountOrdersSchema(Schema):
        location_id = fields.String(required=True)
        rot = fields.Integer(required=True)
        blau = fields.Integer(required=True)
        salad_option = fields.Integer(required=True)

    @staticmethod
    def get_all_daily_orders_count():
        all_daily_orders = OrdersRepository.get_all_daily_orders()

        location_counts = {}
        for order in all_daily_orders:
            if order.nothing:
                continue

            location_id = order.location_id
            if location_id not in location_counts:
                location_counts[location_id] = {
                    "location_name": LocationsRepository.get_location_by_id(
                        location_id
                    ).location_name,
                    "rot": 0,
                    "blau": 0,
                    "salad_option": 0,
                }

            if order.main_dish == MainDish.rot:
                location_counts[location_id]["rot"] += 1
            elif order.main_dish == MainDish.blau:
                location_counts[location_id]["blau"] += 1
            if order.salad_option:
                location_counts[location_id]["salad_option"] += 1

        orders = [  # TODO: store the whole location and not only the location_name with a Schema (Lennox)
            DailyOrdersService.CountOrdersObject(
                location_name=location["location_name"],
                rot=location["rot"],
                blau=location["blau"],
                salad_option=location["salad_option"],
            )
            for location in location_counts.values()
        ]

        return DailyOrdersService.CountOrdersSchema(many=True).dump(orders)
