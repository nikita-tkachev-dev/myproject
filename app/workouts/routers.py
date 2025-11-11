from flask import (
    Blueprint,
    request,
    jsonify,
    render_template,
    redirect,
    url_for,
    session,
    flash,
)
from app.extensions import db
from .models import (
    WorkoutSession,
    WorkoutExercise,
    ExerciseSet,
    WorkoutPlan,
    WorkoutPlanDay,
    WorkoutPlanExercise,
    WorkoutTemplate,
    TemplateExercise,
)
from app.exercises.models import Exercise
from datetime import datetime, date

workout_routes = Blueprint("workouts", __name__, url_prefix="/workouts")


# ------------------ CREATE PLAN FROM TEMPLATE ------------------
@workout_routes.route("/create-plan", methods=["GET", "POST"])
def create_plan():
    """Step-by-step plan creation based on user level"""
    if "user_id" not in session:
        flash("Please log in first", "error")
        return redirect(url_for("users.login"))

    from app.users.models import User

    user = User.query.get(session["user_id"])

    if not user or not user.level:
        flash("Please select your level first", "error")
        return redirect(url_for("users.select_level"))

    if request.method == "GET":
        # Load templates for user's level
        templates = (
            WorkoutTemplate.query.filter_by(level=user.level)
            .order_by(WorkoutTemplate.day_number)
            .all()
        )

        # Get all exercises grouped by muscle group
        exercises = (
            Exercise.query.filter_by(is_active=True)
            .order_by(Exercise.muscle_group, Exercise.name)
            .all()
        )

        exercises_by_group = {}
        for ex in exercises:
            group = ex.muscle_group
            if group not in exercises_by_group:
                exercises_by_group[group] = []
            exercises_by_group[group].append(ex)

        return render_template(
            "workouts/create_plan.html",
            user=user,
            templates=templates,
            exercises_by_group=exercises_by_group,
        )

    # POST: Save user's plan
    try:
        plan_name = request.form.get("plan_name", f"{user.username}'s Plan")

        # Create the main plan
        plan = WorkoutPlan(
            user_id=user.id,
            name=plan_name,
            level=user.level,
            is_active=True,
        )
        db.session.add(plan)
        db.session.flush()

        # Process each training day
        day_count = 3 if user.level == "intermediate" else 2  # beginner has 2 days

        for day_num in range(1, day_count + 1):
            day_name = request.form.get(f"day_{day_num}_name", f"Training #{day_num}")
            is_optional = (
                day_num == 3 and user.level == "intermediate"
            )  # Friday is optional

            plan_day = WorkoutPlanDay(
                workout_plan_id=plan.id,
                day_number=day_num,
                name=day_name,
                is_optional=is_optional,
            )
            db.session.add(plan_day)
            db.session.flush()

            # Get selected exercises for this day
            exercise_keys = [
                k
                for k in request.form.keys()
                if k.startswith(f"day_{day_num}_exercise_")
            ]

            for i, key in enumerate(sorted(exercise_keys), start=1):
                exercise_id = request.form.get(key)
                if not exercise_id:
                    continue

                # Get target sets and reps based on level
                if user.level == "beginner":
                    target_sets = 2
                    reps_min, reps_max = 12, 15
                    warmup_sets = 1
                else:  # intermediate
                    target_sets = 4
                    reps_min, reps_max = 8, 12
                    warmup_sets = 2

                # Special case for core and calves - always 3 sets
                exercise = Exercise.query.get(exercise_id)
                if exercise and exercise.muscle_group in ["core"]:
                    target_sets = 3

                plan_exercise = WorkoutPlanExercise(
                    plan_day_id=plan_day.id,
                    exercise_id=exercise_id,
                    order_in_workout=i,
                    target_sets=target_sets,
                    target_reps_min=reps_min,
                    target_reps_max=reps_max,
                    warmup_sets=warmup_sets,
                )
                db.session.add(plan_exercise)

        db.session.commit()
        flash("Your workout plan has been created!", "success")
        return redirect(url_for("users.dashboard"))

    except Exception as e:
        db.session.rollback()
        flash(f"Error creating plan: {str(e)}", "error")
        return redirect(url_for("workouts.create_plan"))


