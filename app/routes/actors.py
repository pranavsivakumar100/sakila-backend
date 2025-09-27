from flask import Blueprint, jsonify
from ..services import actor_service

bp = Blueprint("actors", __name__)

'''
    GET /api/actors/<actor_id>
    Returns actor details.
'''
@bp.get("/<int:actor_id>")
def get_actor(actor_id: int):
    data = actor_service.actor_detail(actor_id)
    if not data:
        return {"error": "Actor not found"}, 404
    return jsonify(data)

'''
    GET /api/actors/top5
    Returns top 5 actors appearing in films
'''
@bp.get("/top5")
def top_actors():
    return jsonify(actor_service.top_5_actors())

'''
    GET /api/actors/<actor_id>/top5films
    Returns top 5 most rented films for an actor
'''
@bp.get("/<int:actor_id>/top5films")
def actor_top_films(actor_id: int):
    return jsonify(actor_service.actor_top_5_rented_films(actor_id))