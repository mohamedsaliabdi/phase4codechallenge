# app.py
from flask import Flask, jsonify, request
from models import db, Hero, Power, HeroPower
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///superheroes.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# ---------- ROUTES ----------

# a. GET /heroes
@app.route("/heroes", methods=["GET"])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([h.to_dict() for h in heroes]), 200


# b. GET /heroes/:id
@app.route("/heroes/<int:hero_id>", methods=["GET"])
def get_hero(hero_id):
    hero = Hero.query.get(hero_id)
    if not hero:
        return jsonify({"error": "Hero not found"}), 404
    return jsonify(hero.to_dict_with_powers()), 200


# c. GET /powers
@app.route("/powers", methods=["GET"])
def get_powers():
    powers = Power.query.all()
    return jsonify([p.to_dict() for p in powers]), 200


# d. GET /powers/:id
@app.route("/powers/<int:power_id>", methods=["GET"])
def get_power(power_id):
    power = Power.query.get(power_id)
    if not power:
        return jsonify({"error": "Power not found"}), 404
    return jsonify(power.to_dict()), 200


# e. PATCH /powers/:id
@app.route("/powers/<int:power_id>", methods=["PATCH"])
def update_power(power_id):
    power = Power.query.get(power_id)
    if not power:
        return jsonify({"error": "Power not found"}), 404

    data = request.get_json(silent=True) or {}
    description = data.get("description")

    try:
        power.description = description
        db.session.commit()
    except (ValueError, IntegrityError):
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400

    return jsonify(power.to_dict()), 200


# f. POST /hero_powers
@app.route("/hero_powers", methods=["POST"])
def create_hero_power():
    data = request.get_json(silent=True) or {}
    hero_id = data.get("hero_id")
    power_id = data.get("power_id")
    strength = data.get("strength")

    hero = Hero.query.get(hero_id)
    power = Power.query.get(power_id)
    if not hero or not power:
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        hero_power = HeroPower(
            hero_id=hero_id,
            power_id=power_id,
            strength=strength
        )
        db.session.add(hero_power)
        db.session.commit()
    except (ValueError, IntegrityError):
        db.session.rollback()
        return jsonify({"errors": ["validation errors"]}), 400

    return jsonify(hero_power.to_dict_full()), 201


# Root route
@app.route("/")
def home():
    return jsonify({"message": "Superheroes API is running"}), 200


if __name__ == "__main__":
    app.run(debug=True)
