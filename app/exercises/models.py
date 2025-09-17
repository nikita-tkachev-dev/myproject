from app.extensions import db

class Exercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.Text)
    muscle_group = db.Column(db.String(80)) #legs, chest, back
    equipment = db.Column(db.String(80)) #dumbbell, barbell, bodyweight
    difficulty = db.Column(db.String(80)) #begginer, intermediate, advance
    video_url = db.Column(db.String(200))

    workouts = db.relationship('Workout', back_populates="exercise")


