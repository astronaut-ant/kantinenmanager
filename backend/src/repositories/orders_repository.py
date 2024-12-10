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
from src.models.dailyorder import DailyOrder


class OrdersRepository:

    @staticmethod
    def create_bulk_orders(bulk_orders):
        """
        Create (pre)orders
        :param orders: List of (pre)orders
        """
        db.session.bulk_save_objects(bulk_orders)
        db.session.commit()

    @staticmethod
    def create_single_order(order):
        """
        Create (pre)order for user
        :param order: (pre)order object to create
        """
        db.session.add(order)
        db.session.commit()

    @staticmethod
    def update_order():
        """
        Update order
        """
        db.session.commit()

    @staticmethod
    def delete_order(order):
        """
        Delete order
        """
        db.session.delete(order)
        db.session.commit()

    @staticmethod
    def get_preorder_by_id(preorder_id: UUID) -> PreOrder:
        """Get preorder by id
        :param preorder_id: Preorder id
        :return: Preorder object
        """
        return db.session.scalars(
            select(PreOrder).filter(PreOrder.id == preorder_id)
        ).first()

    @staticmethod
    def preorder_already_exists(person_id: UUID, date: date) -> PreOrder:
        """Check if an order already exists for the person and date
        :param person_id: Person id
        :param date: Date
        :return: Preorder if it exists else None
        """
        return db.session.scalars(
            select((PreOrder)).filter(
                and_(
                    (PreOrder.person_id == person_id),
                    (PreOrder.date == date),
                )
            )
        ).first()

    @staticmethod
    def get_employees_to_order_for(user_id: UUID) -> List[UUID]:
        """Get all employee ids of the groups the user has to do the orders for
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

    def employee_in_location(person_id: UUID, location_id: UUID) -> bool:
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

    @staticmethod
    def get_daily_order_by_person_id(person_id: UUID) -> DailyOrder:
        """
        Get daily order by person id
        :param person_id: Person id
        :return: DailyOrder object
        """
        return db.session.scalars(
            select(DailyOrder).filter(PreOrder.person_id == person_id)
        ).first()

    @staticmethod
    def get_daily_order_by_id(daily_order_id: UUID) -> DailyOrder:
        """
        Get daily order by id
        :param daily_order_id: Daily order id
        :return: DailyOrder object
        """
        return db.session.scalars(
            select(DailyOrder).filter(DailyOrder.id == daily_order_id)
        ).first()