# ------------------ VIEW PLAN ------------------
@workout_routes.route("/plan/<int:plan_id>")
def view_plan(plan_id):
    """View user's workout plan"""
    if "user_id" not in session:
        return redirect(url_for("users.login"))

    plan = WorkoutPlan.query.get_or_404(plan_id)

    if plan.user_id != session["user_id"]:
        flash("Access denied", "error")
        return redirect(url_for("users.dashboard"))

    return render_template("workouts/view_plan.html", plan=plan)


# ------------------ EDIT PLAN ------------------
@workout_routes.route("/plan/<int:plan_id>/edit", methods=["GET", "POST"])
def edit_plan(plan_id):
    """Edit existing workout plan"""
    if "user_id" not in session:
        return redirect(url_for("users.login"))

    plan = WorkoutPlan.query.get_or_404(plan_id)

    if plan.user_id != session["user_id"]:
        flash("Access denied", "error")
        return redirect(url_for("users.dashboard"))

    if request.method == "GET":
        exercises = (
            Exercise.query.filter_by(is_active=True)
            .order_by(Exercise.muscle_group, Exercise.name)
            .all()
        )
        exercises_by_group = {}
        for ex in exercises:
            group = ex.muscle_group
            if group not in exercises_by_group:
                exercises_by_group[group] = []
            exercises_by_group[group].append(ex)

        return render_template(
            "workouts/edit_plan.html", plan=plan, exercises_by_group=exercises_by_group
        )

    # POST: Update plan
    try:
        plan.name = request.form.get("plan_name", plan.name)

        # Update each day's exercises (simplified - full implementation would handle additions/deletions)
        for day in plan.plan_days:
            for ex in day.exercises:
                new_exercise_id = request.form.get(f"exercise_{ex.id}")
                if new_exercise_id:
                    ex.exercise_id = new_exercise_id

        db.session.commit()
        flash("Plan updated successfully", "success")
        return redirect(url_for("workouts.view_plan", plan_id=plan.id))

    except Exception as e:
        db.session.rollback()
        flash(f"Error updating plan: {str(e)}", "error")
        return redirect(url_for("workouts.edit_plan", plan_id=plan_id))


# ------------------ START WORKOUT ------------------
@workout_routes.route("/start/<int:plan_day_id>", methods=["POST"])
def start_workout(plan_day_id):
    """Start a new workout session from a plan day"""
    if "user_id" not in session:
        return redirect(url_for("users.login"))

    plan_day = WorkoutPlanDay.query.get_or_404(plan_day_id)

    if plan_day.workout_plan.user_id != session["user_id"]:
        flash("Access denied", "error")
        return redirect(url_for("users.dashboard"))

    # Create new workout session
    workout_session = WorkoutSession(
        user_id=session["user_id"],
        workout_plan_id=plan_day.workout_plan_id,
        name=plan_day.name,
        date=date.today(),
        start_time=datetime.utcnow(),
        is_completed=False,
    )
    db.session.add(workout_session)
    db.session.flush()

    # Copy exercises from plan to session
    for plan_ex in plan_day.exercises:
        workout_ex = WorkoutExercise(
            workout_session_id=workout_session.id,
            exercise_id=plan_ex.exercise_id,
            order_in_workout=plan_ex.order_in_workout,
            target_sets=plan_ex.target_sets,
        )
        db.session.add(workout_ex)
        db.session.flush()

        # Create warmup sets
        for i in range(1, plan_ex.warmup_sets + 1):
            warmup_set = ExerciseSet(
                workout_exercise_id=workout_ex.id,
                set_number=i,
                is_warmup=True,
                is_completed=False,
            )
            db.session.add(warmup_set)

        # Create working sets
        for i in range(1, plan_ex.target_sets + 1):
            working_set = ExerciseSet(
                workout_exercise_id=workout_ex.id,
                set_number=plan_ex.warmup_sets + i,
                is_warmup=False,
                is_completed=False,
            )
            db.session.add(working_set)

    db.session.commit()
    flash("Workout started!", "success")
    return redirect(url_for("workouts.active_workout", workout_id=workout_session.id))


