from flask import Blueprint, jsonify
from ..services import film_service

bp = Blueprint("films", __name__)

'''
    GET /api/films/top5
    Returns top 5 rented films of all time.
'''
@bp.get("/top5")
def top_films():
    return jsonify(film_service.top_5_rented_films())

'''
    GET /api/films/<film_id>
    Returns details for a single film.
'''
@bp.get("/<int:film_id>")
def film_detail(film_id: int):
    film = film_service.film_detail(film_id)
    if not film:
        return {"error": "Film not found"}, 404
    return jsonify(film)



