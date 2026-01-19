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
from .models import User, Goal
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.workouts.routers import get_user_stats

user_routes = Blueprint("users", __name__, url_prefix="/users")


def _create_user(data):
    """Helper to create a user from a dict. Returns (user, (error_message, status)) on failure."""
    if not data or not all(k in data for k in ("username", "email", "password")):
        return None, ("Missing required fields", 400)

    # Check uniqueness
    if User.query.filter(
        (User.username == data["username"]) | (User.email == data["email"])
    ).first():
        return None, ("Username or email already exists", 400)

    # Safe parsing of input values (dates/numbers may be empty strings)
    birth_date = None
    bd = data.get("birth_date")
    if bd:
        try:
            birth_date = datetime.strptime(str(bd), "%Y-%m-%d").date()
        except Exception:
            birth_date = None

    height = None
    h_raw = data.get("height")
    if h_raw is not None and str(h_raw).strip() != "":
        try:
            # allow integer or float strings
            height = int(float(str(h_raw)))
        except Exception:
            height = None

    weight = None
    w_raw = data.get("weight")
    if w_raw is not None and str(w_raw).strip() != "":
        try:
            weight = float(str(w_raw))
        except Exception:
            weight = None

    # Create the user
    user = User(
        username=data["username"],
        email=data["email"],
        level=data.get("level", "beginner"),
        birth_date=birth_date,
        height=height,
        weight=weight,
        gender=data.get("gender"),
    )
    user.password_hash = generate_password_hash(data["password"])

    try:
        db.session.add(user)
        db.session.flush()  # Ensure user.id is available

        db.session.commit()
        return user, None
    except Exception as e:
        db.session.rollback()
        return None, (str(e), 500)


@user_routes.route(
    "/create", methods=["POST"]
)  # accepts JSON or form; will set session in both
def create_user():
    # support form submissions and JSON
    data = None
    if request.form and len(request.form) > 0:
        # convert ImmutableMultiDict to plain dict
        data = request.form.to_dict()
    else:
        data = request.get_json()

    user, error = _create_user(data)
    if error:
        if request.is_json:
            return jsonify({"error": error[0]}), error[1]
        flash(error[0], "error")
        return redirect(url_for("users.register"))

    # create session for both form and JSON registration
    session["user_id"] = getattr(user, "id", None)

    if request.is_json:
        # safe message
        username_safe = getattr(user, "username", "<user>")
        return (
            jsonify({"message": f"User {username_safe} created!"}),
            201,
        )

    flash("Account created and logged in", "success")
    return redirect(url_for("users.select_level"))


# --- Server-rendered registration/login ---
@user_routes.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form = request.form
        # Do not set level on registration form — user selects it on the next page
        data = {
            "username": form.get("username"),
            "email": form.get("email"),
            "password": form.get("password"),
            "birth_date": form.get("birth_date"),
            "height": form.get("height"),
            "weight": form.get("weight"),
            "gender": form.get("gender"),
        }
        user, error = _create_user(data)
        if error:
            flash(error[0], "error")
            return render_template("users/register.html", form=data)
        # Auto-login after register
        session["user_id"] = getattr(user, "id", None)
        flash("Account created and logged in", "success")
        return redirect(url_for("users.select_level"))

    return render_template("users/register.html")


@user_routes.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        identifier = request.form.get("identifier")  # username or email
        password = request.form.get("password")

        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()
        if not user or not check_password_hash(user.password_hash, password or ""):
            flash("Invalid credentials", "error")
            return render_template("users/login.html")

        session["user_id"] = user.id
        flash("Logged in", "success")
        return redirect(url_for("users.dashboard"))

    return render_template("users/login.html")


@user_routes.route("/logout")
def logout():
    session.pop("user_id", None)
    flash("Logged out", "info")
    return redirect(url_for("users.login"))


@user_routes.route("/select-level", methods=["GET", "POST"])
def select_level():
    if "user_id" not in session:
        flash("Please log in first", "error")
        return redirect(url_for("users.login"))

    user = User.query.get(session["user_id"])
    if request.method == "POST":
        level = request.form.get("level")

        if level not in ("beginner", "intermediate", "advanced"):
            flash("Invalid level", "error")
            return render_template("users/select_level.html", user=user)

        # guard: ensure user exists
        if user:
            user.level = level
            # Deactivate existing plans when changing level
            for plan in user.workout_plans:
                plan.is_active = False
            db.session.commit()
            flash("Level saved. Please create a new workout plan.", "success")

        else:
            flash("User not found", "error")
            return redirect(url_for("users.login"))
        return redirect(url_for("users.select_goal"))

    return render_template("users/select_level.html", user=user)


@user_routes.route("/select-goal", methods=["GET", "POST"])
def select_goal():
    if "user_id" not in session:
        flash("Please log in first", "error")
        return redirect(url_for("users.login"))

    user = User.query.get(session["user_id"])
    if not user:
        flash("User not found", "error")
        return redirect(url_for("users.login"))

    existing_goal = Goal.query.filter_by(user_id=user.id, is_active=True).first()

    if request.method == "POST":
        goal_type = request.form.get("goal_type")
        target_value = request.form.get("target_value")
        unit = request.form.get("unit")
        target_date = request.form.get("target_date")

        if not goal_type:
            flash("Please select a goal", "error")
            return render_template(
                "users/select_goal.html", user=user, existing_goal=existing_goal
            )

        # Проверка: уже есть цель → не создаём новую
        if existing_goal:
            existing_goal.is_active = False

        current_value = None
        if goal_type in ["weight_loss", "muscle_gain"]:
            current_value = user.weight

        goal = Goal(
            user_id=user.id,
            goal_type=goal_type,
            target_value=float(target_value) if target_value else None,
            current_value=current_value,
            unit=unit,
            target_date=(
                datetime.strptime(target_date, "%Y-%m-%d").date()
                if target_date
                else None
            ),
        )

        db.session.add(goal)
        db.session.commit()

        flash("Goal saved successfully", "success")

        # Новый юзер: создаём план
        if not user.workout_plans:
            return redirect(url_for("workouts.create_plan"))

        # Старый: сразу на дэшборд
        return redirect(url_for("users.dashboard"))

    return render_template(
        "users/select_goal.html", user=user, existing_goal=existing_goal
    )


@user_routes.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("users.login"))
    user = User.query.get(session["user_id"])
    stats = get_user_stats(user.id) if user else {}
    return render_template("users/dashboard.html", user=user, stats=stats)
