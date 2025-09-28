from functools import wraps
from flask import request, jsonify, Blueprint
from ..services.auth_service import verify_token, authenticate_staff, generate_token, get_staff_details

bp = Blueprint("auth", __name__)

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Get token from Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]  # Bearer <token>
            except IndexError:
                return jsonify({"error": "Invalid token format"}), 401
        
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        
        staff_id, error = verify_token(token)
        if error:
            return jsonify({"error": error}), 401
        
        # Pass staff_id to the route function
        return f(staff_id=staff_id, *args, **kwargs)
    
    return decorated_function

'''
    POST /api/auth/login
    Staff login endpoint
    Payload: {"username": str, "password": str}
'''
@bp.post("/login")
def login():
    data = request.get_json()
    
    if not data:
        return {"error": "Request body is required"}, 400
    
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return {"error": "Username and password are required"}, 400
    
    staff_id, error = authenticate_staff(username, password)
    if error:
        return {"error": error}, 401
    
    # Generate token
    token = generate_token(staff_id)
    
    # Get staff details
    staff_details = get_staff_details(staff_id)
    
    return {
        "message": "Login successful",
        "token": token,
        "staff": staff_details
    }, 200

'''
    POST /api/auth/verify
    Verify token validity
    Body: {"token": str}
'''
@bp.post("/verify")
def verify():
    data = request.get_json()
    
    if not data or 'token' not in data:
        return {"error": "Token is required"}, 400
    
    token = data['token']
    staff_id, error = verify_token(token)
    
    if error:
        return {"error": error}, 401
    
    staff_details = get_staff_details(staff_id)
    return {
        "valid": True,
        "staff": staff_details
    }, 200