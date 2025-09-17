from app.extensions import db

class NutritionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    name = db.Column(db.String(100))  # креатин, протеин и т.д.
    amount = db.Column(db.String(50))  # "5g", "2 scoops"
    time = db.Column(db.Time, default=db.func.current_time())
    date = db.Column(db.Date, default=db.func.current_date())

    user = db.relationship("User", back_populates="nutrition_logs")
