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


