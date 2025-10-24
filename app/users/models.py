from app.extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(200), nullable=False)  # FIXED: password hash
    level = db.Column(
        db.Enum("beginner", "intermediate", "advanced", name="user_levels"),
        default="beginner",
    )

    # Personal data
    birth_date = db.Column(db.Date, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)
    gender = db.Column(
        db.Enum("male", "female", "other", name="genders"), nullable=True
    )

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Relationships
    workout_sessions = db.relationship(
        "WorkoutSession", back_populates="user", cascade="all, delete-orphan"
    )
    goals = db.relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    nutrition_logs = db.relationship(
        "NutritionLog", back_populates="user", cascade="all, delete-orphan"
    )


class Goal(db.Model):
    __tablename__ = "goals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    goal_type = db.Column(
        db.Enum(
            "weight_loss",
            "muscle_gain",
            "strength",
            "endurance",
            "flexibility",
            name="goal_types",
        ),
        nullable=False,
    )
    target_value = db.Column(db.Float)  # Target value
    current_value = db.Column(db.Float, default=0)  # Current value
    unit = db.Column(db.String(20))  # e.g. kg, km, minutes, etc.
    target_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = db.relationship("User", back_populates="goals")
