from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base

# Connects to DB, gives you a session
db = SQLAlchemy()

# Stores all the Sakila tables as classes
Base = automap_base()

# Storing Base.classes into models dict- keys represent table names and values are python ORM classes
models = {}

def init_db(app):
    db.init_app(app)
    with app.app_context():
        Base.prepare(db.engine, reflect=True)
        models.update(Base.classes)

def get_session():
    return db.session