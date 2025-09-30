from flask import Blueprint, jsonify, request
from ..services import customer_service
from .auth import require_auth

bp = Blueprint("customers", __name__)

'''
    GET /api/customers
    Get all customers
'''
@bp.get("/")
def get_customers():
    result = customer_service.get_customers()
    return jsonify(result), 200

'''
    GET /api/customers/<customer_id>
    Get customer details
'''
@bp.get("/<int:customer_id>")
def get_customer_details(customer_id: int):
    result = customer_service.get_customer_details(customer_id)
    if not result:
        return {"error": "Customer not found"}, 404
    return jsonify(result), 200

'''
    POST /api/customers
    Create a new customer
    Payload: {"first_name": str, "last_name": str, "email": str (optional), "store_id": int (optional), "address_id": int (optional)}
'''
@bp.post("/")
def create_customer():
    data = request.get_json()
    
    if not data:
        return {"error": "Request body is required"}, 400
    
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    store_id = data.get('store_id', 1)  # Default to store 1
    address_id = data.get('address_id')
    
    if not first_name or not last_name:
        return {"error": "first_name and last_name are required"}, 400
    
    result = customer_service.create_customer(first_name, last_name, email, store_id, address_id)
    if isinstance(result, dict) and 'error' in result:
        return jsonify(result), 500
    
    return jsonify(result), 201

'''
    PUT /api/customers/<customer_id>
    Update customer details
    Payload: {"first_name": str (optional), "last_name": str (optional), "email": str (optional), "store_id": int (optional), "address_id": int (optional), "active": int (optional)}
'''
@bp.put("/<int:customer_id>")
@require_auth
def update_customer(customer_id: int, staff_id):
    data = request.get_json()
    
    if not data:
        return {"error": "Request body is required"}, 400
    
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    email = data.get('email')
    store_id = data.get('store_id')
    address_id = data.get('address_id')
    active = data.get('active')
    
    result = customer_service.update_customer(customer_id, first_name, last_name, email, store_id, address_id, active)
    if isinstance(result, dict) and 'error' in result:
        status_code = 404 if "not found" in result.get('error', '') else 500
        return jsonify(result), status_code
    
    return jsonify(result), 200

'''
    DELETE /api/customers/<customer_id>
    Delete a customer
'''
@bp.delete("/<int:customer_id>")
@require_auth
def delete_customer(customer_id: int, staff_id):
    result, status_code = customer_service.delete_customer(customer_id)
    return jsonify(result), status_code

'''
    GET /api/customers/<customer_id>/rentals
    Get customer rental history (active and past rentals)
'''
@bp.get("/<int:customer_id>/rentals")
@require_auth
def get_customer_rental_history(customer_id: int, staff_id):
    result = customer_service.get_customer_rental_history(customer_id)
    if isinstance(result, dict) and 'error' in result:
        status_code = 404 if "not found" in result.get('error', '') else 500
        return jsonify(result), status_code
    
    return jsonify(result), 200

'''
    PUT /api/customers/<customer_id>/rentals/<rental_id>/return
    Mark a customer's rental as returned
'''
@bp.put("/<int:customer_id>/rentals/<int:rental_id>/return")
@require_auth
def return_customer_rental(customer_id: int, rental_id: int, staff_id):
    result, status_code = customer_service.return_customer_rental(rental_id)
    return jsonify(result), status_code
