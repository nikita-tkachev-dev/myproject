from flask import Blueprint
from .extensions import db
from .models import User

user_routes = Blueprint('user_routes', __name__)

@user_routes.route('/user/<name>')
def create_user(name):
    user = User(name = name)
    db.session.add(user)
    db.session.commit()
    return f'User {name} created'