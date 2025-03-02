"""Tests for the UsersService class."""

import pytest
from uuid import uuid4
from src.models.user import UserGroup
from src.services.auth_service import AuthService
from src.repositories.locations_repository import LocationsRepository
from src.utils.exceptions import AlreadyExistsError, NotFoundError
from src.services.users_service import UsersService
from src.repositories.users_repository import UsersRepository
from .helper import *  # for fixtures # noqa: F403


def describe_get_users():
    def it_returns_all_users(mocker, user_verwaltung):
        mocker.patch.object(
            UsersRepository, "get_users", return_value=[user_verwaltung]
        )

        users = UsersService.get_users()

        assert users == [user_verwaltung]

    def it_takes_user_group_filter_argument(mocker, user_verwaltung):
        mocker.patch.object(
            UsersRepository, "get_users", return_value=[user_verwaltung]
        )

        users = UsersService.get_users(user_group_filter=user_verwaltung.user_group)

        assert users == [user_verwaltung]


def describe_get_user_by_id():
    def it_returns_user_by_id(mocker, user_verwaltung):
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_verwaltung
        )

        user_by_id = UsersService.get_user_by_id(user_verwaltung.id)

        assert user_by_id == user_verwaltung

    def it_returns_none_if_user_not_found(mocker):
        mocker.patch.object(UsersRepository, "get_user_by_id", return_value=None)

        user_by_id = UsersService.get_user_by_id(uuid4())

        assert user_by_id is None


def describe_get_user_by_username():
    def it_returns_user_by_username(mocker, user_verwaltung):
        mocker.patch.object(
            UsersRepository, "get_user_by_username", return_value=user_verwaltung
        )

        user_by_username = UsersService.get_user_by_username(user_verwaltung.username)

        assert user_by_username == user_verwaltung

    def it_returns_none_if_user_not_found(mocker):
        mocker.patch.object(UsersRepository, "get_user_by_username", return_value=None)

        user_by_username = UsersService.get_user_by_username("nonexistent")

        assert user_by_username is None


def describe_create_user():
    def it_does_not_create_existing_user(mocker, user_verwaltung):
        mocker.patch.object(
            UsersRepository, "get_user_by_username", return_value=user_verwaltung
        )

        with pytest.raises(AlreadyExistsError):
            UsersService.create_user(
                first_name=user_verwaltung.first_name,
                last_name=user_verwaltung.last_name,
                username=user_verwaltung.username,
                user_group=user_verwaltung.user_group,
            )

    def it_does_not_create_deleted_user(mocker, user_verwaltung):
        user_verwaltung.deleted = True
        mocker.patch.object(UsersRepository, "get_user_by_username", return_value=None)
        mocker.patch.object(
            UsersRepository, "get_hidden_user_by_username", return_value=user_verwaltung
        )

        with pytest.raises(AlreadyExistsError):
            UsersService.create_user(
                first_name=user_verwaltung.first_name,
                last_name=user_verwaltung.last_name,
                username=user_verwaltung.username,
                user_group=user_verwaltung.user_group,
            )

    def it_checks_location_id(mocker, user_verwaltung):
        mocker.patch.object(UsersRepository, "get_user_by_username", return_value=None)
        mocker.patch.object(
            UsersRepository, "get_hidden_user_by_username", return_value=None
        )
        mocker.patch.object(
            LocationsRepository, "get_location_by_id", return_value=None
        )

        with pytest.raises(NotFoundError):
            UsersService.create_user(
                first_name=user_verwaltung.first_name,
                last_name=user_verwaltung.last_name,
                username=user_verwaltung.username,
                user_group=user_verwaltung.user_group,
                location_id=uuid4(),  # random location_id that does not exist
            )

    def it_generates_password_if_none_given(mocker, user_verwaltung):
        mocker.patch.object(UsersRepository, "get_user_by_username", return_value=None)
        mocker.patch.object(
            UsersRepository, "get_hidden_user_by_username", return_value=None
        )
        mock_generate_pw = mocker.patch.object(
            AuthService, "generate_password", return_value="password"
        )
        mock_hash_pw = mocker.patch.object(
            AuthService, "hash_password", return_value="hashed_password"
        )
        id = uuid4()
        mocker.patch.object(UsersRepository, "create_user", return_value=id)

        created_id, initial_password = UsersService.create_user(
            first_name=user_verwaltung.first_name,
            last_name=user_verwaltung.last_name,
            username=user_verwaltung.username,
            user_group=user_verwaltung.user_group,
        )

        assert created_id == id
        assert initial_password == "password"
        mock_generate_pw.assert_called_once()
        mock_hash_pw.assert_called_once_with("password")

    def it_uses_given_password(mocker, user_verwaltung):
        mocker.patch.object(UsersRepository, "get_user_by_username", return_value=None)
        mocker.patch.object(
            UsersRepository, "get_hidden_user_by_username", return_value=None
        )
        mock_generate_pw = mocker.patch.object(AuthService, "generate_password")
        mock_hash_pw = mocker.patch.object(
            AuthService, "hash_password", return_value="hashed_password"
        )
        id = uuid4()
        mocker.patch.object(UsersRepository, "create_user", return_value=id)

        created_id, initial_password = UsersService.create_user(
            first_name=user_verwaltung.first_name,
            last_name=user_verwaltung.last_name,
            username=user_verwaltung.username,
            user_group=user_verwaltung.user_group,
            password="given_password",
        )

        assert created_id == id
        assert initial_password == "given_password"
        mock_hash_pw.assert_called_once_with("given_password")
        mock_generate_pw.assert_not_called()

    def it_uses_given_location(mocker, user_verwaltung, location):
        mocker.patch.object(UsersRepository, "get_user_by_username", return_value=None)
        mocker.patch.object(
            UsersRepository, "get_hidden_user_by_username", return_value=None
        )
        mocker.patch.object(
            LocationsRepository, "get_location_by_id", return_value=location
        )
        mocker.patch.object(AuthService, "generate_password", return_value="password")
        mocker.patch.object(
            AuthService, "hash_password", return_value="hashed_password"
        )
        id = uuid4()

        def create_user_side_effect(user):
            assert user.location_id == location.id
            return id

        mock_create_user = mocker.patch.object(
            UsersRepository, "create_user", side_effect=create_user_side_effect
        )

        created_id, initial_password = UsersService.create_user(
            first_name=user_verwaltung.first_name,
            last_name=user_verwaltung.last_name,
            username=user_verwaltung.username,
            user_group=user_verwaltung.user_group,
            location_id=location.id,
        )

        assert created_id == id
        assert initial_password == "password"
        mock_create_user.assert_called_once()


