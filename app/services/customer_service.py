from ..db import get_session, models
from datetime import datetime, timedelta
from sqlalchemy import or_, func

''' Helper function to format customer data '''
def _format_customer_data(customer_obj, address_obj=None):
    return {
        "customer_id": customer_obj.customer_id,
        "first_name": customer_obj.first_name,
        "last_name": customer_obj.last_name,
        "email": customer_obj.email if hasattr(customer_obj, 'email') else None,
        "store_id": customer_obj.store_id,
        "address_id": customer_obj.address_id,
        "address": {
            "address_id": address_obj.address_id,
            "address": address_obj.address,
            "address2": address_obj.address2 if hasattr(address_obj, 'address2') else None,
            "district": address_obj.district,
            "city_id": address_obj.city_id,
            "postal_code": address_obj.postal_code if hasattr(address_obj, 'postal_code') else None,
            "phone": address_obj.phone if hasattr(address_obj, 'phone') else None
        } if address_obj else None,
        "active": customer_obj.active,
        "create_date": customer_obj.create_date.isoformat() if customer_obj.create_date else None,
        "last_update": customer_obj.last_update.isoformat() if customer_obj.last_update else None
    }

''' Get all customers '''
def get_customers():
    session = get_session()
    customer, address = models["customer"], models["address"]
    
    # Get all customers with their addresses
    customers = (
        session.query(customer, address)
        .outerjoin(address, address.address_id == customer.address_id)
        .order_by(customer.last_name, customer.first_name)
        .all()
    )
    
    return [_format_customer_data(c, a) for c, a in customers]

''' Search customers by id, first name, or last name '''
def search_customers(search_term: str):
    session = get_session()
    customer, address = models["customer"], models["address"]
    
    # Build search query
    search_filter = or_(
        customer.customer_id.ilike(f"%{search_term}%"),
        customer.first_name.ilike(f"%{search_term}%"),
        customer.last_name.ilike(f"%{search_term}%")
    )
    
    # Get all matching customers with their addresses
    customers = (
        session.query(customer, address)
        .outerjoin(address, address.address_id == customer.address_id)
        .filter(search_filter)
        .order_by(customer.last_name, customer.first_name)
        .all()
    )
    
    return [_format_customer_data(c, a) for c, a in customers]

''' Get customer details '''
def get_customer_details(customer_id: int):
    session = get_session()
    customer, address = models["customer"], models["address"]
    
    result = (
        session.query(customer, address)
        .outerjoin(address, address.address_id == customer.address_id)
        .filter(customer.customer_id == customer_id)
        .first()
    )
    
    if not result:
        return None
    
    c, a = result
    return _format_customer_data(c, a)

''' Create a new customer '''
def create_customer(first_name: str, last_name: str, email: str = None, store_id: int = 1, address_id: int = None):
    session = get_session()
    customer = models["customer"]
    
    # Create new customer
    new_customer = customer(
        first_name=first_name,
        last_name=last_name,
        email=email,
        store_id=store_id,
        address_id=address_id,
        active=1,
        create_date=datetime.now(),
        last_update=datetime.now()
    )
    
    try:
        session.add(new_customer)
        session.commit()
        return get_customer_details(new_customer.customer_id)
    except Exception as e:
        session.rollback()
        return {"error": f"Failed to create customer: {str(e)}"}, 500

''' Update customer details '''
def update_customer(customer_id: int, first_name: str = None, last_name: str = None, email: str = None, store_id: int = None, address_id: int = None, active: int = None):
    session = get_session()
    customer = models["customer"]
    
    customer_obj = session.get(customer, customer_id)
    if not customer_obj:
        return {"error": "Customer not found"}, 404
    
    # Update fields if provided
    if first_name is not None:
        customer_obj.first_name = first_name
    if last_name is not None:
        customer_obj.last_name = last_name
    if email is not None:
        customer_obj.email = email
    if store_id is not None:
        customer_obj.store_id = store_id
    if address_id is not None:
        customer_obj.address_id = address_id
    if active is not None:
        customer_obj.active = active
    
    customer_obj.last_update = datetime.now()
    
    try:
        session.commit()
        return get_customer_details(customer_id)
    except Exception as e:
        session.rollback()
        return {"error": f"Failed to update customer: {str(e)}"}, 500

''' Delete customer '''
def delete_customer(customer_id: int):
    session = get_session()
    customer, rental = models["customer"], models["rental"]
    
    customer_obj = session.get(customer, customer_id)
    if not customer_obj:
        return {"error": "Customer not found"}, 404
    
    # Check if customer has active rentals
    active_rentals = (
        session.query(rental)
        .filter(rental.customer_id == customer_id, rental.return_date.is_(None))
        .count()
    )
    
    if active_rentals > 0:
        return {"error": f"Cannot delete customer with {active_rentals} active rentals"}, 400
    
    try:
        session.delete(customer_obj)
        session.commit()
        return {"message": "Customer deleted successfully"}, 200
    except Exception as e:
        session.rollback()
        return {"error": f"Failed to delete customer: {str(e)}"}, 500

''' Get customer rental history '''
def get_customer_rental_history(customer_id: int):
    session = get_session()
    customer, rental, inventory, film = models["customer"], models["rental"], models["inventory"], models["film"]
    
    # Check if customer exists
    customer_obj = session.get(customer, customer_id)
    if not customer_obj:
        return {"error": "Customer not found"}, 404
    
    # Get all rentals for this customer
    rentals = (
        session.query(rental, film)
        .join(inventory, inventory.inventory_id == rental.inventory_id)
        .join(film, film.film_id == inventory.film_id)
        .filter(rental.customer_id == customer_id)
        .order_by(rental.rental_date.desc())
        .all()
    )
    
    rentals_list = [{
        "rental_id": r.rental_id,
        "film_id": f.film_id,
        "film_title": f.title,
        "rental_date": r.rental_date.isoformat(),
        "return_date": r.return_date.isoformat() if r.return_date else None,
        "rental_rate": float(f.rental_rate),
        "is_returned": r.return_date is not None,
        "inventory_id": r.inventory_id
    } for r, f in rentals]
    
    # Separate active and past rentals
    active_rentals = [r for r in rentals_list if not r["is_returned"]]
    past_rentals = [r for r in rentals_list if r["is_returned"]]
    
    # Get full customer details
    customer_details = get_customer_details(customer_id)
    if not customer_details:
        return {"error": "Customer not found"}, 404
    
    return {
        "customer": customer_details,
        "active_rentals": active_rentals,
        "past_rentals": past_rentals,
        "total_rentals": len(rentals_list),
        "active_count": len(active_rentals),
        "past_count": len(past_rentals)
    }

''' Return a customer's rental (mark as returned) '''
def return_customer_rental(rental_id: int):
    session = get_session()
    rental = models["rental"]
    
    # Find the rental record
    rental_obj = session.get(rental, rental_id)
    if not rental_obj:
        return {"error": "Rental not found"}, 404
    
    # Check if already returned
    if rental_obj.return_date is not None:
        return {"error": "Film has already been returned"}, 400
    
    # Update return date
    return_date = datetime.now()
    rental_obj.return_date = return_date
    rental_obj.last_update = return_date
    
    try:
        session.commit()
        return {
            "rental_id": rental_id,
            "customer_id": rental_obj.customer_id,
            "return_date": return_date.isoformat(),
            "message": "Film returned successfully"
        }, 200
    except Exception as e:
        session.rollback()
        return {"error": f"Failed to return rental: {str(e)}"}, 500
