from sqlalchemy import func
from ..db import get_session, models

''' Return actor details '''
def actor_detail(actor_id: int):
    session = get_session()
    actor = models["actor"]
    a = session.get(actor, actor_id)
    if not a:
        return None
    return {
        "actor_id": a.actor_id, 
        "first_name": a.first_name, 
        "last_name": a.last_name,
        "last_update": a.last_update.isoformat() if a.last_update else None
    }


''' Return top 5 actors appearing in films '''
def top_5_actors():
    session = get_session()
    actor, film_actor, inventory = models["actor"], models["film_actor"], models["inventory"]
    q = (
        session.query(
            actor.actor_id,
            actor.first_name,
            actor.last_name,
            func.count(func.distinct(inventory.film_id)).label("films_in_store"),
        )
        .join(film_actor, film_actor.actor_id == actor.actor_id)
        .join(inventory, inventory.film_id == film_actor.film_id)
        .group_by(actor.actor_id, actor.first_name, actor.last_name)
        .order_by(func.count(func.distinct(inventory.film_id)).desc(),
                  actor.last_name.asc(), actor.first_name.asc())
        .limit(5)
    ).all()
    return [
        {"actor_id": aid, "first_name": f"{fn}", "last_name": f"{ln}", "films_in_store": int(n)}
        for aid, fn, ln, n in q
    ]

''' Return top 5 most-rented films for a given actor '''
def actor_top_5_rented_films(actor_id: int):
    session = get_session()
    film, film_actor, inventory, rental = models["film"], models["film_actor"], models["inventory"], models["rental"]
    q = (
        session.query(
            film.film_id,
            film.title,
            func.count(rental.rental_id).label("rentals"),
        )
        .join(film_actor, film_actor.film_id == film.film_id)
        .join(inventory, inventory.film_id == film.film_id)
        .join(rental, rental.inventory_id == inventory.inventory_id)
        .filter(film_actor.actor_id == actor_id)
        .group_by(film.film_id, film.title)
        .order_by(func.count(rental.rental_id).desc())
        .limit(5)
    ).all()
    return [{"film_id": fid, "title": title, "rentals": int(count)} for fid, title, count in q]