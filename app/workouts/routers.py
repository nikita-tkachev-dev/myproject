from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    session,
    flash,
)
from app.extensions import db
from .models import WorkoutSession, WorkoutExercise, ExerciseSet
from datetime import datetime

workout_routes = Blueprint("workouts", __name__, url_prefix="/workouts")


@workout_routes.route("/")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("users.login"))

    workouts = WorkoutSession.query.filter_by(user_id=session["user_id"]).all()
    return render_template("dashboard.html", workouts=workouts)


@workout_routes.route("/create", methods=["POST"])
def create_workout():
    data = request.get_json()

    # Check required fields
    if not data or not all(k in data for k in ("user_id", "name", "exercises")):
        return (
            jsonify({"error": "Missing required fields: user_id, name, exercises"}),
            400,
        )

    # Create session
    session = WorkoutSession(
        user_id=data["user_id"],
        name=data["name"],
        date=(
            datetime.strptime(data["date"], "%Y-%m-%d").date()
            if data.get("date")
            else None
        ),
        start_time=(
            datetime.fromisoformat(data["start_time"])
            if data.get("start_time")
            else None
        ),
        end_time=(
            datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None
        ),
        notes=data.get("notes"),
        is_completed=data.get("is_completed", False),
    )

    try:
        db.session.add(session)
        db.session.flush()  # Ensure session.id is available

        # Add exercises
        for ex in data["exercises"]:
            workout_ex = WorkoutExercise(
                workout_session_id=session.id,
                exercise_id=ex["exercise_id"],
                order_in_workout=ex.get("order_in_workout", 1),
                target_sets=ex.get("target_sets", 1),
                notes=ex.get("notes"),
            )
            db.session.add(workout_ex)
            db.session.flush()  # Ensure workout_ex.id is available

            # Add sets
            for s in ex.get("sets", []):
                exercise_set = ExerciseSet(
                    workout_exercise_id=workout_ex.id,
                    set_number=s.get("set_number", 1),
                    weight=s.get("weight"),
                    reps=s.get("reps"),
                    duration_seconds=s.get("duration_seconds"),
                    distance_meters=s.get("distance_meters"),
                    rest_seconds=s.get("rest_seconds"),
                    is_completed=s.get("is_completed", False),
                    rpe=s.get("rpe"),
                    notes=s.get("notes"),
                )
                db.session.add(exercise_set)

        db.session.commit()
        return jsonify({"message": "Workout session created!", "id": session.id}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
