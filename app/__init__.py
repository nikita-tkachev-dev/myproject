from flask import Flask
from .extensions import db
from .config import Config

from .exercises.routers import exercise_routes
from .users.routers import user_routes
from .workouts.routers import workout_routes


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    db.init_app(app)

    app.register_blueprint(exercise_routes)
    app.register_blueprint(user_routes)
    app.register_blueprint(workout_routes)

    with app.app_context():
        db.create_all()

    return app
