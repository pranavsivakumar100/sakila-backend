import jwt
from datetime import datetime, timedelta, timezone
from ..db import get_session, models
from flask import current_app

''' Generate JWT token for staff member '''
def generate_token(staff_id: int):
    payload = {
        'staff_id': staff_id,
        'exp': datetime.now(timezone.utc) + timedelta(hours=24),  # Token expires in 24 hours
        'iat': datetime.now(timezone.utc)  # Issued at
    }
    
    token = jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    return token

''' Verify JWT token and return staff_id '''
def verify_token(token):
   
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        staff_id = payload['staff_id']
        
        # Verify staff exists in database
        session = get_session()
        staff = models["staff"]
        staff_obj = session.get(staff, staff_id)
        
        if not staff_obj:
            return None, "Staff member not found"
        
        return staff_id, None
        
    except jwt.ExpiredSignatureError:
        return None, "Token has expired"
    except jwt.InvalidTokenError:
        return None, "Invalid token"
    except Exception as e:
        return None, f"Token verification failed: {str(e)}"

''' Authenticate staff member with username and password '''
def authenticate_staff(username: str, password: str):
    
    session = get_session()
    staff = models["staff"]
    
    # Find staff by username (assuming username field exists)
    staff_obj = (
        session.query(staff)
        .filter(staff.username == username)
        .first()
    )
    
    if not staff_obj:
        return None, "Invalid username or password"
    
    if staff_obj.password != password:
        return None, "Invalid username or password"
    
    return staff_obj.staff_id, None

''' Get staff member details '''
def get_staff_details(staff_id: int):
    session = get_session()
    staff = models["staff"]
    
    staff_obj = session.get(staff, staff_id)
    if not staff_obj:
        return None
    
    return {
        "staff_id": staff_obj.staff_id,
        "first_name": staff_obj.first_name,
        "last_name": staff_obj.last_name,
        "username": staff_obj.username,
        "email": staff_obj.email if hasattr(staff_obj, 'email') else None,
        "active": staff_obj.active
    }