import os
import requests
from flask import Blueprint, request, jsonify
from dotenv import load_dotenv
from app.config import check_admin_auth

# Cargar variables de entorno desde .env
load_dotenv()

paypal_bp = Blueprint("paypal", __name__)

PAYPAL_API_URL = os.getenv("PAYPAL_API_URL")
PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_SECRET = os.getenv("PAYPAL_SECRET")

# Función para obtener el token de autenticación de PayPal
def get_paypal_token():
    auth = (PAYPAL_CLIENT_ID, PAYPAL_SECRET)
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {"grant_type": "client_credentials"}

    response = requests.post(f"{PAYPAL_API_URL}/v1/oauth2/token", headers=headers, data=data, auth=auth)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        return None

# Ruta para crear una orden de pago con productos detallados
@paypal_bp.route("/create-order", methods=["POST"])
def create_order():
    token = get_paypal_token()
    if not token:
        return jsonify({"message": "Error obteniendo token de PayPal"}), 500

    data = request.json  # Recibe los datos JSON
    products = data.get("products", [])  # Lista de productos seleccionados

    if not products:
        return jsonify({"message": "No se enviaron productos"}), 400

    # Construir la lista de productos para PayPal
    items = []
    total_amount = 0

    for product in products:
        name = product.get("name", "Producto sin nombre")
        description = product.get("description", "")
        quantity = int(product.get("quantity", 1))
        unit_price = float(product.get("price", 0))

        total_amount += unit_price * quantity  # Sumar al total

        items.append({
            "name": name,
            "description": description,
            "quantity": str(quantity),
            "unit_amount": {
                "currency_code": "USD",
                "value": str(unit_price)
            }
        })

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    order_payload = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {
                "currency_code": "USD",
                "value": str(total_amount),
                "breakdown": {
                    "item_total": {
                        "currency_code": "USD",
                        "value": str(total_amount)
                    }
                }
            },
            "items": items
        }],
        "application_context": {
          "return_url": "http://senoragarabato.com/success",  # URL de redirección tras pago exitoso
          "cancel_url": "http://senoragarabato.com/store"  # URL si el usuario cancela el pago
        }
    }

    response = requests.post(f"{PAYPAL_API_URL}/v2/checkout/orders", json=order_payload, headers=headers)

    if response.status_code == 201:
        return jsonify(response.json())  # Retorna el ID de la orden para el frontend
    else:
        return jsonify({"message": "Error creando orden de PayPal", "error": response.json()}), response.status_code

# Capturar el pago
@paypal_bp.route("/capture-order/<order_id>", methods=["POST"])
def capture_order(order_id):
    token = get_paypal_token()
    if not token:
        return jsonify({"message": "Error obteniendo token de PayPal"}), 500

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    response = requests.post(f"{PAYPAL_API_URL}/v2/checkout/orders/{order_id}/capture", headers=headers)

    if response.status_code == 201:
        return jsonify(response.json())
    else:
        return jsonify({"message": "Error capturando el pago", "error": response.json()}), response.status_code
