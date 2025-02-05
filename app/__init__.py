from flask import Flask
from flasgger import Swagger
from app.routes.products import products_bp  # Solo dejamos productos
from app.config import config

def create_app(env="development"):
    app = Flask(__name__)
    app.config.from_object(config[env])  # Cargar configuración según el entorno

    Swagger(app)

    # Registrar Blueprints
    # Eliminamos el registro del blueprint de usuarios
    app.register_blueprint(products_bp, url_prefix="/products")

    return app
