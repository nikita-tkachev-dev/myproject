from flask import Blueprint, request, jsonify
from app.extensions import db
from .models import NutritionLog

nutrition_routes = Blueprint("nutrition", __name__, url_prefix="/nutrition")

# Создание записи питания
@nutrition_routes.route("/create", methods=["POST"])
def create_nutrition():
    data = request.get_json()

    if not data or not all(k in data for k in ("user_id", "name", "amount")):
        return jsonify({"error": "Missing required fields: user_id, name, amount"}), 400

    log = NutritionLog(
        user_id=data["user_id"],
        name=data["name"],
        amount=data["amount"],
        time=data.get("time"),  # ожидается формат "HH:MM:SS", если передан
        date=data.get("date")   # ожидается формат "YYYY-MM-DD", если передан
    )

    try:
        db.session.add(log)
        db.session.commit()
        return jsonify({"message": f"Nutrition log created!", "id": log.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Получение всех записей пользователя
@nutrition_routes.route("/user/<int:user_id>", methods=["GET"])
def get_user_nutrition(user_id):
    logs = NutritionLog.query.filter_by(user_id=user_id).order_by(NutritionLog.date.desc(), NutritionLog.time.desc()).all()
    return jsonify([
        {
            "id": log.id,
            "user_id": log.user_id,
            "name": log.name,
            "amount": log.amount,
            "date": log.date.isoformat() if log.date else None,
            "time": log.time.isoformat() if log.time else None
        } for log in logs
    ])
