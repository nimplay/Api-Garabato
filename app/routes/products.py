import json
import os
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from datetime import datetime
from app.config import check_admin_auth  # Importamos la función de autenticación

load_dotenv()

products_bp = Blueprint("products", __name__)

# Función para cargar los productos desde el archivo JSON
def load_products():
    with open("app/models/products.json", "r") as f:
        return json.load(f)

# Función para guardar los productos en el archivo JSON
def save_products(products):
    with open("app/models/products.json", "w") as f:
        json.dump(products, f, indent=4)

@products_bp.route("/", methods=["GET", "POST"])
def manage_products():
    """
    Obtener o agregar productos
    ---
    get:
      description: Obtiene la lista de productos
      responses:
        200:
          description: Lista de productos
          schema:
            type: array
            items:
              type: object
              properties:
                id:
                  type: integer
                name:
                  type: string
                currency:
                  type: string
                subcategory:
                  type: array
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                      img:
                        type: string
                        format: uri
                      description:
                        type: string
                      price:
                        type: number
                created_at:
                  type: string
                  format: date-time
                updated_at:
                  type: string
                  format: date-time
    post:
      description: Agrega un nuevo producto (solo admin)
      parameters:
        - name: X-Admin-Username
          in: header
          type: string
          required: true
          description: Nombre de usuario del administrador
        - name: X-Admin-Password
          in: header
          type: string
          required: true
          description: Contraseña del administrador
        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
              name:
                type: string
              currency:
                type: string
              subcategory:
                type: array
                items:
                  type: object
                  properties:
                    name:
                      type: string
                    img:
                      type: string
                      format: uri
                    description:
                      type: string
                    price:
                      type: number
      responses:
        201:
          description: Producto agregado exitosamente
        403:
          description: Acceso denegado
    """
    if request.method == "GET":
        products = load_products()
        return jsonify(products)

    elif request.method == "POST":
        # Verificar si el administrador está autenticado
        auth_error = check_admin_auth()
        if auth_error:
            return auth_error

        data = request.get_json()
        products = load_products()
        new_id = max((p["id"] for p in products), default=0) + 1

        new_product = {
            "id": new_id,
            "name": data.get("name"),
            "currency": data.get("currency"),
            "subcategory": data.get("subcategory", []),
            "created_at": datetime.utcnow().isoformat() + "Z",
            "updated_at": datetime.utcnow().isoformat() + "Z"
        }

        products.append(new_product)
        save_products(products)

        return jsonify({"message": "Producto agregado", "id": new_id}), 201

@products_bp.route("/<int:product_id>", methods=["GET", "PUT", "DELETE"])
def product_operations(product_id):
    """
    Operaciones CRUD para un producto específico
    ---
    get:
      description: Obtiene un producto por ID
      parameters:
        - name: product_id
          in: path
          type: integer
          required: true
      responses:
        200:
          description: Producto encontrado
          schema:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              currency:
                type: string
              subcategory:
                type: array
                items:
                  type: object
                  properties:
                    name:
                      type: string
                    img:
                      type: string
                      format: uri
                    description:
                      type: string
                    price:
                      type: number
              created_at:
                type: string
                format: date-time
              updated_at:
                type: string
                format: date-time
        404:
          description: Producto no encontrado
    put:
      description: Actualiza un producto por ID (solo admin)
      parameters:
        - name: X-Admin-Username
          in: header
          type: string
          required: true
          description: Nombre de usuario del administrador
        - name: X-Admin-Password
          in: header
          type: string
          required: true
          description: Contraseña del administrador
        - name: product_id
          in: path
          type: integer
          required: true
        - name: body
          in: body
          required: true
          schema:
            type: object
            properties:
              name:
                type: string
              currency:
                type: string
              subcategory:
                type: array
                items:
                  type: object
                  properties:
                    name:
                      type: string
                    img:
                      type: string
                      format: uri
                    description:
                      type: string
                    price:
                      type: number
      responses:
        200:
          description: Producto actualizado exitosamente
        403:
          description: Acceso denegado
        404:
          description: Producto no encontrado
    delete:
      description: Elimina un producto por ID (solo admin)
      parameters:
        - name: X-Admin-Username
          in: header
          type: string
          required: true
          description: Nombre de usuario del administrador
        - name: X-Admin-Password
          in: header
          type: string
          required: true
          description: Contraseña del administrador
        - name: product_id
          in: path
          type: integer
          required: true
      responses:
        200:
          description: Producto eliminado exitosamente
        403:
          description: Acceso denegado
        404:
          description: Producto no encontrado
    """
    products = load_products()
    product = next((p for p in products if p["id"] == product_id), None)

    if not product:
        return jsonify({"message": "Producto no encontrado"}), 404

    if request.method == "GET":
        return jsonify(product)

    if request.method == "PUT":
        # Verificar si el administrador está autenticado
        auth_error = check_admin_auth()
        if auth_error:
            return auth_error

        data = request.get_json()
        product.update({
            "name": data.get("name", product["name"]),
            "currency": data.get("currency", product["currency"]),
            "subcategory": data.get("subcategory", product["subcategory"]),
            "updated_at": datetime.utcnow().isoformat() + "Z"
        })

        save_products(products)
        return jsonify({"message": "Producto actualizado exitosamente"}), 200

    if request.method == "DELETE":
        # Verificar si el administrador está autenticado
        auth_error = check_admin_auth()
        if auth_error:
            return auth_error

        products.remove(product)
        save_products(products)

        return jsonify({"message": "Producto eliminado exitosamente"}), 200
