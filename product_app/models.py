from datetime import datetime

from app.extensions import db


class Category(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    parent = db.relationship("Category", remote_side=[id], backref=("children"))

    def __repr__(self):
        return f"Caegory <{self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "parent_id": self.parent_id,
            "created_at": self.created_at.isoformat(),
        }


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"))
    category = db.relationship("Category", backref="products")
    name = db.Column(db.String(150), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"Product: <{self.name}>"

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "price": self.price,
            "created_at": self.created_at.isoformat(),
        }
