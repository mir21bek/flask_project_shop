import os

import pytest
import tempfile

from app import create_app
from app.extensions import db
from models.user_models import GroupEnum, Group, RoleEnum, Role, User
from models.product_models import Product, Category


@pytest.fixture()
def app():
    db_fd, db_path = tempfile.mkstemp()
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": f"sqlite:///{db_path}",
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

    os.close(db_fd)
    os.unlink(db_path)


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


def test_get_user(client):
    user_role = Role.query.filter_by(name=RoleEnum.BUYER).first()
    user_group = Group.query.filter_by(name=GroupEnum.BUYER).first()

    if not user_role:
        user_role = Role(name=RoleEnum.BUYER)
        db.session.add(user_role)
    if not user_group:
        user_group = Group(name=GroupEnum.BUYER)
        db.session.add(user_group)
    db.session.commit()

    data = [
        {"username": "user1", "email": "user1@mail.ru", "password": "user12345"},
        {"username": "user2", "email": "user2@mail.ru", "password": "user12345"},
        {"username": "user3", "email": "user3@mail.ru", "password": "user12345"},

    ]

    for user_data in data:
        user  = User(username=user_data["username"], email=user_data["email"], role_id=user_role.id, group_id=user_group.id)
        user.set_password(user_data["password"])
        db.session.add(user)
    db.session.commit()

    response = client.get("/users/all-users")

    assert response.status_code == 200
    json_data = response.get_json()

    assert len(json_data) == len(data)

    for users_data in data:
        assert any(user["username"] == users_data["username"] for user in json_data)
        assert any(user["email"] == users_data["email"] for user in json_data)


def test_create_product(app, client):
    login_data = {
        "email": "user@mail.ru",
        "password": "user12345",
    }
    login_response = client.post("/users/login", json=login_data)
    assert login_response.status_code == 200
    json_login_data = login_response.get_json()
    token = json_login_data["access_token"]
    print(token)

    data = {
        "category_id": 1,
        "name": "Samsung",
        "title": "cool phone",
        "price": 300
    }

    response = client.post("/products/product-create", json=data, headers={"Authorization": f"Bearer Token {token}"})

    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data["Message"] == "Product create successfully"
    assert "product" in json_data

