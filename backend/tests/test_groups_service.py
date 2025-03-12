"""Tests for the GroupsService class."""

import pytest
from uuid import uuid4
from src.models.user import UserGroup
from src.models.group import Group
from src.services.groups_service import GroupsService
from src.repositories.groups_repository import GroupsRepository
from src.repositories.users_repository import UsersRepository
from src.repositories.locations_repository import LocationsRepository
from src.repositories.employees_repository import EmployeesRepository
from src.utils.exceptions import AlreadyExistsError, NotFoundError, BadValueError
from src.utils.pdf_creator import PDFCreationUtils
from .helper import *  # for fixtures # noqa: F403


def describe_create_group():
    def it_creates_group_successfully(mocker, user_gruppenleitung, location):
        mocker.patch.object(
            LocationsRepository, "get_location_by_id", return_value=location
        )
        mocker.patch.object(
            GroupsRepository, "get_group_by_name_and_location", return_value=None
        )
        mocker.patch.object(GroupsRepository, "get_group_by_number", return_value=None)

        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_gruppenleitung
        )
        mocker.patch.object(
            GroupsRepository, "check_if_user_already_group_leader", return_value=False
        )

        new_id = uuid4()
        mock_create_group = mocker.patch.object(
            GroupsRepository, "create_group", return_value=new_id
        )

        result = GroupsService.create_group(
            group_name="Test Group",
            group_number=1,
            user_id_group_leader=user_gruppenleitung.id,
            location_id=location.id,
        )

        assert result == new_id
        mock_create_group.assert_called_once_with(
            "Test Group", 1, user_gruppenleitung.id, location.id, None
        )

    def it_creates_group_with_replacement_successfully(
        mocker, user_gruppenleitung, location
    ):
        mocker.patch.object(
            LocationsRepository, "get_location_by_id", return_value=location
        )
        mocker.patch.object(
            GroupsRepository, "get_group_by_name_and_location", return_value=None
        )
        mocker.patch.object(GroupsRepository, "get_group_by_number", return_value=None)
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_gruppenleitung
        )
        mocker.patch.object(
            GroupsRepository, "check_if_user_already_group_leader", return_value=False
        )

        replacement_id = uuid4()
        new_id = uuid4()
        mock_create_group = mocker.patch.object(
            GroupsRepository, "create_group", return_value=new_id
        )

        result = GroupsService.create_group(
            group_name="Test Group",
            group_number=1,
            user_id_group_leader=user_gruppenleitung.id,
            location_id=location.id,
            user_id_replacement=replacement_id,
        )

        assert result == new_id
        mock_create_group.assert_called_once_with(
            "Test Group", 1, user_gruppenleitung.id, location.id, replacement_id
        )

    def it_raises_if_location_not_found(mocker, user_gruppenleitung):
        mocker.patch.object(
            LocationsRepository, "get_location_by_id", return_value=None
        )

        location_id = uuid4()

        with pytest.raises(NotFoundError) as exc_info:
            GroupsService.create_group(
                group_name="Test Group",
                group_number=1,
                user_id_group_leader=user_gruppenleitung.id,
                location_id=location_id,
            )

        assert f"Standort mit ID {location_id}" in str(exc_info.value)

    def it_raises_if_group_number_exists(mocker, user_gruppenleitung, location, group):
        mocker.patch.object(
            LocationsRepository, "get_location_by_id", return_value=location
        )
        mocker.patch.object(
            GroupsRepository, "get_group_by_name_and_location", return_value=None
        )
        mocker.patch.object(GroupsRepository, "get_group_by_number", return_value=group)

        with pytest.raises(AlreadyExistsError) as exc_info:
            GroupsService.create_group(
                group_name="Test Group",
                group_number=1,
                user_id_group_leader=user_gruppenleitung.id,
                location_id=location.id,
            )

        assert "Gruppe 1" in str(exc_info.value)

    def it_raises_if_group_with_name_already_exists_at_location(
        mocker, user_gruppenleitung, location, group
    ):
        mocker.patch.object(
            LocationsRepository, "get_location_by_id", return_value=location
        )
        mocker.patch.object(
            GroupsRepository, "get_group_by_name_and_location", return_value=group
        )

        with pytest.raises(AlreadyExistsError) as exc_info:
            GroupsService.create_group(
                group_name="Test Group",
                group_number=1,
                user_id_group_leader=user_gruppenleitung.id,
                location_id=location.id,
            )

        assert "Gruppe Test Group" in str(exc_info.value)
        assert "an diesem Standort" in str(exc_info.value)

    def it_raises_if_group_leader_not_found(mocker, location):
        mocker.patch.object(
            LocationsRepository, "get_location_by_id", return_value=location
        )
        mocker.patch.object(
            GroupsRepository, "get_group_by_name_and_location", return_value=None
        )
        mocker.patch.object(GroupsRepository, "get_group_by_number", return_value=None)
        mocker.patch.object(UsersRepository, "get_user_by_id", return_value=None)

        with pytest.raises(NotFoundError) as exc_info:
            GroupsService.create_group(
                group_name="Test Group",
                group_number=1,
                user_id_group_leader=uuid4(),
                location_id=location.id,
            )

        assert "Gruppenleitung mit ID" in str(exc_info.value)

    def it_raises_if_user_not_gruppenleitung_user_group(
        mocker, user_standortleitung, location
    ):
        mocker.patch.object(
            LocationsRepository, "get_location_by_id", return_value=location
        )
        mocker.patch.object(
            GroupsRepository, "get_group_by_name_and_location", return_value=None
        )
        mocker.patch.object(GroupsRepository, "get_group_by_number", return_value=None)
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_standortleitung
        )

        with pytest.raises(BadValueError) as exc_info:
            GroupsService.create_group(
                group_name="Test Group",
                group_number=1,
                user_id_group_leader=user_standortleitung.id,
                location_id=location.id,
            )

        assert "ist keine Gruppenleitung" in str(exc_info.value)

    def it_raises_if_user_already_group_leader(mocker, user_gruppenleitung, location):
        mocker.patch.object(
            LocationsRepository, "get_location_by_id", return_value=location
        )
        mocker.patch.object(
            GroupsRepository, "get_group_by_name_and_location", return_value=None
        )
        mocker.patch.object(GroupsRepository, "get_group_by_number", return_value=None)
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_gruppenleitung
        )
        mocker.patch.object(
            GroupsRepository, "check_if_user_already_group_leader", return_value=True
        )

        with pytest.raises(BadValueError) as exc_info:
            GroupsService.create_group(
                group_name="Test Group",
                group_number=1,
                user_id_group_leader=user_gruppenleitung.id,
                location_id=location.id,
            )

        assert "ist bereits Gruppenleitung" in str(exc_info.value)

    def it_raises_if_replacement_not_found(mocker, user_gruppenleitung, location):
        mocker.patch.object(
            LocationsRepository, "get_location_by_id", return_value=location
        )
        mocker.patch.object(
            GroupsRepository, "get_group_by_name_and_location", return_value=None
        )
        mocker.patch.object(GroupsRepository, "get_group_by_number", return_value=None)
        mocker.patch.object(UsersRepository, "get_user_by_id")
        UsersRepository.get_user_by_id.side_effect = [user_gruppenleitung, None]
        mocker.patch.object(
            GroupsRepository, "check_if_user_already_group_leader", return_value=False
        )

        replacement_id = uuid4()

        with pytest.raises(NotFoundError) as exc_info:
            GroupsService.create_group(
                group_name="Test Group",
                group_number=1,
                user_id_group_leader=user_gruppenleitung.id,
                location_id=location.id,
                user_id_replacement=replacement_id,
            )

        assert f"Nutzer:in mit ID {replacement_id}" in str(exc_info.value)

    def it_raises_if_replacement_not_gruppenleitung_role(
        mocker, user_gruppenleitung, user_standortleitung, location
    ):
        mocker.patch.object(
            LocationsRepository, "get_location_by_id", return_value=location
        )
        mocker.patch.object(
            GroupsRepository, "get_group_by_name_and_location", return_value=None
        )
        mocker.patch.object(GroupsRepository, "get_group_by_number", return_value=None)
        mocker.patch.object(UsersRepository, "get_user_by_id")
        UsersRepository.get_user_by_id.side_effect = [
            user_gruppenleitung,
            user_standortleitung,
        ]
        mocker.patch.object(
            GroupsRepository, "check_if_user_already_group_leader", return_value=False
        )

        with pytest.raises(BadValueError) as exc_info:
            GroupsService.create_group(
                group_name="Test Group",
                group_number=1,
                user_id_group_leader=user_gruppenleitung.id,
                location_id=location.id,
                user_id_replacement=user_standortleitung.id,
            )

        assert "ist keine Gruppenleitung" in str(exc_info.value)


