from flask import Blueprint, request, jsonify
from app.extensions import db
from .models import User

user_routes = Blueprint("users", __name__, url_prefix="/users")

@user_routes.route("/create", methods=["POST"])
def create_user():
    data = request.get_json()
    user = User(username=data["username"],
                email=data["email"],
                password=data["password"],
                level=data["level"]
    )

    db.session.add(user)
    db.session.commit()
    return jsonify({"message": f"User {user.username} created!"})

@user_routes.route("/all", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([{"id": u.id,
                     "username": u.username,
                     "email": u.email,
                     "level": u.level} for u in users]
    )