def describe_update_user():
    def it_checks_if_new_username_is_taken(
        mocker, user_verwaltung, user_standortleitung
    ):
        mocker.patch.object(
            UsersRepository, "get_user_by_username", return_value=user_standortleitung
        )

        with pytest.raises(AlreadyExistsError):
            UsersService.update_user(
                user_verwaltung,
                first_name=user_verwaltung.first_name,
                last_name=user_verwaltung.last_name,
                username=user_standortleitung.username,
                user_group=user_verwaltung.user_group,
            )

    def it_updates_user(mocker, user_verwaltung):
        mock_get_user_by_username = mocker.patch.object(
            UsersRepository, "get_user_by_username", return_value=None
        )
        mock_update_user = mocker.patch.object(
            UsersRepository, "update_user", return_value=user_verwaltung
        )

        updated_user = UsersService.update_user(
            user_verwaltung,
            first_name="Max",
            last_name="Mustermann",
            username="maxmustermann",
            user_group=UserGroup.standortleitung,
        )

        assert updated_user == user_verwaltung
        assert user_verwaltung.first_name == "Max"
        assert user_verwaltung.last_name == "Mustermann"
        assert user_verwaltung.username == "maxmustermann"
        assert user_verwaltung.user_group == UserGroup.standortleitung
        assert user_verwaltung.location is None
        mock_get_user_by_username.assert_called_once_with("maxmustermann")
        mock_update_user.assert_called_once_with(user_verwaltung)

    def it_updates_user_with_location(mocker, user_verwaltung, location):
        mock_get_user_by_username = mocker.patch.object(
            UsersRepository, "get_user_by_username", return_value=None
        )
        mock_update_user = mocker.patch.object(
            UsersRepository, "update_user", return_value=user_verwaltung
        )

        updated_user = UsersService.update_user(
            user_verwaltung,
            first_name="Max",
            last_name="Mustermann",
            username="maxmustermann",
            user_group=UserGroup.standortleitung,
            location=location,
        )

        assert updated_user == user_verwaltung
        assert user_verwaltung.location == location
        mock_get_user_by_username.assert_called_once_with("maxmustermann")
        mock_update_user.assert_called_once_with(user_verwaltung)

    def it_doesnt_check_username_if_it_not_changed(mocker, user_verwaltung):
        mock_get_user_by_username = mocker.patch.object(
            UsersRepository, "get_user_by_username", return_value=user_verwaltung
        )
        mock_update_user = mocker.patch.object(
            UsersRepository, "update_user", return_value=user_verwaltung
        )

        updated_user = UsersService.update_user(
            user_verwaltung,
            first_name="Max",
            last_name="Mustermann",
            username=user_verwaltung.username,
            user_group=UserGroup.standortleitung,
        )

        assert updated_user == user_verwaltung
        assert user_verwaltung.first_name == "Max"
        assert user_verwaltung.last_name == "Mustermann"
        assert user_verwaltung.username == user_verwaltung.username
        assert user_verwaltung.user_group == UserGroup.standortleitung
        assert user_verwaltung.location is None
        mock_get_user_by_username.assert_not_called()
        mock_update_user.assert_called_once_with(user_verwaltung)


