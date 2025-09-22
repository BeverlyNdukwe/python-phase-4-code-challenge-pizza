#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
from flask import jsonify
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route("/restaurants", methods=["GET", "POST"])
def restaurants():
    if request.method == "GET":
        restaurants = Restaurant.query.all()

        return jsonify([restaurant.to_dict(rules=("-restaurant_pizzas",)) for restaurant in restaurants]), 200
    elif request.method == "POST":
        data = request.get_json()
        new_restaurant = Restaurant(
            name=data.get("name"),
            address=data.get("address")
        )
        db.session.add(new_restaurant)
        db.session.commit()

        return jsonify(new_restaurant.to_dict(rules=("-restaurant_pizzas",))), 201
        
@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route("/pizzas", methods=["GET"])
def pizzas():
    pizzas = Pizza.query.all()
    return jsonify([pizza.to_dict(rules=("-restaurant_pizzas",)) for pizza in pizzas]), 200

@app.route("/restaurant_pizzas", methods=["POST"])
def create_restaurant_pizza():
    data = request.get_json()
    try:
        rp = RestaurantPizza(
            price=data['price'],
            pizza_id=data['pizza_id'],
            restaurant_id=data['restaurant_id']
        )
        db.session.add(rp)
        db.session.commit()
        return jsonify(rp.to_dict()), 201
    except ValueError as e:
        return jsonify({"errors": ["validation errors"]}), 400

@app.route("/restaurants/<int:id>", methods=["GET", "DELETE"])
def get_or_delete_restaurant(id):
    restaurant = Restaurant.query.get(id)
    if request.method == "GET":
        if restaurant is None:
            return jsonify({"error": "Restaurant not found"}), 404
        
        return jsonify(restaurant.to_dict(rules=())), 200
    elif request.method == "DELETE":
        if restaurant is None:
            return jsonify({"error": "Restaurant not found"}), 404
        db.session.delete(restaurant)
        db.session.commit()
        return '', 204


if __name__ == "__main__":
    app.run(port=5555, debug=True)