# ------------------ ACTIVE WORKOUT PAGE ------------------
@workout_routes.route("/active/<int:workout_id>")
def active_workout(workout_id):
    """Display active workout for user to log sets"""
    if "user_id" not in session:
        return redirect(url_for("users.login"))

    workout = WorkoutSession.query.get_or_404(workout_id)

    if workout.user_id != session["user_id"]:
        flash("Access denied", "error")
        return redirect(url_for("users.dashboard"))

    return render_template("workouts/active_workout.html", workout=workout)


# ------------------ UPDATE SET ------------------
@workout_routes.route("/set/<int:set_id>/update", methods=["POST"])
def update_set(set_id):
    """Update a single set during workout"""
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    exercise_set = ExerciseSet.query.get_or_404(set_id)

    # Verify ownership
    if exercise_set.workout_exercise.workout_session.user_id != session["user_id"]:
        return jsonify({"error": "Access denied"}), 403

    data = request.get_json()

    exercise_set.weight = data.get("weight")
    exercise_set.reps = data.get("reps")
    exercise_set.is_completed = data.get("is_completed", False)
    exercise_set.rpe = data.get("rpe")
    exercise_set.notes = data.get("notes")

    db.session.commit()

    return jsonify({"message": "Set updated", "set_id": set_id})


# ------------------ FINISH WORKOUT ------------------
@workout_routes.route("/<int:workout_id>/finish", methods=["POST"])
def finish_workout(workout_id):
    """Complete the workout session"""
    if "user_id" not in session:
        return redirect(url_for("users.login"))

    workout = WorkoutSession.query.get_or_404(workout_id)

    if workout.user_id != session["user_id"]:
        flash("Access denied", "error")
        return redirect(url_for("users.dashboard"))

    workout.end_time = datetime.utcnow()
    workout.is_completed = True
    db.session.commit()

    flash("Great work! Workout completed! 💪", "success")
    return redirect(url_for("users.dashboard"))


# ------------------ DASHBOARD (workout history) ------------------
@workout_routes.route("/history")
def history():
    """Show user's workout history"""
    if "user_id" not in session:
        return redirect(url_for("users.login"))

    workouts = (
        WorkoutSession.query.filter_by(user_id=session["user_id"], is_completed=True)
        .order_by(WorkoutSession.date.desc())
        .limit(30)
        .all()
    )

    return render_template("workouts/history.html", workouts=workouts)


# ------------------ GET WORKOUT DETAILS (API) ------------------
@workout_routes.route("/<int:workout_id>/details", methods=["GET"])
def get_workout_details(workout_id):
    """API endpoint for workout details"""
    workout = WorkoutSession.query.get_or_404(workout_id)

    return jsonify(
        {
            "id": workout.id,
            "name": workout.name,
            "date": workout.date.isoformat() if workout.date else None,
            "start_time": (
                workout.start_time.isoformat() if workout.start_time else None
            ),
            "end_time": workout.end_time.isoformat() if workout.end_time else None,
            "is_completed": workout.is_completed,
            "exercises": [
                {
                    "id": ex.id,
                    "exercise_id": ex.exercise_id,
                    "exercise_name": ex.exercise.name,
                    "muscle_group": ex.exercise.muscle_group,
                    "order": ex.order_in_workout,
                    "target_sets": ex.target_sets,
                    "sets": [
                        {
                            "id": s.id,
                            "set_number": s.set_number,
                            "weight": s.weight,
                            "reps": s.reps,
                            "is_completed": s.is_completed,
                            "is_warmup": s.is_warmup,
                            "rpe": s.rpe,
                        }
                        for s in ex.sets
                    ],
                }
                for ex in workout.exercises
            ],
        }
    )
