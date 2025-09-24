from flask import Blueprint, request, jsonify
from app.extensions import db
from .models import User, Goal
from werkzeug.security import generate_password_hash
from datetime import datetime

user_routes = Blueprint("users", __name__, url_prefix="/users")

@user_routes.route("/create", methods=["POST"])
def create_user():
    data = request.get_json()

    # Проверка обязательных полей
    if not data or not all(k in data for k in ("username", "email", "password")):
        return jsonify({"error": "Missing required fields"}), 400

    # Проверка уникальности
    if User.query.filter((User.username == data["username"]) | (User.email == data["email"])).first():
        return jsonify({"error": "Username or email already exists"}), 400

    # Создаём пользователя
    user = User(
        username=data["username"],
        email=data["email"],
        level=data.get("level", "beginner"),
        birth_date = data.get("birth_date"),
        height=data.get("height"),
        weight=data.get("weight"),
        gender=data.get("gender")
    )
    user.password_hash = generate_password_hash(data["password"])

    try:
        db.session.add(user)
        db.session.flush()  # чтобы появился user.id

        # Создаём цели, если они есть
        for g in data.get("goals", []):
            current_value = g.get("current_value")
            if current_value is None and g["goal_type"] in ["weight_loss", "muscle_gain"]:
                current_value = user.weight

            goal = Goal(
                user_id=user.id,
                goal_type=g["goal_type"],
                target_value=g.get("target_value"),
                current_value=current_value,
                unit=g.get("unit"),
                target_date=datetime.strptime(g["target_date"], "%Y-%m-%d").date() if g.get("target_date") else None,
                is_active=g.get("is_active", True)
            )
            db.session.add(goal)

        db.session.commit()
        return jsonify({"message": f"User {user.username} created with {len(data.get('goals', []))} goals!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
