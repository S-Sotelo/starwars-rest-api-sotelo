import os
from flask import Flask, request, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planet, Favorite_People, Favorite_Planet

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)

# USER Endpoints
@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    results = [{"id": user.id, "username": user.username} for user in users]
    return jsonify(results), 200

@app.route('/users/<int:user_id>/favorites', methods=['GET'])
def get_user_favorites(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404

    favorite_people = Favorite_People.query.filter_by(user_id=user_id).all()
    favorite_planets = Favorite_Planet.query.filter_by(user_id=user_id).all()

    favorite_people_list = [{"id": fav.id, "people_id": fav.people_id} for fav in favorite_people]
    favorite_planets_list = [{"id": fav.id, "planet_id": fav.planet_id} for fav in favorite_planets]

    favorites = {
        "favorite_people": favorite_people_list,
        "favorite_planets": favorite_planets_list
    }

    return jsonify(favorites), 200

# PEOPLE Endpoints
@app.route('/people', methods=['GET'])
def get_people():
    people = People.query.all()
    people_list = [p.serialize() for p in people]
    return jsonify(people_list), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_people_id(people_id):
    person = People.query.get(people_id)
    if person:
        return jsonify(person.serialize()), 200
    return jsonify({"msg": "Person not found"}), 404

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_people(people_id):
    user_id = request.json.get("user_id")
    if not user_id:
        return jsonify({"msg": "User ID is required"}), 400
    new_favorite = Favorite_People(user_id=user_id, people_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"msg": "Favorite people added"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_people(people_id):
    user_id = request.json.get("user_id")
    favorite = Favorite_People.query.filter_by(user_id=user_id, people_id=people_id).first()
    if not favorite:
        return jsonify({"msg": "Favorite people not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Favorite people deleted"}), 200

# PLANETS Endpoints
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all()
    planet_list = [planet.serialize() for planet in planets]
    return jsonify(planet_list), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_id(planet_id):
    planet = Planet.query.get(planet_id)
    if planet:
        return jsonify(planet.serialize()), 200
    return jsonify({"msg": "Planet not found"}), 404

@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.json.get("user_id")
    if not user_id:
        return jsonify({"msg": "User ID is required"}), 400
    new_favorite = Favorite_Planet(user_id=user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"msg": "Favorite planet added"}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.json.get("user_id")
    favorite = Favorite_Planet.query.filter_by(user_id=user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"msg": "Favorite planet not found"}), 404
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Favorite planet deleted"}), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=True)
