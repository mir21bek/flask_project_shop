from datetime import timedelta

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token

from app.extensions import db

from .models import (
    Group,
    GroupEnum,
    Permission,
    PermissionEnum,
    PermissionGroup,
    Role,
    RoleEnum,
    User,
)

user_blueprint = Blueprint("users", __name__)


@user_blueprint.route("/admin-create", methods=["POST"])
def create_admin():
    data = request.get_json()
    if not data or not all(k in data for k in ["username", "email", "password"]):
        return jsonify({"error": "Invalid data"}), 400

    if (
        User.query.filter_by(username=data["username"]).first()
        or User.query.filter_by(email=data["email"]).first()
    ):
        return jsonify({"message": "This username or email already exists"}), 400

    user = User(username=data["username"], email=data["email"])
    user.set_password(data["password"])

    try:
        # Отключаем автофлеш для избежания ошибки
        with db.session.no_autoflush:
            # Добавление пользователя в сессию
            db.session.add(user)

            # Получаем роль администратора
            admin_role = Role.query.filter_by(name=RoleEnum.ADMIN).first()
            if not admin_role:
                admin_role = Role(name=RoleEnum.ADMIN)
                db.session.add(admin_role)

            # Получаем группу администратора
            admin_group = Group.query.filter_by(name=GroupEnum.ADMIN).first()
            if not admin_group:
                admin_group = Group(name=GroupEnum.ADMIN)
                db.session.add(admin_group)

            # Назначаем роль и группу пользователю
            user.role = admin_role
            user.group = admin_group

            permissions = [
                Permission(name=PermissionEnum.CREATE_UPDATE),
                Permission(name=PermissionEnum.DELETE),
                Permission(name=PermissionEnum.LIST_VIEW),
            ]

            for perm in permissions:
                existing_perm = Permission.query.filter_by(name=perm.name).first()
                if not existing_perm:
                    db.session.add(perm)
                else:
                    permissions[permissions.index(perm)] = existing_perm

        # Осуществляем явный flush для всех изменений
        db.session.flush()

        # Сохраняем связи разрешений и групп
        for perm in permissions:
            if not PermissionGroup.query.filter_by(
                group_id=admin_group.id, permission_id=perm.id
            ).first():
                group_perm = PermissionGroup(
                    group_id=admin_group.id, permission_id=perm.id
                )
                db.session.add(group_perm)

        db.session.commit()  # Подтверждаем транзакцию

    except Exception as e:
        db.session.rollback()  # Откат транзакции в случае ошибки
        return jsonify({"error": str(e)}), 500

    return (
        jsonify({"Message": "User created successfully", "user": user.to_dict()}),
        201,
    )




@user_blueprint.route("/buyer-create", methods=["POST"])
def create_buyer():
    data = request.get_json()
    if not data or not all(k in data for k in ["username", "email", "password"]):
        return jsonify({"error": "Invalid data"}), 400

    if (
        User.query.filter_by(username=data["username"]).first()
        or User.query.filter_by(email=data["email"]).first()
    ):
        return jsonify({"message": "This username or email already exists"}), 400

    user = User(username=data["username"], email=data["email"])
    user.set_password(data["password"])

    try:
        # Начало транзакции
        user_role = Role.query.filter_by(name=RoleEnum.BUYER).first()
        if not user_role:
            user_role = Role(name=RoleEnum.BUYER)
            db.session.add(user_role)

        user_group = Group.query.filter_by(name=GroupEnum.ADMIN).first()
        if not user_group:
            admin_group = Group(name=GroupEnum.BUYER)
            db.session.add(user_group)

        user.role = user_role
        user.group = user_group

        permissions = [Permission(name=PermissionEnum.LIST_VIEW)]

        for perm in permissions:
            existing_perm = Permission.query.filter_by(name=perm.name).first()
            if not existing_perm:
                db.session.add(perm)
            else:
                permissions[permissions.index(perm)] = existing_perm

        db.session.flush()  # Flush to ensure permissions have IDs before using them

        for perm in permissions:
            if not PermissionGroup.query.filter_by(
                group_id=user_group.id, permission_id=perm.id
            ).first():
                group_perm = PermissionGroup(
                    group_id=user_group.id, permission_id=perm.id
                )
                db.session.add(group_perm)

        db.session.add(user)
        db.session.commit()  # Подтверждение транзакции

    except Exception as e:
        db.session.rollback()  # Откат транзакции в случае ошибки
        return jsonify({"error": str(e)}), 500

    return (
        jsonify({"Message": "User created successfully", "user": user.to_dict()}),
        201,
    )


@user_blueprint.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Bad email or password"}), 401

    expires = timedelta(hours=1)
    access_token = create_access_token(identity=user.id, expires_delta=expires)
    return jsonify(access_token=access_token), 201


@user_blueprint.route("/all-users", methods=["GET"])
def get_user():
    users = User.query.all()
    return ([user.to_dict() for user in users]), 200
