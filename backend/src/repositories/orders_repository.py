"""Repository to handle database operations for order data."""

from sqlalchemy import delete, insert, select, func, or_, and_, text
from sqlalchemy.orm import joinedload, aliased
from src.database import db
from uuid import UUID
from typing import List, Optional
from datetime import date, datetime, time
from flask import current_app as app
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
    def create_bulk_orders(bulk_orders: List[PreOrder], commit=True):
        """
        Create preorders

        :param orders: List of preorders
        """
        db.session.bulk_save_objects(bulk_orders)
        if commit:
            db.session.commit()

    @staticmethod
    def bulk_delete_orders(
        orders: List[PreOrder] | List[DailyOrder] | List[OldOrder], commit=True
    ):
        """
        Delete orders

        :param orders: List of orders
        """
        try:
            for order in orders:
                db.session.delete(order)
        except Exception as e:
            db.session.rollback()
            return e

        if commit:
            db.session.commit()

    @staticmethod
    def create_single_order(order: PreOrder) -> PreOrder:
        """
        Create preorder for user

        :param order: preorder object to create

        :return: Created preorder object
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
    def delete_order(order: PreOrder | DailyOrder | OldOrder):
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
        user_id: UUID,
        user_group: UserGroup,
        prejoin_person: bool = False,
        prejoin_location: bool = False,
    ) -> List[PreOrder]:
        """
        Get pre orders based on filters

        :param filters: Filters for orders
        :return: List of pre orders
        """
        query = select(PreOrder)

        user = UsersRepository.get_user_by_id(user_id)
        if user_group == UserGroup.verwaltung:
            query = query
        elif (
            user_group == UserGroup.standortleitung
            or user_group == UserGroup.kuechenpersonal
        ):
            query = query.filter(PreOrder.location_id == user.location_id)
        elif user_group == UserGroup.gruppenleitung:
            employee_alias = aliased(Employee)
            query = (
                query.join(PreOrder.person)
                .outerjoin(employee_alias, PreOrder.person_id == employee_alias.id)
                .filter(
                    or_(
                        user.leader_of_group.id == employee_alias.group_id,
                        employee_alias.group_id.in_(
                            [group.id for group in user.replacement_leader_of_groups]
                        ),
                        user.id == PreOrder.person_id,
                    )
                )
            )

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

        dt = datetime.combine(date, time(0, 0))  # convert date to datetime

        return db.session.scalars(
            select((PreOrder)).filter(
                and_(
                    (PreOrder.person_id == person_id),
                    (PreOrder.date == dt),
                )
            )
        ).first()

    @staticmethod
    def preorder_already_exists_different_id(
        person_id: UUID, date: date, id: int
    ) -> Optional[PreOrder]:
        """Check if another order already exists for the person and date
        :param person_id: Person id
        :param date: Date
        :return: Preorder if it exists else None
        """
        dt = datetime.combine(date, time(0, 0))  # convert date to datetime

        return db.session.scalars(
            select((PreOrder)).filter(
                and_(
                    (PreOrder.person_id == person_id),
                    (PreOrder.date == dt),
                    (PreOrder.id != id),
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
    def get_daily_order_by_id(daily_order_id: UUID) -> Optional[DailyOrder]:
        """
        Get daily order by id

        :param daily_order_id: Daily order id

        :return: DailyOrder object
        """

        return db.session.scalars(
            select(DailyOrder).filter(DailyOrder.id == daily_order_id)
        ).first()

    @staticmethod
    def get_all_daily_orders(
        filters: OrdersFilters | None = None,
        prejoin_person: bool = False,
        prejoin_location: bool = False,
    ) -> List[DailyOrder]:
        """
        Get daily orders based on filters

        :param filters: Filters for orders
        :param prejoin_person: Is Person Table Prejoined
        :param prejoin_location: Is Location Table Prejoined

        :return: List of daily orders in a response schema
        """
        query = select(DailyOrder)

        if prejoin_person:
            query = query.options(joinedload(DailyOrder.person))

        if prejoin_location:
            query = query.options(joinedload(DailyOrder.location))

        if filters is None:
            # Return early if no filters are provided
            return db.session.execute(query).scalars().all()

        if filters.person_id:
            query = query.filter(DailyOrder.person_id == filters.person_id)

        if filters.location_id:
            query = query.filter(DailyOrder.location_id == filters.location_id)

        if filters.group_id:
            query = query.filter(
                DailyOrder.person_id.in_(
                    select(Employee.id).where(Employee.group_id == filters.group_id)
                )
            )

        if filters.date:
            query = query.filter(DailyOrder.date == filters.date)

        if filters.date_start:
            query = query.filter(DailyOrder.date >= filters.date_start)

        if filters.date_end:
            query = query.filter(DailyOrder.date <= filters.date_end)

        return db.session.execute(query).scalars().all()

    @staticmethod
    def get_daily_orders_filtered_by_user_scope(user_id: UUID) -> List[DailyOrder]:
        """
        Get daily orders based on user scope

        :param user_id: UUID

        :return: Daily orders in a response schmea
        """
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
    def get_daily_orders_for_group(group_id: UUID) -> List[DailyOrder]:
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

        query = query.order_by(OldOrder.date.asc())

        return db.session.execute(query).scalars().all()

    ############################ Migrations ############################

    @staticmethod
    def push_preorders_to_dailyorders(today: date):
        """
        Push preorders from today to dailyorders
        """

        db.session.execute(text("BEGIN TRANSACTION"))

        db.session.execute(
            insert(DailyOrder).from_select(
                [
                    DailyOrder.person_id,
                    DailyOrder.location_id,
                    DailyOrder.date,
                    DailyOrder.nothing,
                    DailyOrder.main_dish,
                    DailyOrder.salad_option,
                    DailyOrder.handed_out,
                ],
                select(
                    PreOrder.person_id,
                    PreOrder.location_id,
                    PreOrder.date,
                    PreOrder.nothing,
                    PreOrder.main_dish,
                    PreOrder.salad_option,
                    False,
                ).filter(PreOrder.date == today),
            )
        )

        result = db.session.execute(delete(PreOrder).filter(PreOrder.date == today))
        app.logger.info(f"Pushed {result.rowcount} orders to daily orders table.")

        db.session.commit()

    @staticmethod
    def push_dailyorders_to_oldorders(today: date):
        """
        Push old dailyorders to oldorders
        """

        db.session.execute(text("BEGIN TRANSACTION"))

        db.session.execute(
            insert(OldOrder).from_select(
                [
                    OldOrder.person_id,
                    OldOrder.location_id,
                    OldOrder.date,
                    OldOrder.nothing,
                    OldOrder.main_dish,
                    OldOrder.salad_option,
                    OldOrder.handed_out,
                ],
                select(
                    DailyOrder.person_id,
                    DailyOrder.location_id,
                    DailyOrder.date,
                    DailyOrder.nothing,
                    DailyOrder.main_dish,
                    DailyOrder.salad_option,
                    DailyOrder.handed_out,
                ).filter(DailyOrder.date < today),
            )
        )

        result = db.session.execute(delete(DailyOrder).filter(DailyOrder.date < today))
        app.logger.info(f"Pushed {result.rowcount} daily orders to old orders table.")

        db.session.commit()

    @staticmethod
    def clean_preorders(today: date):
        """
        Push old preorders directly to oldorders
        This is just a fallback in case there are preorders left for some reason (e.g. development environment)
        """

        db.session.execute(text("BEGIN TRANSACTION"))

        db.session.execute(
            insert(OldOrder).from_select(
                [
                    OldOrder.person_id,
                    OldOrder.location_id,
                    OldOrder.date,
                    OldOrder.nothing,
                    OldOrder.main_dish,
                    OldOrder.salad_option,
                    OldOrder.handed_out,
                ],
                select(
                    PreOrder.person_id,
                    PreOrder.location_id,
                    PreOrder.date,
                    PreOrder.nothing,
                    PreOrder.main_dish,
                    PreOrder.salad_option,
                    False,
                ).filter(PreOrder.date < today),
            )
        )

        result = db.session.execute(delete(PreOrder).filter(PreOrder.date < today))
        app.logger.info(f"Pushed {result.rowcount} preorders to old orders table.")

        db.session.commit()
