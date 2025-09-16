from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import datetime

app = Flask(__name__)

# Secret key for JWT
app.config["JWT_SECRET_KEY"] = "super-secret-key"
jwt = JWTManager(app)

# Connect to MongoDB Atlas
client = MongoClient("mongodb+srv://my_db_user:mydbuser1234@apryllv.kbvqx83.mongodb.net/?retryWrites=true&w=majority&appName=ApryllV")
db = client["client_server_db"]
users_collection = db["users"]
events_collection = db["events"]

# ------------------- Helpers -------------------

def serialize_doc(doc):
    """Convert MongoDB doc to JSON serializable dict"""
    doc["_id"] = str(doc["_id"])
    if "attendees" not in doc:   # normalize
        doc["attendees"] = []
    return doc

# ------------------- AUTH ROUTES -------------------

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    if users_collection.find_one({"username": username}):
        return jsonify({"error": "User already exists"}), 400

    hashed_pw = generate_password_hash(password)
    users_collection.insert_one({"username": username, "password": hashed_pw})
    return jsonify({"message": "User registered successfully"}), 201


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    user = users_collection.find_one({"username": username})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=username, expires_delta=datetime.timedelta(hours=1))
    return jsonify({"token": token}), 200

# ------------------- EVENT ROUTES -------------------

@app.route("/events", methods=["POST"])
@jwt_required()
def create_event():
    data = request.json
    name = data.get("name")
    date = data.get("date")

    if not name or not date:
        return jsonify({"error": "Event name and date required"}), 400

    event = {
        "name": name,
        "date": date,
        "attendees": []
    }
    result = events_collection.insert_one(event)
    event["_id"] = str(result.inserted_id)
    return jsonify({"message": "Event created", "event": event}), 201


@app.route("/events", methods=["GET"])
@jwt_required()
def list_events():
    events = list(events_collection.find())
    # Normalize old docs: ensure "attendees" always exists
    for ev in events:
        if "attendees" not in ev:
            events_collection.update_one(
                {"_id": ev["_id"]}, {"$set": {"attendees": []}}
            )
            ev["attendees"] = []
    events = [serialize_doc(e) for e in events]
    return jsonify(events), 200


@app.route("/events/<event_id>/register", methods=["POST"])
@jwt_required()
def register_event(event_id):
    username = request.json.get("username")
    if not username:
        return jsonify({"error": "Username required"}), 400

    event = events_collection.find_one({"_id": ObjectId(event_id)})
    if not event:
        return jsonify({"error": "Event not found"}), 404

    # Ensure attendees field exists
    if "attendees" not in event:
        event["attendees"] = []
        events_collection.update_one(
            {"_id": ObjectId(event_id)},
            {"$set": {"attendees": []}}
        )

    # Add username if not already there
    if username not in event["attendees"]:
        events_collection.update_one(
            {"_id": ObjectId(event_id)},
            {"$push": {"attendees": username}}
        )

    event = events_collection.find_one({"_id": ObjectId(event_id)})
    return jsonify({"message": "Registered successfully", "event": serialize_doc(event)}), 200

# ------------------- MAIN -------------------

if __name__ == "__main__":
    app.run(debug=True)

