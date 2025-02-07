from flask import Flask
from flasgger import Swagger
from app.routes.products import products_bp
from app.routes.paypal import paypal_bp
from app.config import config
from flask_cors import CORS

def create_app(env="development"):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config[env])  # Cargar configuración según el entorno

    # Inicializa Swagger para documentación automática
    Swagger(app)

    # Registrar Blueprints
    app.register_blueprint(products_bp, url_prefix="/products")
    app.register_blueprint(paypal_bp, url_prefix="/paypal")  # Registrar PayPal

    return app
