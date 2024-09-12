from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash
from app.extensions import db
from enum import Enum


class RoleEnum(Enum):
    ADMIN = "admin"
    BUYER = "buyer"


class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(RoleEnum), nullable=False, unique=True)

    def __repr__(self):
        return f"Role: <{self.name}>"


class GroupEnum(Enum):
    ADMIN = "admin"
    BUYER = "buyer"


class Group(db.Model):
    __tablename__ = "groups"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(GroupEnum), nullable=False, unique=True)
    description = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PermissionEnum(Enum):
    CREATE_UPDATE = "create_update"
    DELETE = "delete"
    LIST_VIEW = "list_view"


class Permission(db.Model):
    __tablename__ = "permissions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum(PermissionEnum), nullable=False, unique=True)
    description = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class PermissionGroup(db.Model):
    __tablename__ = "permission_groups"
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), primary_key=True)
    permission_id = db.Column(
        db.Integer, db.ForeignKey("permissions.id"), primary_key=True
    )
    group = db.relationship("Group", backref="permission_groups")
    permission = db.relationship("Permission", backref="permission_groups")


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, unique=True, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"), nullable=False)
    role = db.relationship("Role", backref="users")
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=False)
    group = db.relationship("Group", backref="users")

    def __repr__(self):
        return f"User: <{self.username}>"

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }
