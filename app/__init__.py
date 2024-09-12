from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from app_config.config import Config
from app.extensions import db, migrate
from user_app.routes import user_blueprint
from product_app.routes import product_blueprint


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(Config)
    JWTManager(app)

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(user_blueprint, url_prefix="/users")
    app.register_blueprint(product_blueprint, url_prefix="/products")

    return app
