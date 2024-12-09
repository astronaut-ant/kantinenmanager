"""Repository to handle database operations for order data."""

from sqlalchemy import select, func, or_, and_
from src.database import db
from uuid import UUID
from typing import List
from datetime import date, datetime
from src.models.user import User
from src.models.user import UserGroup
from src.models.employee import Employee
from src.models.group import Group
from src.models.preorder import PreOrder


class OrdersRepository:

    @staticmethod
    def create_bulk_orders(bulk_orders: List[PreOrder]):
        """
        Create preorders
        :param orders: List of preorders
        """
        db.session.bulk_save_objects(bulk_orders)
        db.session.commit()

    @staticmethod
    def create_order_user(order: PreOrder):
        """
        Create order for user
        :param order: preorder
        """
        db.session.add(order)
        db.session.commit()

    @staticmethod
    def update_bulk_orders():
        # db.ession.bulk_save_objects(objects, return_defaults=False, update_changed_only=True
        pass

    @staticmethod
    def order_already_exists(person_id: UUID, date: date) -> bool:
        """
        Check if an order already exists for the person and date
        :param order: Order
        :return: True if order already exists
        """
        return (
            db.session.scalars(
                select(func.count(PreOrder.id)).filter(
                    and_(
                        (PreOrder.person_id == person_id),
                        (PreOrder.date == date),
                    )
                )
            ).one_or_none()
            > 0
        )

    @staticmethod
    def get_employees_to_order_for(user_id: UUID) -> List[UUID]:
        """
        Get all employee ids of the groups the user has to do the orders for
        :param user_id: User id
        :return: List of employee ids
        """
        # Use a subquery to get group ids for the user
        group_ids_subquery = select(Group.id).filter(
            or_(
                # User is the group leader and no replacement is set
                and_(
                    (Group.user_id_group_leader == user_id)
                    & (Group.user_id_replacement == None),
                ),
                # Or the user is a replacement for the group leader
                (Group.user_id_replacement == user_id),
            )
        )

        # Use the group IDs to fetch all employee IDs
        employee_ids = db.session.scalars(
            select(Employee.id).filter(Employee.group_id.in_(group_ids_subquery))
        ).all()

        return employee_ids

    # def get_groups_to_order_for(user_id: UUID) -> List[Group]:
    #     """
    #     Get all groups the user has to do the orders for
    #     :param user_id: User id
    #     :return: List of groups
    #     """
    #     return db.session.scalars(
    #         select(Group.id).filter(
    #             or_(
    #                 # User ist der Gruppenleiter und es ist keine Vertretung eingetragen
    #                 and_(
    #                     (Group.user_id_group_leader == user_id)
    #                     & (Group.user_id_replacement == None),
    #                 ),
    #                 # Oder User ist Vertretung für den Gruppenleiter
    #                 (Group.user_id_replacement == user_id),
    #             )
    #         )
    #     ).all()

    # def get_employee_ids(ids_of_groups_to_order_for: List[UUID]) -> List[UUID]:
    #     """
    #     Get all employee ids of the groups the user has to do the orders for
    #     :param ids_of_groups_to_order_for: List of group ids
    #     :return: List of employee ids
    #     """
    #     return db.session.scalars(
    #         select(Employee.id).filter(
    #             Employee.group_id.in_(ids_of_groups_to_order_for)
    #         )
    #     ).all()

    def employee_belongs_to_location(person_id: UUID, location_id: UUID) -> bool:
        """
        Check if a person belongs to a location
        :param person_id: Person id
        :param location_id: Location id
        :return: True if person belongs to location
        """
        return (
            db.session.scalars(
                select(func.count(Employee.id))
                .join(Group, Employee.group_id == Group.id)
                .filter(
                    and_(
                        (Employee.id == person_id),
                        (Group.location_id == location_id),
                    )
                )
            ).one_or_none()
            > 0
        )
