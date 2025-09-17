from flask import Blueprint, request, jsonify
from app.extensions import db
from .models import Goal

goal_routers = Blueprint("goal_routers", __name__, url_prefix="/goals")

@goal_routers.route("/create", methods=["POST"])
def create_goal():
    data = request.get_json()
    goal = Goal(
        user_id = data["user_id"],
        type = data["type"],
        target_value = data["target_value"],
        deadline = data["deadline"],
        achieved =data["achieved"]
    )

    db.session.add(goal)
    db.session.commit()
    return jsonify({"goal_id": goal.id})

@goal_routers.route("/all", methods=["GET"])
def get_goals():
    goals = Goal.query.all()
    result = []
    for g in goals:
        result.append({
            "id": g.id,
            "type": g.type,
            "target_value": g.target_value,
            "deadline": g.deadline,
            "achieved": g.achieved
        })
