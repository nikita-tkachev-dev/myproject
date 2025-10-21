import pytest
from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    return app


@pytest.fixture
def client(app):
    return app.test_client()


def test_register_page(client):
    r = client.get("/users/register")
    assert r.status_code == 200


def test_login_page(client):
    r = client.get("/users/login")
    assert r.status_code == 200


def test_register_json_missing_fields(client):
    r = client.post("/users/create", json={})
    assert r.status_code == 400 or r.status_code == 500
