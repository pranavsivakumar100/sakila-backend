from ..db import get_session, models
from datetime import datetime, timedelta
from sqlalchemy import and_

''' Create a new rental for a customer '''
def create_rental(customer_id: int, film_id: int, staff_id: int):
    session = get_session()
    rental, inventory, customer, film = models["rental"], models["inventory"], models["customer"], models["film"]
    
    # Check if customer exists
    customer_obj = session.get(customer, customer_id)
    if not customer_obj:
        return {"error": "Customer not found"}, 404
    
    # Check if film exists
    film_obj = session.get(film, film_id)
    if not film_obj:
        return {"error": "Film not found"}, 404
    pass

    # Find available inventory for this film
    available_inventory = (
        session.query(inventory)
        .filter(inventory.film_id == film_id)
        .outerjoin(rental, and_(
            rental.inventory_id == inventory.inventory_id,
            rental.return_date.is_(None) 
        ))
        .filter(rental.rental_id.is_(None))  
        .first()
    )
    
    if not available_inventory:
        return {"error": "Film is not available for rental"}, 400
    
    # Calculate rental date and return date
    rental_date = datetime.now()
    return_date = rental_date + timedelta(days=film_obj.rental_duration)
    
    # Create new rental record
    new_rental = rental(
        rental_date=rental_date,
        inventory_id=available_inventory.inventory_id,
        customer_id=customer_id,
        staff_id=staff_id,
        last_update=rental_date
    )
    try:
        session.add(new_rental)
        session.commit()
        return get_rental_details(new_rental.rental_id)
    except Exception as e:
        session.rollback()
        return {"error": f"Failed to create rental: {str(e)}"}, 500

''' Get rental details '''
def get_rental_details(rental_id: int):
    session = get_session()
    rental, customer, inventory, film = models["rental"], models["customer"], models["inventory"], models["film"]
    
    rental_obj = (
        session.query(rental, customer, film)
        .join(customer, customer.customer_id == rental.customer_id)
        .join(inventory, inventory.inventory_id == rental.inventory_id)
        .join(film, film.film_id == inventory.film_id)
        .filter(rental.rental_id == rental_id)
        .first()
    )
    
    if not rental_obj:
        return {"error": "Rental not found"}, 404
    
    r, c, f = rental_obj
    
    # Calculate expected return date
    expected_return_date = r.rental_date + timedelta(days=f.rental_duration)
    
    return {
        "rental_id": r.rental_id,
        "customer_id": c.customer_id,
        "customer_name": f"{c.first_name} {c.last_name}",
        "film_id": f.film_id,
        "film_title": f.title,
        "rental_date": r.rental_date.isoformat(),
        "return_date": r.return_date.isoformat() if r.return_date else None,
        "expected_return_date": expected_return_date.isoformat(),
        "rental_rate": float(f.rental_rate),
        "rental_duration_days": f.rental_duration,
        "is_returned": r.return_date is not None,
        "inventory_id": r.inventory_id
    }, 201

''' Return a rented film '''
def return_rental(rental_id: int):
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
            "return_date": return_date.isoformat(),
            "message": "Film returned successfully"
        }, 200
    except Exception as e:
        session.rollback()
        return {"error": f"Failed to return rental: {str(e)}"}, 500