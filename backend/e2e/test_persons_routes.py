"""End-to-end tests for the persons routes."""

import uuid
from .helper import *  # for fixtures # noqa: F403
from .helper import login


def describe_persons_create_qr():
    def it_returns_404_when_person_not_found(client, db, user_verwaltung):
        db.session.add(user_verwaltung)
        db.session.commit()
        login(user=user_verwaltung, client=client)

        res = client.get("/api/persons/create-qr/{}".format(uuid.uuid4()))

        assert res.status_code == 404
        assert res.json["title"] == "Person existiert nicht"

    def it_returns_pdf_response(client, db, user_verwaltung):
        db.session.add(user_verwaltung)
        db.session.commit()
        login(user=user_verwaltung, client=client)

        res = client.get("/api/persons/create-qr/{}".format(user_verwaltung.id))

        assert res.status_code == 200
        assert res.headers["Content-Type"] == "application/pdf"
