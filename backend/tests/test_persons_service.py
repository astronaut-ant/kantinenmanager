"""Tests for persons service."""

import pytest
from uuid import uuid4
from src.utils.pdf_creator import PDFCreationUtils
from src.services.persons_service import PersonsService
from src.repositories.persons_repository import PersonsRepository
from src.utils.exceptions import (
    NotFoundError,
)
from .helper import *  # for fixtures # noqa: F403


def describe_create_qr_code_person():
    def it_raises_when_person_not_found(mocker):
        mocker.patch.object(PersonsRepository, "get_person_by_id", return_value=None)

        with pytest.raises(NotFoundError):
            PersonsService.create_qr_code_person(person_id=uuid4())

    def it_returns_pdf_response(mocker, user_verwaltung):
        mocker.patch.object(
            PersonsRepository, "get_person_by_id", return_value=user_verwaltung
        )
        mock_create_qr = mocker.patch.object(
            PDFCreationUtils, "create_qr_code_person", return_value="pdf"
        )

        response = PersonsService.create_qr_code_person(person_id=user_verwaltung.id)

        assert response == "pdf"
        mock_create_qr.assert_called_once_with(user_verwaltung)