def describe_get_group_by_id():
    def it_returns_group_by_id(mocker, group):
        mock_group = mocker.patch.object(
            GroupsRepository, "get_group_by_id", return_value=group
        )

        result = GroupsService.get_group_by_id(group.id)

        assert result == group
        mock_group.assert_called_once_with(group.id)

    def it_raises_if_group_not_found(mocker):
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=None)

        with pytest.raises(NotFoundError) as exc_info:
            GroupsService.get_group_by_id(uuid4())

        assert "Gruppe mit ID" in str(exc_info.value)


def describe_get_all_groups_with_locations():
    def it_returns_groups_with_locations(mocker, group, location, app):
        with app.app_context():
            location.location_name = "Test Location"
            group.group_name = "Test Group"
            mocker.patch.object(
                GroupsRepository, "get_groups_by_userscope", return_value=[group]
            )
            mocker.patch.object(
                LocationsRepository, "get_location_by_id", return_value=location
            )

            result = GroupsService.get_all_groups_with_locations(
                uuid4(), UserGroup.verwaltung
            )

            assert result == {"Test Location": ["Test Group"]}


def describe_get_groups():
    def it_returns_groups_for_user(mocker, group, user_verwaltung):
        mock_group = mocker.patch.object(
            GroupsRepository, "get_groups_by_userscope", return_value=[group]
        )

        result = GroupsService.get_groups(user_verwaltung.id, UserGroup.verwaltung)

        assert result == [group]
        mock_group.assert_called_once_with(user_verwaltung.id, UserGroup.verwaltung)


