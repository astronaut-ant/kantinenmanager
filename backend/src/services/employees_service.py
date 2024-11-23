"""Service for handling employee management."""

from uuid import UUID
from src.services.auth_service import AuthService
from src.models.user import UserGroup
from src.models.employee import Employee
from src.repositories.employees_repository import EmployeesRepository


class EmployeesService:
    """Service for handling employee management."""

    @staticmethod
    def get_employees(user_group: UserGroup, user_id: UUID) -> list[Employee]:
        """Get all employees the user has access to based on their user group and id."""

        return EmployeesRepository.get_employees_by_user_scope(user_group, user_id)
