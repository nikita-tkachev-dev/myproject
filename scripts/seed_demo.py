#!/usr/bin/env python3
"""
Seed script for demo data.

Usage:
  source .venv/bin/activate
  export FLASK_APP=app
  flask db upgrade   # make sure migrations applied
  python scripts/seed_demo.py

This script requires the DB configured in app/config.py to be reachable.
"""
from app import create_app
from app.extensions import db
from app.users.models import User
from app.exercises.models import Exercise
from werkzeug.security import generate_password_hash


def seed():
    app = create_app()
    with app.app_context():
        # Note: migrations should be applied beforehand (flask db upgrade)
        # Create demo user 'd'
        if not User.query.filter_by(username="d").first():
            u = User(
                username="d",
                email="d@example.com",
                password_hash=generate_password_hash("password"),
                height=175,
                weight=70.0,
            )
            db.session.add(u)

        # Add a few exercises
        sample = [
            {
                "name": "Push-up",
                "muscle_group": "chest",
                "difficulty": "beginner",
                "equipment": "bodyweight",
            },
            {
                "name": "Squat",
                "muscle_group": "legs",
                "difficulty": "beginner",
                "equipment": "bodyweight",
            },
            {
                "name": "Dumbbell Row",
                "muscle_group": "back",
                "difficulty": "intermediate",
                "equipment": "dumbbell",
            },
        ]
        for ex in sample:
            if not Exercise.query.filter_by(name=ex["name"]).first():
                e = Exercise(
                    name=ex["name"],
                    description="",
                    muscle_group=ex["muscle_group"],
                    equipment=ex.get("equipment"),
                    difficulty=ex["difficulty"],
                    is_active=True,
                )
                db.session.add(e)

        db.session.commit()
        print("Seed data created: user 'd' and sample exercises")


if __name__ == "__main__":
    seed()
