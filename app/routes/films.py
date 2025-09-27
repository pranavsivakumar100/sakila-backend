from flask import Blueprint, jsonify, request
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

'''
    GET /api/films/search/title?q=<search_term>
    Search films by title.
'''
@bp.get("/search/title")
def search_films_by_title():
    search_term = request.args.get('q', '')
    if not search_term:
        return {"error": "Search term is required"}, 400
    results = film_service.search_films_by_title(search_term)
    return jsonify(results)
    
'''
    GET /api/films/search/actor?q=<search_term>
    Search films by actor name.
'''
@bp.get("/search/actor")
def search_films_by_actor():
    search_term = request.args.get('q', '')
    if not search_term:
        return {"error": "Search term is required"}, 400
    results = film_service.search_films_by_actor(search_term)
    return jsonify(results)

'''
    GET /api/films/search/genre?q=<search_term>
    Search films by genre.
'''
@bp.get("/search/genre")
def search_films_by_genre():
    search_term = request.args.get('q', '')
    if not search_term:
        return {"error": "Search term is required"}, 400
    results = film_service.search_films_by_genre(search_term)
    return jsonify(results)