def describe_block_user():
    def it_blocks_user(mocker, user_verwaltung):
        mock_update_user = mocker.patch.object(
            UsersRepository, "update_user", return_value=user_verwaltung
        )

        assert not user_verwaltung.blocked

        UsersService.block_user(user_verwaltung)

        assert user_verwaltung.blocked
        mock_update_user.assert_called_once_with(user_verwaltung)


def describe_unblock_user():
    def it_unblocks_user(mocker, user_verwaltung):
        mock_update_user = mocker.patch.object(
            UsersRepository, "update_user", return_value=user_verwaltung
        )

        user_verwaltung.blocked = True
        assert user_verwaltung.blocked

        UsersService.unblock_user(user_verwaltung)

        assert not user_verwaltung.blocked
        mock_update_user.assert_called_once_with(user_verwaltung)


def describe_delete_user():
    pass


def describe_reset_password():
    def it_resets_to_a_generated_password(mocker, user_verwaltung):
        mock_generate_pw = mocker.patch.object(
            AuthService, "generate_password", return_value="random_password"
        )
        mock_hash_pw = mocker.patch.object(
            AuthService, "hash_password", return_value="hashed_password"
        )
        mock_update_user = mocker.patch.object(
            UsersRepository, "update_user", return_value=user_verwaltung
        )
        mock_invalidate_all_refresh_tokens = mocker.patch.object(
            AuthService, "invalidate_all_refresh_tokens"
        )

        UsersService.reset_password(user_verwaltung)

        assert user_verwaltung.hashed_password == "hashed_password"
        mock_generate_pw.assert_called_once()
        mock_hash_pw.assert_called_once_with("random_password")
        mock_update_user.assert_called_once_with(user_verwaltung)
        mock_invalidate_all_refresh_tokens.assert_called_once_with(user_verwaltung.id)


def describe_get_group_leader():
    def it_returns_all_group_leaders_for_verwaltung(
        mocker, user_verwaltung, user_gruppenleitung
    ):
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_verwaltung
        )
        mocker.patch.object(
            UsersRepository, "get_group_leader", return_value=[user_gruppenleitung]
        )

        group_leader = UsersService.get_group_leader(user_verwaltung.id)

        assert group_leader == [user_gruppenleitung]

    def it_returns_group_leaders_with_same_or_no_location_for_standortleitung(
        mocker,
        user_verwaltung,
        user_gruppenleitung,
        user_standortleitung,
        user_kuechenpersonal,
    ):
        mocker.patch.object(
            UsersRepository, "get_user_by_id", return_value=user_standortleitung
        )

        user_standortleitung.location_id = uuid4()
        user_verwaltung.location_id = (
            user_standortleitung.location_id
        )  # Should be included, because same location
        user_gruppenleitung.location_id = (
            None  # Should be included, because no location
        )
        user_kuechenpersonal.location_id = (
            uuid4()
        )  # Should not be included, because different location

        # in the mock we return all values, because the repository would filter by user_group
        # I don't want to create so many mock group leaders
        mocker.patch.object(
            UsersRepository,
            "get_group_leader",
            return_value=[
                user_gruppenleitung,
                user_verwaltung,
                user_kuechenpersonal,
            ],  # doesn't matter that we don't return group leaders
        )

        group_leader = UsersService.get_group_leader(user_standortleitung.id)

        assert group_leader == [user_gruppenleitung, user_verwaltung]


def describe_get_location_leader():
    def it_returns_location_leader(mocker, user_standortleitung):
        mocker.patch.object(
            UsersRepository, "get_location_leader", return_value=[user_standortleitung]
        )

        location_leader = UsersService.get_location_leader()

        assert location_leader == [user_standortleitung]
