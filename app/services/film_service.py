from ..db import get_session, models
from sqlalchemy import func, or_, case

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
    film, film_actor, actor, film_category, category = models["film"], models["film_actor"], models["actor"], models["film_category"], models["category"]
    
    f = session.get(film, film_id)
    if not f: 
        return None
    
    # Get actors for this film
    actors_query = (
        session.query(actor)
        .join(film_actor, film_actor.actor_id == actor.actor_id)
        .filter(film_actor.film_id == film_id)
        .order_by(actor.first_name, actor.last_name)
    ).all()
    
    actors_list = [{
        "actor_id": a.actor_id,
        "first_name": a.first_name,
        "last_name": a.last_name,
        "full_name": f"{a.first_name} {a.last_name}"
    } for a in actors_query]
    
    # Get category for this film
    category_query = (
        session.query(category)
        .join(film_category, film_category.category_id == category.category_id)
        .filter(film_category.film_id == film_id)
    ).first()
    
    category_obj = {
        "category_id": category_query.category_id,
        "name": category_query.name
    } if category_query else None
    
    return {
        "film_id": f.film_id,
        "title": f.title,
        "description": f.description,
        "release_year": f.release_year,
        "language_id": f.language_id,
        "original_language_id": f.original_language_id,
        "rental_duration": f.rental_duration,
        "rental_rate": float(f.rental_rate),
        "length": f.length,
        "replacement_cost": float(f.replacement_cost),
        "rating": f.rating,
        "special_features": list(f.special_features) if f.special_features else [],
        "last_update": f.last_update.isoformat() if f.last_update else None,
        "actors": actors_list,
        "category": category_obj,
    }
    
''' Search films by film title '''
def search_films_by_title(search_term: str):
    session = get_session()
    film, film_text = models["film"], models["film_text"]
    
    # Create ranking based on match quality
    ranking = case(
        (film_text.title.ilike(search_term), 1),  # Exact match (case-insensitive)
        (film_text.title.ilike(f"{search_term}%"), 2),  # Starts with search term
        (film_text.title.ilike(f"%{search_term}"), 3),  # Ends with search term
        else_=4  # Contains search term anywhere
    )
    
    q = (
        session.query(film, ranking.label('rank'))
        .join(film_text, film.film_id == film_text.film_id)
        .filter(film_text.title.ilike(f"%{search_term}%"))
        .order_by(ranking, film_text.title)
    ).all()
    
    return [film_detail(f.film_id) for f, rank in q if film_detail(f.film_id) is not None]

''' Search films by actor name '''
def search_films_by_actor(search_term: str):
    session = get_session()
    film, film_actor, actor = models["film"], models["film_actor"], models["actor"]
    q = (
        session.query(film)
        .join(film_actor, film_actor.film_id == film.film_id)
        .join(actor, actor.actor_id == film_actor.actor_id)
        .filter(
            or_(
                actor.first_name.ilike(f"%{search_term}%"),
                actor.last_name.ilike(f"%{search_term}%"),
                func.concat(actor.first_name, ' ', actor.last_name).ilike(f"%{search_term}%")
            )
        ).distinct()
    ).all()
    return [film_detail(f.film_id) for f in q if film_detail(f.film_id) is not None]

''' Search films by genre '''
def search_films_by_genre(search_term: str):
    session = get_session()
    film, film_category, category = models["film"], models["film_category"], models["category"]
    q = (
        session.query(film)
        .join(film_category, film_category.film_id == film.film_id)
        .join(category, category.category_id == film_category.category_id)
        .filter(category.name.ilike(f"%{search_term}%"))
        .distinct()
    ).all()
    return [film_detail(f.film_id) for f in q if film_detail(f.film_id) is not None]
    