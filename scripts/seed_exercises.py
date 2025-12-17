"""
Seed script to populate the exercises database with basic exercises.
Run this from your Flask shell or as a management command.

Usage:
    flask shell
    >>> from seed_exercises import seed_all_exercises
    >>> seed_all_exercises()
"""

from app import create_app
from app.extensions import db
from app.exercises.models import Exercise


def seed_all_exercises():
    """Seed all exercises into the database"""
    app = create_app()

    with app.app_context():
        # Check if exercises already exist
        if Exercise.query.count() > 0:
            print("⚠️  Exercises already exist. Skipping seed.")
            return

        exercises_data = [
            # ============ LEGS ============
            {
                "name": "Barbell Squats",
                "muscle_group": "legs",
                "equipment": "barbell",
                "difficulty": "intermediate",
                "description": "Classic compound exercise for legs and core",
            },
            {
                "name": "Goblet Squats",
                "muscle_group": "legs",
                "equipment": "dumbbell",
                "difficulty": "beginner",
                "description": "Beginner-friendly squat variation with a dumbbell",
            },
            {
                "name": "Romanian Deadlift",
                "muscle_group": "legs",
                "equipment": "barbell",
                "difficulty": "intermediate",
                "description": "Hamstring and glute focused deadlift variation",
            },
            {
                "name": "Leg Press",
                "muscle_group": "legs",
                "equipment": "machine",
                "difficulty": "beginner",
                "description": "Machine-based leg exercise for quads and glutes",
            },
            {
                "name": "Bulgarian Split Squats",
                "muscle_group": "legs",
                "equipment": "dumbbell",
                "difficulty": "intermediate",
                "description": "Single-leg exercise for balance and strength",
            },
            {
                "name": "Walking Lunges",
                "muscle_group": "legs",
                "equipment": "dumbbell",
                "difficulty": "beginner",
                "description": "Dynamic leg exercise for quads and glutes",
            },
            # ============ BACK ============
            {
                "name": "Pull-ups",
                "muscle_group": "back",
                "equipment": "bodyweight",
                "difficulty": "intermediate",
                "description": "Bodyweight exercise for lats and biceps",
            },
            {
                "name": "Bent Over Barbell Rows",
                "muscle_group": "back",
                "equipment": "barbell",
                "difficulty": "intermediate",
                "description": "Compound back exercise for thickness",
            },
            {
                "name": "Lat Pulldown",
                "muscle_group": "back",
                "equipment": "machine",
                "difficulty": "beginner",
                "description": "Machine exercise for lat development",
            },
            {
                "name": "Dumbbell Rows",
                "muscle_group": "back",
                "equipment": "dumbbell",
                "difficulty": "beginner",
                "description": "Unilateral back exercise for balance",
            },
            {
                "name": "Seated Cable Rows",
                "muscle_group": "back",
                "equipment": "machine",
                "difficulty": "beginner",
                "description": "Cable exercise for mid-back development",
            },
            {
                "name": "Face Pulls",
                "muscle_group": "back",
                "equipment": "machine",
                "difficulty": "beginner",
                "description": "Cable exercise for rear delts and upper back",
            },
            # ============ CHEST ============
            {
                "name": "Barbell Bench Press",
                "muscle_group": "chest",
                "equipment": "barbell",
                "difficulty": "intermediate",
                "description": "Classic chest compound exercise",
            },
            {
                "name": "Push-ups",
                "muscle_group": "chest",
                "equipment": "bodyweight",
                "difficulty": "beginner",
                "description": "Bodyweight chest exercise",
            },
            {
                "name": "Dumbbell Bench Press",
                "muscle_group": "chest",
                "equipment": "dumbbell",
                "difficulty": "beginner",
                "description": "Chest press with dumbbells for better range of motion",
            },
            {
                "name": "Incline Dumbbell Press",
                "muscle_group": "chest",
                "equipment": "dumbbell",
                "difficulty": "intermediate",
                "description": "Upper chest focused pressing movement",
            },
            {
                "name": "Cable Chest Flyes",
                "muscle_group": "chest",
                "equipment": "machine",
                "difficulty": "intermediate",
                "description": "Isolation exercise for chest stretch",
            },
            {
                "name": "Dips",
                "muscle_group": "chest",
                "equipment": "bodyweight",
                "difficulty": "intermediate",
                "description": "Bodyweight exercise for lower chest and triceps",
            },
            # ============ CORE ============
            {
                "name": "Plank",
                "muscle_group": "core",
                "equipment": "bodyweight",
                "difficulty": "beginner",
                "description": "Isometric core exercise",
            },
            {
                "name": "Russian Twists",
                "muscle_group": "core",
                "equipment": "dumbbell",
                "difficulty": "beginner",
                "description": "Rotational core exercise for obliques",
            },
            {
                "name": "Ab Wheel Rollouts",
                "muscle_group": "core",
                "equipment": "bodyweight",
                "difficulty": "advanced",
                "description": "Advanced core exercise with ab wheel",
            },
            {
                "name": "Hanging Leg Raises",
                "muscle_group": "core",
                "equipment": "bodyweight",
                "difficulty": "intermediate",
                "description": "Hanging exercise for lower abs",
            },
            {
                "name": "Cable Crunches",
                "muscle_group": "core",
                "equipment": "machine",
                "difficulty": "beginner",
                "description": "Cable machine exercise for abs",
            },
            {
                "name": "Dead Bug",
                "muscle_group": "core",
                "equipment": "bodyweight",
                "difficulty": "beginner",
                "description": "Core stability exercise",
            },
            # ============ SHOULDERS ============
            {
                "name": "Overhead Press",
                "muscle_group": "shoulders",
                "equipment": "barbell",
                "difficulty": "intermediate",
                "description": "Compound shoulder press movement",
            },
            {
                "name": "Dumbbell Shoulder Press",
                "muscle_group": "shoulders",
                "equipment": "dumbbell",
                "difficulty": "beginner",
                "description": "Shoulder press with dumbbells",
            },
            {
                "name": "Lateral Raises",
                "muscle_group": "shoulders",
                "equipment": "dumbbell",
                "difficulty": "beginner",
                "description": "Isolation for side delts",
            },
            {
                "name": "Front Raises",
                "muscle_group": "shoulders",
                "equipment": "dumbbell",
                "difficulty": "beginner",
                "description": "Isolation for front delts",
            },
            # ============ ARMS ============
            {
                "name": "Barbell Curls",
                "muscle_group": "arms",
                "equipment": "barbell",
                "difficulty": "beginner",
                "description": "Classic bicep exercise",
            },
            {
                "name": "Tricep Dips",
                "muscle_group": "arms",
                "equipment": "bodyweight",
                "difficulty": "intermediate",
                "description": "Bodyweight tricep exercise",
            },
            {
                "name": "Dumbbell Hammer Curls",
                "muscle_group": "arms",
                "equipment": "dumbbell",
                "difficulty": "beginner",
                "description": "Bicep curl variation for brachialis",
            },
            {
                "name": "Overhead Tricep Extension",
                "muscle_group": "arms",
                "equipment": "dumbbell",
                "difficulty": "beginner",
                "description": "Isolation exercise for triceps",
            },
        ]

        # Create Exercise objects
        exercises = []
        for ex_data in exercises_data:
            exercise = Exercise(
                name=ex_data["name"],
                muscle_group=ex_data["muscle_group"],
                equipment=ex_data["equipment"],
                difficulty=ex_data["difficulty"],
                description=ex_data.get("description", ""),
                is_active=True,
            )
            exercises.append(exercise)

        # Bulk insert
        try:
            db.session.bulk_save_objects(exercises)
            db.session.commit()
            print(f"✅ Successfully seeded {len(exercises)} exercises!")

            # Print summary
            print("\n📊 Summary by muscle group:")
            for group in ["legs", "back", "chest", "core", "shoulders", "arms"]:
                count = sum(1 for ex in exercises_data if ex["muscle_group"] == group)
                print(f"   {group.capitalize()}: {count} exercises")

        except Exception as e:
            db.session.rollback()
            print(f"❌ Error seeding exercises: {str(e)}")


if __name__ == "__main__":
    seed_all_exercises()
