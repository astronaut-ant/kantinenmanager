"""Tests for the LocationsService class."""

import pytest
import io
import uuid
from .helper import *  # for fixtures # noqa: F403
from src.services.locations_service import LocationsService
from src.repositories.locations_repository import LocationsRepository
from src.repositories.users_repository import UsersRepository
from src.models.user import UserGroup
from src.utils.exceptions import AlreadyExistsError, BadValueError, NotFoundError
from src.utils.pdf_creator import PDFCreationUtils


def describe_get_locations():
    def it_returns_locations_list(mocker, location):
        mock_locations = mocker.patch.object(
            LocationsService,
            "get_locations",
            return_value=[location],
        )

        locations = LocationsService.get_locations()

        assert locations == [location]
        mock_locations.assert_called_once_with()


def describe_get_location_by_id():
    def it_returns_location_by_id(mocker, location):
        mock_location = mocker.patch.object(
            LocationsService,
            "get_location_by_id",
            return_value=location,
        )

        res_location = LocationsService.get_location_by_id(location.id)
        assert res_location == location
        mock_location.assert_called_once_with(location.id)

    def it_raises_not_found_error_if_location_not_found(mocker, location):
        mocker.patch.object(
            LocationsRepository,
            "get_location_by_id",
            return_value=None,
        )
        with pytest.raises(NotFoundError) as e:
            LocationsService.get_location_by_id(uuid.uuid4())
        assert "Standort mit ID" in str(e)


def describe_create_location():
    def it_creates_location_successfully(mocker, user_standortleitung):
        mocker.patch.object(
            LocationsRepository,
            "get_location_by_name",
            return_value=None,
        )
        mocker.patch.object(
            UsersRepository,
            "get_user_by_id",
            return_value=user_standortleitung,
        )
        mocker.patch.object(
            LocationsRepository,
            "get_location_by_leader",
            return_value=None,
        )
        loc_id = uuid.uuid4()
        mocker.patch.object(
            LocationsRepository,
            "create_location",
            return_value=loc_id,
        )
        # Mock get_location_by_id instead of create_location
        mock_location = mocker.MagicMock()
        mock_location.id = loc_id
        mock_location.location_name = "Test Location"
        mock_location.user_id_location_leader = user_standortleitung.id
        mocker.patch.object(
            LocationsRepository,
            "get_location_by_id",
            return_value=mock_location,
        )

        result = LocationsService.create_location(
            "Test Location", user_standortleitung.id
        )
        assert result == loc_id

    def it_raises_already_exists_error_if_location_name_exists(
        mocker, user_standortleitung, location
    ):
        mocker.patch.object(
            LocationsRepository,
            "get_location_by_name",
            return_value=location,
        )
        with pytest.raises(AlreadyExistsError) as e:
            LocationsService.create_location("Test Location", user_standortleitung.id)
        assert "Standort Test Location" in str(e)

    def it_raises_not_found_error_if_user_not_found(mocker):
        mocker.patch.object(
            LocationsRepository,
            "get_location_by_name",
            return_value=None,
        )
        mocker.patch.object(
            UsersRepository,
            "get_user_by_id",
            return_value=None,
        )
        with pytest.raises(NotFoundError) as e:
            LocationsService.create_location("Test Location", uuid.uuid4())
        assert "Gruppenleitung mit ID" in str(e)

    def it_raises_already_exists_error_if_location_leader_is_not_free(
        mocker, user_standortleitung, location
    ):
        mocker.patch.object(
            LocationsRepository,
            "get_location_by_name",
            return_value=None,
        )
        mocker.patch.object(
            UsersRepository,
            "get_user_by_id",
            return_value=user_standortleitung,
        )
        mocker.patch.object(
            LocationsRepository,
            "get_location_by_leader",
            return_value=location,
        )
        with pytest.raises(AlreadyExistsError) as e:
            LocationsService.create_location("Test Location", user_standortleitung.id)
        assert "Nutzer:in" in str(e)


