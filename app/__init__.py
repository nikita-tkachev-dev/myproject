from flask import Flask, render_template
from flask_migrate import Migrate
from .extensions import db
from .config import Config

from .exercises.routers import exercise_routes
from .users.routers import user_routes
from .workouts.routers import workout_routes
from .nutritionlogs.routers import nutrition_routes


def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)
    app.secret_key = app.config.get("SECRET_KEY", "dev-secret-key-change-in-production")

    db.init_app(app)
    migrate = Migrate(app, db)

    # API Blueprints
    app.register_blueprint(exercise_routes)
    app.register_blueprint(user_routes)
    app.register_blueprint(workout_routes)
    app.register_blueprint(nutrition_routes)

    from .cli import init_cli

    init_cli(app)

    @app.route("/")
    def index():
        return render_template("index.html")

    return app
