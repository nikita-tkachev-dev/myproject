from app.extensions import db


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    muscle_group = db.Column(
        db.Enum(
            "chest",
            "back",
            "shoulders",
            "arms",
            "legs",
            "core",
            "cardio",
            name="muscle_groups",
        ),
        nullable=False,
    )
    equipment = db.Column(
        db.Enum(
            "bodyweight",
            "dumbbell",
            "barbell",
            "machine",
            "resistance_band",
            "kettlebell",
            name="equipment_types",
        )
    )
    difficulty = db.Column(
        db.Enum("beginner", "intermediate", "advanced", name="difficulty_levels"),
        nullable=False,
    )
    video_url = db.Column(db.String(500))
    instructions = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    workout_exercises = db.relationship("WorkoutExercise", back_populates="exercise")
    exercise_logs = db.relationship("ExerciseLog", back_populates="exercise")
    statistics = db.relationship("ExerciseStatistic", back_populates="exercise")
    template_exercises = db.relationship("TemplateExercise", back_populates="exercise")


class ExerciseLog(db.Model):
    __tablename__ = "exercise_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    date = db.Column(db.Date, nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    is_warmup = db.Column(db.Boolean, default=False)
    reps = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float)  # in kg

    user = db.relationship("User", back_populates="exercise_logs")
    exercise = db.relationship("Exercise", back_populates="exercise_logs")


class ExerciseStatistic(db.Model):
    __tablename__ = "exercise_statistics"

    id = db.Column(db.Integer, primary_key=True)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    total_performed = db.Column(db.Integer, default=0, nullable=False)
    total_weight_lifted = db.Column(db.Float, default=0.0, nullable=False)  # in kg
    last_performed = db.Column(db.Date)
    is_warmup = db.Column(db.Boolean, default=False, nullable=False)
    exercise = db.relationship("Exercise", back_populates="statistics")
