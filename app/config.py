import os
from flask import request, jsonify  # Importar request y jsonify desde Flask
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

def check_admin_auth():
    # Aquí se usa request para obtener los headers de la solicitud
    username = request.headers.get("X-Admin-Username")
    password = request.headers.get("X-Admin-Password")

    # Verifica si las credenciales son correctas
    if username != os.getenv("ADMIN_USERNAME") or password != os.getenv("ADMIN_PASSWORD"):
        return jsonify({"message": "Acceso denegado"}), 403
    return None

class Config:
    """Configuración base de la aplicación."""
    SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")  # Clave secreta para Flask
    DEBUG = os.getenv("DEBUG", "True") == "True"  # Convertir a booleano
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")  # Nombre de usuario para admin
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")  # Contraseña para admin

class DevelopmentConfig(Config):
    """Configuración para desarrollo."""
    DEBUG = True

class ProductionConfig(Config):
    """Configuración para producción."""
    DEBUG = False

# Mapeo de entornos
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig
}
