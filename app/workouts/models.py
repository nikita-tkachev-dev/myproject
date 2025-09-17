from app.extensions import db
from datetime import datetime, date, time

class WorkoutSession(db.Model):
    __tablename__ = 'workout_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)  # "Грудь и трицепс", "Кардио"
    date = db.Column(db.Date, default=date.today, nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    notes = db.Column(db.Text)
    is_completed = db.Column(db.Boolean, default=False, nullable=False)

    # Связи
    user = db.relationship("User", back_populates="workout_sessions")
    exercises = db.relationship("WorkoutExercise", back_populates="workout_session",
                                cascade="all, delete-orphan")

    __table_args__ = (
        db.Index('idx_workout_session_user_date', 'user_id', 'date'),
    )


class WorkoutExercise(db.Model):
    __tablename__ = 'workout_exercises'

    id = db.Column(db.Integer, primary_key=True)
    workout_session_id = db.Column(db.Integer, db.ForeignKey('workout_sessions.id'),
                                   nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey('exercises.id'), nullable=False)

    # Данные выполнения упражнения
    order_in_workout = db.Column(db.Integer, nullable=False)  # Порядок в тренировке
    target_sets = db.Column(db.Integer, nullable=False, default=1)
    notes = db.Column(db.Text)

    # Связи
    workout_session = db.relationship("WorkoutSession", back_populates="exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")
    sets = db.relationship("ExerciseSet", back_populates="workout_exercise",
                           cascade="all, delete-orphan")

    __table_args__ = (
        db.Index('idx_workout_exercise_session', 'workout_session_id'),
    )

class ExerciseSet(db.Model):
    __tablename__ = 'exercise_sets'

    id = db.Column(db.Integer, primary_key=True)
    workout_exercise_id = db.Column(db.Integer, db.ForeignKey('workout_exercises.id'),
                                    nullable=False)
    set_number = db.Column(db.Integer, nullable=False)  # Номер подхода (1, 2, 3...)

    # Данные подхода
    weight = db.Column(db.Float)  # Вес в кг
    reps = db.Column(db.Integer)  # Количество повторений
    duration_seconds = db.Column(db.Integer)  # Для упражнений на время (планка)
    distance_meters = db.Column(db.Float)  # Для кардио
    rest_seconds = db.Column(db.Integer)  # Время отдыха после подхода

    # Метаданные
    is_completed = db.Column(db.Boolean, default=False, nullable=False)
    rpe = db.Column(db.Integer)  # Rate of Perceived Exertion (1-10)
    notes = db.Column(db.Text)

    # Связи
    workout_exercise = db.relationship("WorkoutExercise", back_populates="sets")

    __table_args__ = (
        db.Index('idx_exercise_set_workout_exercise', 'workout_exercise_id'),
    )