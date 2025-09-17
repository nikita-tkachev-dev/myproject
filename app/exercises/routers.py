from flask import Blueprint, request, jsonify
from app.extensions import db
from .models import Exercise

exercise_routes = Blueprint("exercises", __name__, url_prefix="/exercises")

@exercise_routes.route("/create", methods=["POST"])
def create_exercise():
    data = request.get_json()
    exercise = Exercise(
        name=data["name"],
        description=data["description"],
        muscle_group=data["muscle_group"],
        equipment=data["equipment"],
        difficulty=data["difficulty"],
        video_url=data["video_url"]
    )

    db.session.add(exercise)
    db.session.commit()
    return jsonify({"message": f"Exercise {exercise.name} created!"})

@exercise_routes.route("/all", methods=["GET"])
def get_exercises():
    exercises = Exercise.query.all()
    return jsonify([{"id": e.id,
                     "name": e.name,
                     "description": e.description,
                     "muscle_group": e.muscle_group,
                     "equipment": e.equipment,
                     "difficulty": e.difficulty} for e in exercises]
    )