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
    def it_returns_all_users(mocker, user):
        mocker.patch.object(UsersRepository, "get_users", return_value=[user])

        users = UsersService.get_users()

        assert users == [user]

    def it_takes_user_group_filter_argument(mocker, user):
        mocker.patch.object(UsersRepository, "get_users", return_value=[user])

        users = UsersService.get_users(user_group_filter=user.user_group)

        assert users == [user]


def describe_get_user_by_id():
    def it_returns_user_by_id(mocker, user):
        mocker.patch.object(UsersRepository, "get_user_by_id", return_value=user)

        user_by_id = UsersService.get_user_by_id(user.id)

        assert user_by_id == user

    def it_returns_none_if_user_not_found(mocker):
        mocker.patch.object(UsersRepository, "get_user_by_id", return_value=None)

        user_by_id = UsersService.get_user_by_id(uuid4())

        assert user_by_id is None


def describe_get_user_by_username():
    def it_returns_user_by_username(mocker, user):
        mocker.patch.object(UsersRepository, "get_user_by_username", return_value=user)

        user_by_username = UsersService.get_user_by_username(user.username)

        assert user_by_username == user

    def it_returns_none_if_user_not_found(mocker):
        mocker.patch.object(UsersRepository, "get_user_by_username", return_value=None)

        user_by_username = UsersService.get_user_by_username("nonexistent")

        assert user_by_username is None


def describe_create_user():
    def it_does_not_create_existing_user(mocker, user):
        mocker.patch.object(UsersRepository, "get_user_by_username", return_value=user)

        with pytest.raises(AlreadyExistsError):
            UsersService.create_user(
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                user_group=user.user_group,
            )

    def it_checks_location_id(mocker, user):
        mocker.patch.object(UsersRepository, "get_user_by_username", return_value=None)
        mocker.patch.object(
            LocationsRepository, "get_location_by_id", return_value=None
        )

        with pytest.raises(NotFoundError):
            UsersService.create_user(
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                user_group=user.user_group,
                location_id=uuid4(),  # random location_id that does not exist
            )

    def it_generates_password_if_none_given(mocker, user):
        mocker.patch.object(UsersRepository, "get_user_by_username", return_value=None)
        mock_generate_pw = mocker.patch.object(
            AuthService, "generate_password", return_value="password"
        )
        mock_hash_pw = mocker.patch.object(
            AuthService, "hash_password", return_value="hashed_password"
        )
        id = uuid4()
        mocker.patch.object(UsersRepository, "create_user", return_value=id)

        created_id, initial_password = UsersService.create_user(
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            user_group=user.user_group,
        )

        assert created_id == id
        assert initial_password == "password"
        mock_generate_pw.assert_called_once()
        mock_hash_pw.assert_called_once_with("password")

    def it_uses_given_password(mocker, user):
        mocker.patch.object(UsersRepository, "get_user_by_username", return_value=None)
        mock_generate_pw = mocker.patch.object(AuthService, "generate_password")
        mock_hash_pw = mocker.patch.object(
            AuthService, "hash_password", return_value="hashed_password"
        )
        id = uuid4()
        mocker.patch.object(UsersRepository, "create_user", return_value=id)

        created_id, initial_password = UsersService.create_user(
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            user_group=user.user_group,
            password="given_password",
        )

        assert created_id == id
        assert initial_password == "given_password"
        mock_hash_pw.assert_called_once_with("given_password")
        mock_generate_pw.assert_not_called()

    def it_uses_given_location(mocker, user, location):
        mocker.patch.object(UsersRepository, "get_user_by_username", return_value=None)
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
            first_name=user.first_name,
            last_name=user.last_name,
            username=user.username,
            user_group=user.user_group,
            location_id=location.id,
        )

        assert created_id == id
        assert initial_password == "password"
        mock_create_user.assert_called_once()


