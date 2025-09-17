from app.extensions import db


class Exercise(db.Model):
    __tablename__ = 'exercises'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)
    description = db.Column(db.Text)
    muscle_group = db.Column(
        db.Enum('chest', 'back', 'shoulders', 'arms', 'legs', 'core',
                                     'cardio', name='muscle_groups'),
        nullable=False
    )
    equipment = db.Column(
        db.Enum('bodyweight', 'dumbbell', 'barbell', 'machine',
                                  'resistance_band', 'kettlebell', name='equipment_types')
    )
    difficulty = db.Column(
        db.Enum('beginner', 'intermediate', 'advanced',
                                   name='difficulty_levels'),
        nullable=False
    )
    video_url = db.Column(db.String(500))
    instructions = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    # Связи
    workout_exercises = db.relationship("WorkoutExercise", back_populates="exercise")