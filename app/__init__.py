from flask import Flask

from .routes import user_routes
from .extensions import db
from .config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    app.register_blueprint(user_routes)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app