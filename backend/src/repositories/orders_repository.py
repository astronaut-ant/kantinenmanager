"""Repository to handle database operations for order data."""

from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import joinedload
from src.database import db
from uuid import UUID
from typing import List, Optional
from datetime import date, datetime
from src.models.employee import Employee
from src.models.group import Group
from src.models.preorder import PreOrder
from src.models.dailyorder import DailyOrder
from src.models.oldorder import OldOrder
from src.models.user import UserGroup
from src.repositories.users_repository import UsersRepository


class OrdersFilters:
    """
    Filters for orders

    All filters are optional.

    :param person_id: Person id
    :param location_id: Location id
    :param group_id: Group id
    :param date: Date
    :param date_start: Start date
    :param date_end: End date
    """

    def __init__(
        self,
        person_id: Optional[UUID] = None,
        location_id: Optional[UUID] = None,
        group_id: Optional[UUID] = None,
        date: Optional[datetime] = None,
        date_start: Optional[datetime] = None,
        date_end: Optional[datetime] = None,
    ):
        """
        Constructor

        :param person_id: Person id
        :param location_id: Location id
        :param group_id: Group id
        :param date: Date
        :param date_start: Start date
        :param date_end: End date
        """
        self.person_id = person_id
        self.location_id = location_id
        self.group_id = group_id
        self.date = date
        self.date_start = date_start
        self.date_end = date_end

    def __repr__(self):
        return f"OrdersFilters(person_id={self.person_id}, location_id={self.location_id}, group_id={self.group_id}, date={self.date}, date_start={self.date_start}, date_end={self.date_end})"