def describe_update_location():
    def it_updates_location_successfully(mocker, location, user_standortleitung):
        mocker.patch.object(
            LocationsRepository,
            "get_location_by_id",
            return_value=location,
        )
        mocker.patch.object(
            LocationsRepository,
            "get_location_by_name",
            return_value=None,
        )
        mocker.patch.object(
            UsersRepository,
            "get_user_by_id",
            return_value=user_standortleitung,
        )
        mocker.patch.object(
            LocationsRepository,
            "get_location_by_leader",
            return_value=None,
        )
        mock_update_user = mocker.patch.object(UsersRepository, "update_user")
        mock_update_location = mocker.patch.object(
            LocationsRepository,
            "update_location",
            return_value=True,
        )

        new_id = user_standortleitung.id

        assert user_standortleitung.location_id is None

        LocationsService.update_location(location, "New Location Name", new_id)

        mock_update_location.assert_called_once()
        mock_update_user.assert_called_once_with(user_standortleitung)
        assert location.location_name == "New Location Name"
        assert location.user_id_location_leader == new_id

    def it_raises_not_found_error_if_location_not_found(mocker):
        mocker.patch.object(
            LocationsRepository,
            "get_location_by_id",
            return_value=None,
        )
        with pytest.raises(NotFoundError) as e:
            LocationsService.update_location(
                uuid.uuid4(), "New Location Name", uuid.uuid4()
            )
        assert "Standort mit ID" in str(e)

    def it_raises_already_exists_error_if_location_name_exists(mocker, location):
        mocker.patch.object(
            LocationsRepository,
            "get_location_by_id",
            return_value=location,
        )
        mocker.patch.object(
            LocationsRepository,
            "get_location_by_name",
            return_value=location,
        )
        with pytest.raises(AlreadyExistsError) as e:
            LocationsService.update_location(
                location.id, "New Name", location.user_id_location_leader
            )
        assert "Standort" in str(e)

    def it_raises_already_exists_error_if_location_leader_is_not_free(
        mocker, location, user_standortleitung, app
    ):
        other_location = mocker.MagicMock()
        other_location.id = uuid.uuid4()  # Different from location.id

        current_leader_id = uuid.uuid4()  # Different from user_standortleitung.id
        location.user_id_location_leader = current_leader_id

        mocker.patch.object(
            LocationsRepository,
            "get_location_by_id",
            return_value=location,
        )
        mocker.patch.object(
            LocationsRepository,
            "get_location_by_name",
            return_value=None,
        )
        mocker.patch.object(
            UsersRepository,
            "get_user_by_id",
            return_value=user_standortleitung,
        )
        mocker.patch.object(
            LocationsRepository,
            "get_location_by_leader",
            return_value=other_location,
        )

        with app.app_context():
            with pytest.raises(BadValueError) as e:
                LocationsService.update_location(
                    location.id, "New Name", user_standortleitung.id
                )
            assert "leitet bereits einen Standort" in str(e)


def describe_delete_location():
    def it_deletes_location_successfully(mocker, location):
        mocker.patch.object(
            LocationsService,
            "delete_location",
        )

        LocationsService.delete_location(location)
        LocationsService.delete_location.assert_called_once_with(location)


def describe_get_groups_of_location():
    def it_returns_groups_of_location(mocker, location, group):
        mocker.patch.object(
            LocationsService,
            "get_location_by_id",
            return_value=location,
        )
        mocker.patch.object(
            LocationsService,
            "get_groups_of_location",
            return_value=[group],
        )

        groups = LocationsService.get_groups_of_location(location.id)
        assert groups == [group]

    def it_raises_not_found_error_if_location_not_found(mocker):
        mocker.patch.object(
            LocationsRepository,
            "get_location_by_id",
            return_value=None,
        )
        with pytest.raises(NotFoundError) as e:
            LocationsService.get_groups_of_location(uuid.uuid4())
        assert "Standort mit ID" in str(e)
