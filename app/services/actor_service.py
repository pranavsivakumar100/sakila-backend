from sqlalchemy import func
from ..db import get_session, models

''' Return basic actor info '''
def actor_detail(actor_id: int):
    session = get_session()
    actor = models["actor"]
    a = session.get(actor, actor_id)
    if not a:
        return None
    return {"actor_id": a.actor_id, "first_name": a.first_name, "last_name": a.last_name}


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
