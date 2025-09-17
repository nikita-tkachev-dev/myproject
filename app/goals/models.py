from app.extensions import db

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    type = db.Column(db.String(50))  # 'weight_loss', 'muscle_gain', 'endurance'
    target_value = db.Column(db.Float)  # например -5 кг или +10 кг в жиме
    deadline = db.Column(db.Date)

    created_at = db.Column(db.DateTime, default=db.func.now())
    achieved = db.Column(db.Boolean, default=False)

    user = db.relationship("User", back_populates="goals")
