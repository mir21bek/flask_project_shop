from datetime import datetime

import pytest

from app import create_app
from app.extensions import db
from users_app.models import GroupEnum, Group, RoleEnum, Role, User


@pytest.fixture()
def app():
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        }
    )
    with app.app_context():
        db.create_all()
        if not Role.query.filter_by(name=RoleEnum.ADMIN).first():
            admin_role = Role(name=RoleEnum.ADMIN)
            db.session.add(admin_role)
            db.session.commit()

        if not Group.query.filter_by(name=GroupEnum.ADMIN).first():
            admin_group = Group(name=GroupEnum.ADMIN)
            db.session.add(admin_group)

            if not Role.query.filter_by(name=RoleEnum.BUYER).first():
                user_role = Role(name=RoleEnum.BUYER)
                db.session.add(user_role)

            if not Group.query.filter_by(name=GroupEnum.BUYER).first():
                user_group = Group(name=GroupEnum.BUYER)
                db.session.add(user_group)

            db.session.commit()
        yield app

    with app.app_context():
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


def test_create_admin(client, app):
    data = {"username": "admin", "email": "admin@mail.ru", "password": "admin12345"}
    response = client.post("/users/admin-create", json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["Message"] == "User created successfully"
    assert json_data["user"]["username"] == "admin"


def test_create_invalid_data(client, app):
    data = {
        "username": "admin",
        "email": "admin@mail.ru",
    }

    response = client.post("/users/admin-create", json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["error"] == "Invalid data"


def test_create_admin_exition(client, app):
    admin_role = Role.query.filter_by(name=RoleEnum.ADMIN).first()
    admin_group = Group.query.filter_by(name=GroupEnum.ADMIN).first()

    if not admin_role or not admin_group:
        raise ValueError("admin role or admin group not found")

    user = User(
        username="admin",
        email="admin@mail.ru",
        role_id=admin_role.id,
        group_id=admin_group.id,
    )
    user.set_password("admin12345")
    db.session.add(user)
    db.session.commit()

    data = {
        "username": "admin",
        "email": "admin@mail.ru",
        "password": "admin12345",
    }

    response = client.post("/users/admin-create", json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["message"] == "This username or email already exists"


def test_create_user(client, app):
    data = {"username": "user", "email": "user@mail.ru", "password": "user12345"}

    response = client.post("/users/buyer-create", json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["Message"] == "User created successfully"
    assert json_data["user"]["username"] == "user"


def test_invalid_data(client, app):
    data = {
        "username": "user",
        "email": "user@mail.ru",
    }

    response = client.post("/users/buyer-create", json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["error"] == "Invalid data"


def test_create_user_exition(client, app):
    user_role = Role.query.filter_by(name=RoleEnum.BUYER).first()
    user_group = Group.query.filter_by(name=GroupEnum.BUYER).first()

    if not user_role or not user_group:
        raise ValueError("user group or user role not found")

    user = User(
        username="user", email="email", role_id=user_role.id, group_id=user_group.id
    )

    user.set_password("user12345")
    db.session.add(user)
    db.session.commit()

    data = {"username": "user", "email": "user@mail.ru", "password": "user12345"}

    response = client.post("/users/buyer-create", json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data["message"] == "This username or email already exists"


def test_login_user(client, app):
    user_data = {"username": "user", "email": "user@mail.ru", "password": "user12345"}

    client.post("/users/buyer-create", json=user_data)

    login_data = {
        "email": "user@mail.ru",
        "password": "user12345"
    }
    response = client.post("/users/login", json=login_data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert "access_token" in json_data
