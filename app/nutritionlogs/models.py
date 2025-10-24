from app.extensions import db
from datetime import date


class NutritionLog(db.Model):
    __tablename__ = "nutritionlogs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    name = db.Column(db.String(100))  # e.g. creatine, protein, etc.
    amount = db.Column(db.String(50))  # "5g", "2 scoops"
    time = db.Column(db.Time, default=db.func.current_time())
    date = db.Column(db.Date, default=date.today, nullable=False)

    user = db.relationship("User", back_populates="nutrition_logs")
