from flask import Flask
from flask_cors import CORS
from .db import init_db
from .config import DevelopmentConfig # CHANGE to ProductionConfig when deploying
from .routes import films, actors, rentals, auth, customers

def create_app(config_class=DevelopmentConfig):
    # Create Flask application instance
    app = Flask(__name__)

    # Prevent loading default config values and load from config class instead
    app.config.from_object(config_class)

    # Enable CORS
    CORS(app, origins=app.config["CORS_ORIGINS"], supports_credentials=True) 
    
    # Initialize database
    init_db(app) 

    # Register blueprints
    app.register_blueprint(films.bp, url_prefix="/api/films")
    app.register_blueprint(actors.bp, url_prefix="/api/actors")
    app.register_blueprint(rentals.bp, url_prefix="/api/rentals")
    app.register_blueprint(auth.bp, url_prefix="/api/auth")
    app.register_blueprint(customers.bp, url_prefix="/api/customers")

    # Health check
    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    return app 
