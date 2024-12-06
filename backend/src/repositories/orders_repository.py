"""Repository to handle database operations for order data."""

from sqlalchemy import select, func, or_
from src.database import db
from uuid import UUID
from typing import List
from src.models.user import User
from src.models.user import UserGroup
from src.models.employee import Employee
from src.models.group import Group
from src.models.preorder import PreOrder


class OrdersRepository:

    @staticmethod
    def create_bulk_orders(
        orders: List[dict], user_group: UserGroup, user_id: UUID
    ) -> List[UUID]:
        """
        Create orders
        :param orders: List of orders
        :return: List of order ids
        """
        if user_group == UserGroup.gruppenleitung:
            order_ids = []
            employees = db.session.scalars(
                select(Employee)
                .join(Group)
                .filter(
                    or_(
                        Group.user_id_group_leader == user_id,
                        Group.user_id_replacement == user_id,
                    )
                )
            ).all()

            for order in orders:
                new_order = PreOrder(**order)
                if new_order.person_id in [employee.id for employee in employees]:
                    db.session.add(new_order)
                    order_ids.append(new_order.id)
                else:
                    raise ValueError(
                        "Person {person.id} ist nicht Teil der Gruppe von {user_id}"
                    )

            db.session.commit()
            return order_ids
