from flask import Blueprint, request, jsonify
from app.extensions import db
from .models import Exercise

exercise_routes = Blueprint("exercises", __name__, url_prefix="/exercises")

@exercise_routes.route("/create", methods=["POST"])
def create_exercise():
    data = request.get_json()

    # Проверка обязательных полей
    required_fields = ["name", "muscle_group", "difficulty"]
    if not data or not all(field in data for field in required_fields):
        return jsonify({"error": f"Missing required fields: {', '.join(required_fields)}"}), 400

    # Проверка уникальности
    if Exercise.query.filter_by(name=data["name"]).first():
        return jsonify({"error": "Exercise with this name already exists"}), 400

    # Создание упражнения
    exercise = Exercise(
        name=data["name"],
        description=data.get("description"),
        muscle_group=data["muscle_group"],
        equipment=data.get("equipment"),
        difficulty=data["difficulty"],
        video_url=data.get("video_url"),
        instructions=data.get("instructions"),
        is_active=data.get("is_active", True)
    )

    try:
        db.session.add(exercise)
        db.session.commit()
        return jsonify({"message": f"Exercise {exercise.name} created!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@exercise_routes.route("/all", methods=["GET"])
def get_exercises():
    exercises = Exercise.query.all()
    return jsonify([
        {
            "id": e.id,
            "name": e.name,
            "description": e.description,
            "muscle_group": e.muscle_group.value if e.muscle_group else None,
            "equipment": e.equipment.value if e.equipment else None,
            "difficulty": e.difficulty.value if e.difficulty else None,
            "video_url": e.video_url,
            "instructions": e.instructions,
            "is_active": e.is_active
        } for e in exercises
    ])
