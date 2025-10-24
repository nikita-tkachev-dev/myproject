from app.extensions import db
from datetime import date


class WorkoutSession(db.Model):
    __tablename__ = "workout_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # e.g. "Chest & Triceps", "Cardio"
    date = db.Column(db.Date, default=date.today, nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    user = db.relationship("User", back_populates="workout_sessions")
    exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout_session",
        cascade="all, delete-orphan",
    )

    __table_args__ = (db.Index("idx_workout_session_user_date", "user_id", "date"),)


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)
    workout_session_id = db.Column(
        db.Integer, db.ForeignKey("workout_sessions.id"), nullable=False
    )
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)

    # Exercise performance data
    order_in_workout = db.Column(db.Integer, nullable=False)  # Order within the workout
    target_sets = db.Column(db.Integer, nullable=False, default=1)
    notes = db.Column(db.Text)

    # Relationships
    workout_session = db.relationship("WorkoutSession", back_populates="exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")
    sets = db.relationship(
        "ExerciseSet", back_populates="workout_exercise", cascade="all, delete-orphan"
    )

    __table_args__ = (db.Index("idx_workout_exercise_session", "workout_session_id"),)


class ExerciseSet(db.Model):
    __tablename__ = "exercise_sets"

    id = db.Column(db.Integer, primary_key=True)
    workout_exercise_id = db.Column(
        db.Integer, db.ForeignKey("workout_exercises.id"), nullable=False
    )
    set_number = db.Column(db.Integer, nullable=False)  # Set number (1, 2, 3...)

    # Set data
    weight = db.Column(db.Float)  # Weight in kg
    reps = db.Column(db.Integer)  # Number of repetitions
    duration_seconds = db.Column(db.Integer)  # For timed exercises (e.g. plank)
    distance_meters = db.Column(db.Float)  # For cardio (meters)
    rest_seconds = db.Column(db.Integer)  # Rest time after the set (seconds)

    # Metadata
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    rpe = db.Column(db.Integer)  # Rate of Perceived Exertion (1-10)
    notes = db.Column(db.Text)

    # Relationships
    workout_exercise = db.relationship("WorkoutExercise", back_populates="sets")

    __table_args__ = (
        db.Index("idx_exercise_set_workout_exercise", "workout_exercise_id"),
    )
