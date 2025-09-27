from ..db import get_session, models
from sqlalchemy import func

''' Return top 5 rented films of all time '''
def top_5_rented_films():
    session = get_session()
    film, inventory, rental = models["film"], models["inventory"], models["rental"]

    q = (
        session.query(
            film.film_id.label("film_id"),
            film.title.label("title"),
            func.count(rental.rental_id).label("rentals")
        )
        .join(inventory, inventory.film_id == film.film_id)
        .join(rental, rental.inventory_id == inventory.inventory_id)
        .group_by(film.film_id, film.title)
        .order_by(func.count(rental.rental_id).desc())
        .limit(5)
    ).all()

    return [{"film_id": fid, "title": title, "rentals": int(count)} for fid, title, count in q] 

''' Return details for a single film '''
def film_detail(film_id: int):
    session = get_session()
    film = models["film"]
    f = session.get(film, film_id)
    if not f: 
        return None; 
    return {
        "film_id": f.film_id,
        "title": f.title,
        "description": f.description,
        "release_year": f.release_year,
        "length": f.length,
        "rating": f.rating,
        "rental_rate": float(f.rental_rate),
    }
