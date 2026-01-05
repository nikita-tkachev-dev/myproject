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
from app.users.models import User
from datetime import datetime, date, timedelta

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

    active_goal = next((g for g in user.goals if g.is_active), None)
    if not active_goal:
        flash("Please select your goal first", "error")
        return redirect(url_for("users.select_goal"))

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

        WorkoutPlan.query.filter_by(user_id=user.id, is_active=True).update(
            {"is_active": False}
        )

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
                for k in sorted(request.form.keys())
                if k.startswith(f"day_{day_num}_exercise_") and request.form.get(k)
            ]

            # app/workouts/routers.py
            for i, key in enumerate(sorted(exercise_keys), start=1):
                exercise_id = request.form.get(key)
                if not exercise_id:
                    continue

                # 1️⃣ СНАЧАЛА получаем упражнение
                exercise = Exercise.query.get(exercise_id)
                if not exercise:
                    continue

                # 2️⃣ ПОТОМ получаем цель юзера
                active_goal = next((g for g in user.goals if g.is_active), None)
                goal_type = active_goal.goal_type if active_goal else None

                # 3️⃣ ЗАТЕМ вычисляем параметры
                target_sets, reps_min, reps_max, warmup_sets = get_plan_params(
                    user_level=user.level,
                    goal_type=goal_type,
                    muscle_group=exercise.muscle_group,
                )

                # 4️⃣ И ТОЛЬКО ПОТОМ создаём plan_exercise
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

    from app.users.models import User

    user = User.query.get(session["user_id"])
    plan = WorkoutPlan.query.get_or_404(plan_id)

    if not user:
        flash("User not found", "error")
        return redirect(url_for("users.login"))

    # Check access (только одна проверка)
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
            "workouts/edit_plan.html",
            plan=plan,
            exercises_by_group=exercises_by_group,
            user=user,
        )

    # POST: Update plan
    try:
        plan.name = request.form.get("plan_name", plan.name)

        # Get user's active goal
        active_goal = (
            next((g for g in user.goals if g.is_active), None) if user.goals else None
        )
        goal_type = active_goal.goal_type if active_goal else None

        # Update each day's exercises
        for day in plan.plan_days:
            for plan_ex in day.exercises:
                # Get new exercise ID from form
                new_exercise_id = request.form.get(f"exercise_{plan_ex.id}")
                if not new_exercise_id:
                    continue

                # Update exercise
                plan_ex.exercise_id = int(new_exercise_id)

                # Get exercise object to check muscle group
                exercise = Exercise.query.get(int(new_exercise_id))
                if not exercise:
                    continue

                # Recalculate parameters based on new exercise
                target_sets, reps_min, reps_max, warmup_sets = get_plan_params(
                    user_level=user.level,
                    goal_type=goal_type,
                    muscle_group=exercise.muscle_group,
                )

                plan_ex.target_sets = target_sets
                plan_ex.target_reps_min = reps_min
                plan_ex.target_reps_max = reps_max
                plan_ex.warmup_sets = warmup_sets

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

    active_workout = WorkoutSession.query.filter_by(
        user_id=session["user_id"], is_completed=False
    ).first()

    if active_workout:
        flash("You already have an active workout!", "warning")
        return redirect(
            url_for("workouts.active_workout", workout_id=active_workout.id)
        )

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


# ------------------- DELETE SET ------------------
@workout_routes.route("/set/<int:set_id>/delete", methods=["POST"])
def delete_set(set_id):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    exercise_set = ExerciseSet.query.get_or_404(set_id)

    # Проверка владельца
    if exercise_set.workout_exercise.workout_session.user_id != session["user_id"]:
        return jsonify({"error": "Access denied"}), 403

    try:
        db.session.delete(exercise_set)
        db.session.commit()
        return jsonify({"message": "Set deleted", "set_id": set_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


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

    from sqlalchemy.orm import joinedload
    from typing import cast
    from sqlalchemy.orm.attributes import InstrumentedAttribute

    workouts = (
        WorkoutSession.query.options(
            joinedload(
                cast(InstrumentedAttribute, WorkoutSession.exercises)
            ).joinedload(cast(InstrumentedAttribute, WorkoutExercise.exercise))
        )
        .filter_by(user_id=session["user_id"], is_completed=True)
        .order_by(WorkoutSession.date.desc())
        .limit(30)
        .all()
    )

    # Статистика
    stats = get_user_stats(session["user_id"])

    # Chart data
    chart_data = {
        "labels": [w.date.strftime("%d.%m") for w in workouts],
        "values": [w.total_volume for w in workouts],
    }

    # Личные рекорды (пока пустой список)
    personal_records = []

    # Для кнопки Load More
    has_more = len(workouts) == 30

    return render_template(
        "workouts/history.html",
        workouts=workouts,
        stats=stats,
        chart_data=chart_data,
        personal_records=personal_records,
        has_more=has_more,
    )


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


# ------------------ FUNCTIONS(extras) ------------------
def get_plan_params(user_level, goal_type, muscle_group):
    """Determine plan parameters based on user level, goal, and muscle group"""
    if user_level == "beginner":
        target_sets = 2
        reps_min, reps_max = 12, 15
        warmup_sets = 1
    elif user_level == "intermediate":
        target_sets = 4
        reps_min, reps_max = 8, 12
        warmup_sets = 2
    else:  # advanced
        target_sets = 5
        reps_min, reps_max = 6, 10
        warmup_sets = 2

    if goal_type == "weight_loss" or goal_type == "endurance":
        reps_min, reps_max = 12, 15
    elif goal_type == "muscle_gain":
        reps_min, reps_max = 8, 12
    elif goal_type == "strength":
        reps_min, reps_max = 6, 8

    # Special case for core and calves - always 3 sets
    if muscle_group == "core":
        target_sets = 3
        reps_min, reps_max = 15, 20
        warmup_sets = 0
    elif muscle_group == "calves":
        target_sets = 3
        reps_min, reps_max = 12, 15
        warmup_sets = 1

    return target_sets, reps_min, reps_max, warmup_sets


def get_user_stats(user_id):
    # 1. Completed workouts count
    workouts = WorkoutSession.query.filter_by(user_id=user_id, is_completed=True).all()

    total_workouts = len(workouts)

    # 2. DAY STREAK calculation
    dates = sorted({w.date for w in workouts}, reverse=True)
    today = datetime.utcnow().date()

    streak = 0
    expected_date = today

    for workout_date in dates:
        if workout_date == expected_date:
            streak += 1
            expected_date -= timedelta(days=1)
        elif workout_date < expected_date:
            break

    # 3. Total volume
    total_volume = (
        db.session.query(db.func.sum(ExerciseSet.weight * ExerciseSet.reps))
        .join(WorkoutExercise, ExerciseSet.workout_exercise_id == WorkoutExercise.id)
        .join(WorkoutSession, WorkoutExercise.workout_session_id == WorkoutSession.id)
        .filter(WorkoutSession.user_id == user_id)
        .filter(ExerciseSet.is_warmup == False)
        .scalar()
        or 0
    )

    # 4. Avg duration
    durations = [
        (w.end_time - w.start_time).seconds / 60 for w in workouts if w.end_time
    ]
    avg_duration = round(sum(durations) / len(durations)) if durations else 0

    return {
        "total_workouts": total_workouts,
        "current_streak": streak,
        "total_volume": int(total_volume),
        "avg_duration": avg_duration,
    }
