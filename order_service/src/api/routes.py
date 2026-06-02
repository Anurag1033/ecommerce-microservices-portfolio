from flask import Blueprint, request, jsonify
from src.use_cases.order_ops import create_order

order_blueprint = Blueprint('orders', __name__, url_prefix='/api/v1/orders')

@order_blueprint.route('/', methods=['POST'])
def place_order():
    data = request.get_json()
    
    if not data or 'customer_id' not in data or 'items' not in data:
        return jsonify({"error": "Invalid payload"}), 400
        
    try:
        # Pass the HTTP data into our core application logic
        result = create_order(customer_id=data['customer_id'], items_data=data['items'])
        return jsonify({
            "message": "Order accepted and is being processed",
            "order": result
        }), 202
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal Server Error"}), 500