from flask import Blueprint, request, jsonify
from app.extensions import db
from .models import User

user_routes = Blueprint("users", __name__, url_prefix="/users")

@user_routes.route("/create", methods=["POST"])
def create_user():
    data = request.get_json()

    # Берём данные из запроса
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    # Создаём объект User
    user = User(username=username, password=password, email=email)

    # Сохраняем в БД
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": f"User {user.username} created!"})
