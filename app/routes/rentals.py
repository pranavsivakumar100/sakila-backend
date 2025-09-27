from flask import Blueprint, jsonify, request
from ..services import rental_service

bp = Blueprint("rentals", __name__)

'''
    POST /api/rentals
    Create a new rental
    Payload: {"customer_id": int, "film_id": int, "staff_id": int (optional)}
'''
@bp.post("/")
@bp.post("")
def create_rental():
    data = request.get_json()
    
    if not data:
        return {"error": "Request body is required"}, 400
    
    customer_id = data.get('customer_id')
    film_id = data.get('film_id')
    staff_id = data.get('staff_id', 1)  # Default staff_id = 1 (change this later)
    
    if not customer_id or not film_id:
        return {"error": "customer_id and film_id are required"}, 400
    
    result, status_code = rental_service.create_rental(customer_id, film_id, staff_id)
    return jsonify(result), status_code

'''
    GET /api/rentals/<rental_id>
    Get rental details
'''
@bp.get("/<int:rental_id>")
def get_rental_details(rental_id: int):
    result, status_code = rental_service.get_rental_details(rental_id)
    return jsonify(result), status_code

'''
    PUT /api/rentals/<rental_id>/return
    Return a rented film
'''
@bp.put("/<int:rental_id>/return")
def return_rental(rental_id: int):
    result, status_code = rental_service.return_rental(rental_id)
    return jsonify(result), status_code
