from app.extensions import db

class Workout(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercise.id"), nullable=False)

    weight = db.Column(db.Float)  # рабочий вес
    reps = db.Column(db.Integer)  # количество повторений
    sets = db.Column(db.Integer)  # количество подходов
    date = db.Column(db.Date, default=db.func.current_date())

    user = db.relationship("User", back_populates="workouts")
    exercise = db.relationship("Exercise", back_populates="workouts")