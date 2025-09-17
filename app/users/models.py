from app.extensions import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # хранить хэш!
    level = db.Column(db.String(20))  # 'beginner', 'intermediate', 'advanced'
    created_at = db.Column(db.DateTime, default=db.func.now())

    workouts = db.relationship("Workout", back_populates="user", cascade="all, delete-orphan")
    goals = db.relationship("Goal", back_populates="user", cascade="all, delete-orphan")
    nutrition_logs = db.relationship("NutritionLog", back_populates="user", cascade="all, delete-orphan")