def describe_update_user():
    def it_checks_if_new_username_is_taken(mocker, user, user_standortleitung):
        mocker.patch.object(
            UsersRepository, "get_user_by_username", return_value=user_standortleitung
        )

        with pytest.raises(AlreadyExistsError):
            UsersService.update_user(
                user,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user_standortleitung.username,
                user_group=user.user_group,
            )

    def it_updates_user(mocker, user):
        mock_get_user_by_username = mocker.patch.object(
            UsersRepository, "get_user_by_username", return_value=None
        )
        mock_update_user = mocker.patch.object(
            UsersRepository, "update_user", return_value=user
        )

        updated_user = UsersService.update_user(
            user,
            first_name="Max",
            last_name="Mustermann",
            username="maxmustermann",
            user_group=UserGroup.standortleitung,
        )

        assert updated_user == user
        assert user.first_name == "Max"
        assert user.last_name == "Mustermann"
        assert user.username == "maxmustermann"
        assert user.user_group == UserGroup.standortleitung
        assert user.location is None
        mock_get_user_by_username.assert_called_once_with("maxmustermann")
        mock_update_user.assert_called_once_with(user)

    def it_updates_user_with_location(mocker, user, location):
        mock_get_user_by_username = mocker.patch.object(
            UsersRepository, "get_user_by_username", return_value=None
        )
        mock_update_user = mocker.patch.object(
            UsersRepository, "update_user", return_value=user
        )

        updated_user = UsersService.update_user(
            user,
            first_name="Max",
            last_name="Mustermann",
            username="maxmustermann",
            user_group=UserGroup.standortleitung,
            location=location,
        )

        assert updated_user == user
        assert user.location == location
        mock_get_user_by_username.assert_called_once_with("maxmustermann")
        mock_update_user.assert_called_once_with(user)

    def it_doesnt_check_username_if_it_not_changed(mocker, user):
        mock_get_user_by_username = mocker.patch.object(
            UsersRepository, "get_user_by_username", return_value=user
        )
        mock_update_user = mocker.patch.object(
            UsersRepository, "update_user", return_value=user
        )

        updated_user = UsersService.update_user(
            user,
            first_name="Max",
            last_name="Mustermann",
            username=user.username,
            user_group=UserGroup.standortleitung,
        )

        assert updated_user == user
        assert user.first_name == "Max"
        assert user.last_name == "Mustermann"
        assert user.username == user.username
        assert user.user_group == UserGroup.standortleitung
        assert user.location is None
        mock_get_user_by_username.assert_not_called()
        mock_update_user.assert_called_once_with(user)


def describe_block_user():
    def it_blocks_user(mocker, user):
        mock_update_user = mocker.patch.object(
            UsersRepository, "update_user", return_value=user
        )

        assert not user.blocked

        UsersService.block_user(user)

        assert user.blocked
        mock_update_user.assert_called_once_with(user)


def describe_unblock_user():
    def it_unblocks_user(mocker, user):
        mock_update_user = mocker.patch.object(
            UsersRepository, "update_user", return_value=user
        )

        user.blocked = True
        assert user.blocked

        UsersService.unblock_user(user)

        assert not user.blocked
        mock_update_user.assert_called_once_with(user)


def describe_delete_user():
    pass


def describe_reset_password():
    def it_resets_to_a_generated_password(mocker, user):
        mock_generate_pw = mocker.patch.object(
            AuthService, "generate_password", return_value="random_password"
        )
        mock_hash_pw = mocker.patch.object(
            AuthService, "hash_password", return_value="hashed_password"
        )
        mock_update_user = mocker.patch.object(
            UsersRepository, "update_user", return_value=user
        )
        mock_invalidate_all_refresh_tokens = mocker.patch.object(
            AuthService, "invalidate_all_refresh_tokens"
        )

        UsersService.reset_password(user)

        assert user.hashed_password == "hashed_password"
        mock_generate_pw.assert_called_once()
        mock_hash_pw.assert_called_once_with("random_password")
        mock_update_user.assert_called_once_with(user)
        mock_invalidate_all_refresh_tokens.assert_called_once_with(user.id)


def describe_get_group_leader():
    def it_returns_group_leader(mocker, user_gruppenleitung):
        mocker.patch.object(
            UsersRepository, "get_group_leader", return_value=[user_gruppenleitung]
        )

        group_leader = UsersService.get_group_leader()

        assert group_leader == [user_gruppenleitung]


def describe_get_location_leader():
    def it_returns_location_leader(mocker, user_standortleitung):
        mocker.patch.object(
            UsersRepository, "get_location_leader", return_value=[user_standortleitung]
        )

        location_leader = UsersService.get_location_leader()

        assert location_leader == [user_standortleitung]
