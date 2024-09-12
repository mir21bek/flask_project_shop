from flask import Blueprint, jsonify, request
from app.extensions import db
from .models import Category, Product
from user_app.models import User, RoleEnum
from flask_jwt_extended import get_jwt_identity, jwt_required


product_blueprint = Blueprint('product', __name__)

@product_blueprint.route("/categories", methods=["POST"])
def create_cat():
    data = request.get_json()

    if not data or not "name" in data:
        return jsonify({"error": "Invalid data"}), 400

    parent_id = data.get("parent_id")

    if parent_id:
        parent_cat = Category.query.get(parent_id)
        if not parent_cat:
            return jsonify({"error": "Parent category not found"}), 404
        else:
            parent_cat = None

    category = Category(name=data["name"], parent_id=parent_id)
    db.session.add(category)
    db.session.commit()

    return (
        jsonify(
            {"Message": "Category created successfully", "category": category.to_dict()}
        ),
        201,
    )


@product_blueprint.route("/categories", methods=["GET"])
def get_cat():
    parent_id = request.args.get("parent_id", type=int)

    if parent_id is not None:
        cats = Category.query.filter_by(parent_id=parent_id).all()
    else:
        cats = Category.query.all()
    return ([cat.to_dict() for cat in cats]), 200


@product_blueprint.route("/categories/<int:cat_id>", methods=["DELETE"])
def delete_cat(cat_id):
    cat = Category.query.get(cat_id)

    if cat is None:
        return jsonify({"error": "Category not found"}), 404

    if cat.children:
        return (
            jsonify(
                {
                    "error": "Category has child categories. Please remove child categories first"
                }
            ),
            400,
        )

    db.session.delete(cat)
    db.session.commit()
    return jsonify({"Message": "Category deleted successfully"}), 200


@product_blueprint.route("/product-create", methods=["POST"])
@jwt_required()
def create_product():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or user.role.name != RoleEnum.ADMIN:
        return jsonify({"error": "Access denied. Only admins can create products."})
    data = request.get_json()

    if not data or not all(
        pro in data for pro in ["category_id", "name", "title", "price"]
    ):
        return jsonify({"error": "Invalid data"}), 400

    category_id = data.get("category_id")

    if category_id:
        category = Category.query.get(category_id)
        if not category:
            return jsonify({"error": "Category id not found"}), 404
    else:
        category = None

    product = Product(
        name=data["name"],
        title=data["title"],
        price=data["price"],
        category_id=category.id if category else None,
    )
    db.session.add(product)
    db.session.commit()
    return (
        jsonify(
            {"Message": "Product create successfully", "product": product.to_dict()}
        ),
        201,
    )


@product_blueprint.route("/product-list", methods=["GET"])
def product_list():
    products = Product.query.all()
    return ([product.to_dict() for product in products]), 200


@product_blueprint.route("/category/<int:category_id>/products", methods=["GET"])
def get_products_by_category(category_id):
    category = Category.query.get(category_id)

    if not category:
        return jsonify({"error": "Category not found"}), 404

    products = Product.query.filter_by(category_id=category_id).all()

    if not products:
        return jsonify({"error": "No products found in this category"}), 404

    products_list = [product.to_dict() for product in products]

    return jsonify({"category": category.name, "products": products_list}), 200