class OrdersRepository:
    """Repository to handle database operations for order data."""

    @staticmethod
    def create_bulk_orders(bulk_orders):
        """
        Create (pre)orders
        :param orders: List of (pre)orders
        """
        db.session.bulk_save_objects(bulk_orders)
        db.session.commit()

    @staticmethod
    def bulk_delete_orders(orders: List[PreOrder] | List[DailyOrder] | List[OldOrder]):
        """
        Delete orders
        :param orders: List of orders
        """
        try:
            for order in orders:
                db.session.delete(order)
        except Exception as e:
            return e
        db.session.commit()

    @staticmethod
    def create_single_order(order: PreOrder) -> PreOrder:
        """
        Create (pre)order for user

        :param order: (pre)order object to create

        :return: Created (pre)order object
        """
        db.session.add(order)
        db.session.commit()
        return order

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
    def get_employees_to_order_for(user_id: UUID) -> List[UUID]:
        """Get all employee ids of the groups the user has to do the orders for
        :param user_id: User id
        :return: List of employee ids
        """
        # Use a subquery to get group ids for the user
        group_ids_subquery = select(Group.id).filter(
            or_(
                and_(
                    Group.user_id_group_leader == user_id,
                    Group.user_id_replacement.is_(None),
                ),
                Group.user_id_replacement == user_id,
            )
        )

        # Use the group IDs to fetch all employee IDs
        employee_ids = db.session.scalars(
            select(Employee.id).filter(Employee.group_id.in_(group_ids_subquery))
        ).all()

        return employee_ids

    def employee_in_location(employee_id: UUID, location_id: UUID) -> bool:
        """
        Check if a person belongs to a location
        :param person_id: Person id
        :param location_id: Location id
        :return: True if person belongs to location, False otherwise
        """
        return (
            db.session.scalars(
                select(func.count(Employee.id))
                .join(Group, Employee.group_id == Group.id)
                .filter(
                    and_(
                        (Employee.id == employee_id),
                        (Group.location_id == location_id),
                    )
                )
            ).one_or_none()
            > 0
        )

    ############################ PreOrders ############################

    @staticmethod
    def get_pre_order_by_id(id: int) -> Optional[PreOrder]:
        """
        Get pre order by id

        :param id: Pre order id
        :return: Pre order object
        """
        return db.session.scalars(select(PreOrder).filter(PreOrder.id == id)).first()

    @staticmethod
    def get_pre_orders(
        filters: OrdersFilters,
        prejoin_person: bool = False,
        prejoin_location: bool = False,
    ) -> List[PreOrder]:
        """
        Get pre orders based on filters

        :param filters: Filters for orders
        :return: List of pre orders
        """
        query = select(PreOrder)

        if filters.person_id:
            query = query.filter(PreOrder.person_id == filters.person_id)

        if filters.location_id:
            query = query.filter(PreOrder.location_id == filters.location_id)

        if filters.group_id:
            query = query.filter(
                PreOrder.person_id.in_(
                    select(Employee.id).where(Employee.group_id == filters.group_id)
                )
            )

        if filters.date:
            query = query.filter(PreOrder.date == filters.date)

        if filters.date_start:
            query = query.filter(PreOrder.date >= filters.date_start)

        if filters.date_end:
            query = query.filter(PreOrder.date <= filters.date_end)

        if prejoin_person:
            query = query.options(joinedload(PreOrder.person))

        if prejoin_location:
            query = query.options(joinedload(PreOrder.location))

        return db.session.execute(query).scalars().all()

    @staticmethod
    def preorder_already_exists(person_id: UUID, date: date) -> Optional[PreOrder]:
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

    ############################ DailyOrders ############################
    @staticmethod
    def get_daily_order_by_person_id(person_id: UUID) -> Optional[DailyOrder]:
        """
        Get daily order by person id

        :param person_id: Person id

        :return: DailyOrder object
        """

        return db.session.scalars(
            select(DailyOrder).filter(DailyOrder.person_id == person_id)
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

    @staticmethod
    def get_all_daily_orders(date: Optional[datetime] = None) -> List[DailyOrder]:
        """
        Get all orders in the daily orders

        :return: List of daily orders
        """
        if date:
            return db.session.scalars(
                select(DailyOrder).where(DailyOrder.date == date)
            ).all()

        return db.session.scalars(select(DailyOrder)).all()

    @staticmethod
    def get_daily_orders_filtered_by_user_scope(user_id: UUID) -> List[DailyOrder]:
        user = UsersRepository.get_user_by_id(user_id)
        if user.user_group == UserGroup.verwaltung:
            return db.session.scalars(select(DailyOrder)).all()
        elif (
            user.user_group == UserGroup.kuechenpersonal
            or user.user_group == UserGroup.standortleitung
        ):
            return db.session.scalars(
                select(DailyOrder).filter(DailyOrder.location_id == user.location_id)
            ).all()
        else:
            return []

    @staticmethod
    def get_daily_orders_for_group(group_id: UUID, user_id: UUID) -> List[DailyOrder]:
        """
        Get daily orders for a group

        :param group_id: UUID

        :return: Daily orders in a response schmea
        """
        return db.session.scalars(
            select(DailyOrder)
            .join(Employee, DailyOrder.person_id == Employee.id)
            .filter(Employee.group_id == group_id)
        ).all()

    @staticmethod
    def create_daily_orders(daily_orders: List[DailyOrder]):
        """
        Create daily orders

        :param daily_orders: List of daily orders
        """

        db.session.bulk_save_objects(daily_orders)
        db.session.commit()

    ############################ OldOrders ############################
    @staticmethod
    def get_old_orders(filters: OrdersFilters) -> List[OldOrder]:
        """
        Get old orders based on filters

        :param filters: Filters for orders
        :return: List of old orders
        """
        query = select(OldOrder)

        if filters.person_id:
            query = query.filter(OldOrder.person_id == filters.person_id)

        if filters.location_id:
            query = query.filter(OldOrder.location_id == filters.location_id)

        if filters.group_id:
            query = query.filter(
                OldOrder.person_id.in_(
                    select(Employee.id).where(Employee.group_id == filters.group_id)
                )
            )

        if filters.date:
            query = query.filter(OldOrder.date == filters.date)

        if filters.date_start:
            query = query.filter(OldOrder.date >= filters.date_start)

        if filters.date_end:
            query = query.filter(OldOrder.date <= filters.date_end)

        return db.session.execute(query).scalars().all()