def describe_delete_group():
    def it_deletes_group_successfully(mocker, group):
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=group)
        mock_delete = mocker.patch.object(GroupsRepository, "delete_group")

        GroupsService.delete_group(group.id)

        mock_delete.assert_called_once_with(group)

    def it_raises_if_group_not_found(mocker):
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=None)

        with pytest.raises(NotFoundError) as exc_info:
            GroupsService.delete_group(uuid4())

        assert "Gruppe mit ID" in str(exc_info.value)


def describe_update_group():
    def it_updates_group_successfully_by_name_and_number(mocker, group, location):
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=group)
        mocker.patch.object(GroupsRepository, "get_group_by_number", return_value=None)
        mock_update = mocker.patch.object(GroupsRepository, "update_group")

        result = GroupsService.update_group(
            group_id=group.id,
            group_name="Updated Group",
            group_number=2,
            user_id_group_leader=group.user_id_group_leader,
            location_id=location.id,
        )

        assert result.group_name == "Updated Group"
        assert result.group_number == 2
        mock_update.assert_called_once_with(group)

    def it_updates_group_with_new_leader_successfully(
        mocker, group, user_gruppenleitung, location
    ):
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=group)
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_gruppenleitung
        )
        mocker.patch.object(GroupsRepository, "get_group_by_number", return_value=None)
        mock_update = mocker.patch.object(GroupsRepository, "update_group")

        new_leader_id = uuid4()

        result = GroupsService.update_group(
            group_id=group.id,
            group_name="Updated Group",
            group_number=2,
            user_id_group_leader=new_leader_id,
            location_id=location.id,
        )

        assert result.group_name == "Updated Group"
        assert result.user_id_group_leader == new_leader_id
        mock_update.assert_called_once_with(group)

    def it_updates_group_with_replacement_successfully(
        mocker, group, user_gruppenleitung, location
    ):
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=group)
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_gruppenleitung
        )
        mocker.patch.object(GroupsRepository, "get_group_by_number", return_value=None)
        mock_update = mocker.patch.object(GroupsRepository, "update_group")

        replacement_id = uuid4()

        result = GroupsService.update_group(
            group_id=group.id,
            group_name="Updated Group",
            group_number=2,
            user_id_group_leader=group.user_id_group_leader,
            location_id=location.id,
            user_id_replacement=replacement_id,
        )

        # Assert
        assert result.user_id_replacement == replacement_id
        mock_update.assert_called_once_with(group)

    def it_removes_replacement_when_none_provided(mocker, group, location):
        group.user_id_replacement = uuid4()
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=group)
        mocker.patch.object(GroupsRepository, "get_group_by_number", return_value=None)
        mock_update = mocker.patch.object(GroupsRepository, "update_group")

        result = GroupsService.update_group(
            group_id=group.id,
            group_name="Updated Group",
            group_number=2,
            user_id_group_leader=group.user_id_group_leader,
            location_id=location.id,
            user_id_replacement=None,
        )

        assert result.user_id_replacement is None
        mock_update.assert_called_once_with(group)

    def it_raises_if_group_not_found(mocker):
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=None)

        with pytest.raises(NotFoundError) as exc_info:
            GroupsService.update_group(
                group_id=uuid4(),
                group_name="Updated Group",
                group_number=2,
                user_id_group_leader=uuid4(),
                location_id=uuid4(),
            )

        assert "Gruppe mit ID" in str(exc_info.value)

    def it_raises_if_new_group_leader_not_found(mocker, group):
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=group)
        mocker.patch.object(UsersRepository, "get_user_by_id", return_value=None)

        with pytest.raises(NotFoundError) as exc_info:
            GroupsService.update_group(
                group_id=group.id,
                group_name="Updated Group",
                group_number=2,
                user_id_group_leader=uuid4(),
                location_id=group.location_id,
            )

        assert "Nutzer:in mit ID" in str(exc_info.value)

    def it_raises_if_new_group_leader_not_gruppenleitung(
        mocker, group, user_standortleitung
    ):
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=group)
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_standortleitung
        )

        with pytest.raises(BadValueError) as exc_info:
            GroupsService.update_group(
                group_id=group.id,
                group_name="Updated Group",
                group_number=2,
                user_id_group_leader=user_standortleitung.id,
                location_id=group.location_id,
            )

        assert "ist keine Gruppenleitung" in str(exc_info.value)

    def it_raises_if_replacement_not_found(mocker, group):
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=group)
        mocker.patch.object(UsersRepository, "get_user_by_id")
        UsersRepository.get_user_by_id.side_effect = [None]

        with pytest.raises(NotFoundError) as exc_info:
            GroupsService.update_group(
                group_id=group.id,
                group_name="Updated Group",
                group_number=2,
                user_id_group_leader=group.user_id_group_leader,
                location_id=group.location_id,
                user_id_replacement=uuid4(),
            )

        assert "Nutzer:in mit ID" in str(exc_info.value)

    def it_raises_if_replacement_not_gruppenleitung(
        mocker, group, user_standortleitung
    ):
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=group)
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_standortleitung
        )

        with pytest.raises(BadValueError) as exc_info:
            GroupsService.update_group(
                group_id=group.id,
                group_name="Updated Group",
                group_number=2,
                user_id_group_leader=group.user_id_group_leader,
                location_id=group.location_id,
                user_id_replacement=user_standortleitung.id,
            )

        assert "Vertretungs-Nutzer:in" in str(exc_info.value)
        assert "ist keine Gruppenleitung" in str(exc_info.value)

    def it_raises_if_location_not_found(mocker, group):
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=group)
        mocker.patch.object(
            LocationsRepository, "get_location_by_id", return_value=None
        )

        with pytest.raises(NotFoundError) as exc_info:
            GroupsService.update_group(
                group_id=group.id,
                group_name="Updated Group",
                group_number=2,
                user_id_group_leader=group.user_id_group_leader,
                location_id=uuid4(),
            )

        assert "Standort mit ID" in str(exc_info.value)

    def it_raises_if_group_number_already_exists(mocker, group):
        existing_group = Group(
            group_name="Existing",
            group_number=2,
            location_id=group.location_id,
            user_id_group_leader=uuid4(),
            user_id_replacement=None,
        )
        existing_group.id = uuid4()

        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=group)
        mocker.patch.object(
            GroupsRepository, "get_group_by_number", return_value=existing_group
        )

        with pytest.raises(AlreadyExistsError) as exc_info:
            GroupsService.update_group(
                group_id=group.id,
                group_name="Updated Group",
                group_number=2,
                user_id_group_leader=group.user_id_group_leader,
                location_id=group.location_id,
            )

        assert "Gruppe 2" in str(exc_info.value)


def describe_create_batch_qr_codes():
    def it_generates_qr_codes_for_group(mocker, group, employee, user_verwaltung):
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=group)
        mocker.patch.object(
            EmployeesRepository, "get_employees_by_user_scope", return_value=[employee]
        )
        pdf_bytes = b"mock pdf content"
        mock_pdf = mocker.patch.object(
            PDFCreationUtils, "create_batch_qr_codes", return_value=pdf_bytes
        )

        result = GroupsService.create_batch_qr_codes(
            group.id, user_verwaltung.id, UserGroup.verwaltung
        )

        assert result == pdf_bytes
        mock_pdf.assert_called_once_with(employees=[employee], group=group)

    def it_raises_if_no_employees_found(mocker, group, user_verwaltung):
        mocker.patch.object(GroupsRepository, "get_group_by_id", return_value=group)
        mocker.patch.object(
            EmployeesRepository, "get_employees_by_user_scope", return_value=[]
        )

        with pytest.raises(NotFoundError) as exc_info:
            GroupsService.create_batch_qr_codes(
                group.id, user_verwaltung.id, UserGroup.verwaltung
            )

        assert f"Mitarbeiter:innen der Gruppe mit ID {group.id}" in str(exc_info.value)
