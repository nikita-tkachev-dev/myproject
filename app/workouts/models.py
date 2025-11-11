from app.extensions import db
from datetime import date


class WorkoutSession(db.Model):
    __tablename__ = "workout_sessions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    workout_plan_id = db.Column(
        db.Integer, db.ForeignKey("workout_plans.id"), nullable=True
    )
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, default=date.today, nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    user = db.relationship("User", back_populates="workout_sessions")
    workout_plan = db.relationship("WorkoutPlan", back_populates="sessions")
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
    order_in_workout = db.Column(db.Integer, nullable=False)
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
    set_number = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float)
    reps = db.Column(db.Integer)
    duration_seconds = db.Column(db.Integer)
    distance_meters = db.Column(db.Float)
    rest_seconds = db.Column(db.Integer)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    rpe = db.Column(db.Integer)
    notes = db.Column(db.Text)
    is_warmup = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    workout_exercise = db.relationship("WorkoutExercise", back_populates="sets")

    __table_args__ = (
        db.Index("idx_exercise_set_workout_exercise", "workout_exercise_id"),
    )


class WorkoutPlan(db.Model):
    """User's personal workout plan"""

    __tablename__ = "workout_plans"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(
        db.Enum("beginner", "intermediate", "advanced", name="plan_levels"),
        nullable=False,
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(
        db.DateTime, default=db.func.current_timestamp(), nullable=False
    )

    # Relationships
    user = db.relationship("User", back_populates="workout_plans")
    sessions = db.relationship(
        "WorkoutSession",
        back_populates="workout_plan",
        cascade="all, delete-orphan",
    )
    plan_days = db.relationship(
        "WorkoutPlanDay",
        back_populates="workout_plan",
        cascade="all, delete-orphan",
        order_by="WorkoutPlanDay.day_number",
    )

    __table_args__ = (db.Index("idx_workout_plan_user", "user_id"),)


class WorkoutPlanDay(db.Model):
    """Represents a single training day in user's plan (e.g. Monday workout, Wednesday workout)"""

    __tablename__ = "workout_plan_days"

    id = db.Column(db.Integer, primary_key=True)
    workout_plan_id = db.Column(
        db.Integer, db.ForeignKey("workout_plans.id"), nullable=False
    )
    day_number = db.Column(
        db.Integer, nullable=False
    )  # 1, 2, 3 (Monday, Wednesday, Friday)
    name = db.Column(
        db.String(100), nullable=False
    )  # e.g. "Training #1", "Training #2"
    is_optional = db.Column(db.Boolean, default=False, nullable=False)

    # Relationships
    workout_plan = db.relationship("WorkoutPlan", back_populates="plan_days")
    exercises = db.relationship(
        "WorkoutPlanExercise",
        back_populates="plan_day",
        cascade="all, delete-orphan",
        order_by="WorkoutPlanExercise.order_in_workout",
    )


class WorkoutPlanExercise(db.Model):
    """Exercise within a specific day of user's plan"""

    __tablename__ = "workout_plan_exercises"

    id = db.Column(db.Integer, primary_key=True)
    plan_day_id = db.Column(
        db.Integer, db.ForeignKey("workout_plan_days.id"), nullable=False
    )
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    order_in_workout = db.Column(db.Integer, nullable=False)
    target_sets = db.Column(db.Integer, nullable=False)
    target_reps_min = db.Column(db.Integer, nullable=False)
    target_reps_max = db.Column(db.Integer, nullable=False)
    warmup_sets = db.Column(db.Integer, default=1, nullable=False)

    # Relationships
    plan_day = db.relationship("WorkoutPlanDay", back_populates="exercises")
    exercise = db.relationship("Exercise")


class WorkoutTemplate(db.Model):
    """System templates for different levels"""

    __tablename__ = "workout_templates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    level = db.Column(
        db.Enum("beginner", "intermediate", "advanced", name="template_levels"),
        nullable=False,
    )
    day_number = db.Column(db.Integer, nullable=False)  # 1, 2, 3
    is_optional = db.Column(db.Boolean, default=False, nullable=False)
    description = db.Column(db.Text)

    # Relationships
    template_exercises = db.relationship(
        "TemplateExercise",
        back_populates="template",
        cascade="all, delete-orphan",
    )


class TemplateExercise(db.Model):
    """Exercise slots in system templates"""

    __tablename__ = "template_exercises"

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(
        db.Integer, db.ForeignKey("workout_templates.id"), nullable=False
    )
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    muscle_group = db.Column(
        db.Enum(
            "legs",
            "back",
            "chest",
            "core",
            "calves",
            "arms",
            "shoulders",
            name="template_muscle_groups",
        ),
        nullable=False,
    )
    exercise_number = db.Column(
        db.Integer, nullable=False
    )  # 1 or 2 (for legs #1, legs #2)
    order_in_workout = db.Column(db.Integer, nullable=False)
    target_sets = db.Column(db.Integer, nullable=False)
    target_reps_min = db.Column(db.Integer, nullable=False)
    target_reps_max = db.Column(db.Integer, nullable=False)
    warmup_sets = db.Column(db.Integer, default=1, nullable=False)

    # Relationships
    template = db.relationship("WorkoutTemplate", back_populates="template_exercises")
    exercise = db.relationship("Exercise", back_populates="template_exercises")
