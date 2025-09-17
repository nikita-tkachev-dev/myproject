from flask import Blueprint, request, jsonify
from app.extensions import db
from .models import Workout

workout_routes = Blueprint('workout_router', __name__, url_prefix='/workouts')

@workout_routes.route("/create", methods=["POST"])
def create_workout():
    data = request.get_json()

    workout = Workout(
        user_id=data["user_id"],
        exercise_id=data["exercise_id"],
        weight=data.get("weight"),
        reps=data.get("reps"),
        sets=data.get("sets")
    )

    db.session.add(workout)
    db.session.commit()
    return jsonify({"message": "Workout created!", "id": workout.id})

@workout_routes.route("/all", methods=["GET"])
def get_workouts():
    workouts = Workout.query.all()
    result = []
    for w in workouts:
        result.append({
            "id": w.id,
            "user_id": w.user_id,
            "exercise_id": w.exercise_id,
            "weight": w.weight,
            "reps": w.reps,
            "sets": w.sets,
            "date": w.date.isoformat()
        })
    return jsonify(result)