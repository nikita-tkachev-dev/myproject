from flask import Blueprint, request, jsonify
from app.extensions import db
from .models import Workout

workout_routes = Blueprint('workout_router', __name__, url_prefix='/workouts')

@workout_routes.route("/create", methods=["POST"])
def create_workout():
    data = request.get_json()

    workout = Workout(name=data["name"], description=data["description"])
    db.session.add(workout)
    db.session.commit()
    return jsonify({"message": "Workout created!"})

@workout_routes.route("/all", methods=["GET"])
def get_workouts():
    workouts = Workout.query.all()
    return jsonify([{"id": w.id, "name": w.name, "description": w.description} for w in workouts])
