import os
import logging
from logging.handlers import RotatingFileHandler
import random
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, User, Interaction  # Import models

# Load environment variables
load_dotenv()

# Initialize Flask App
app = Flask(__name__)
CORS(app)

# Configure Database
base_dir = os.path.abspath(os.path.dirname(__file__))
db_dir = os.path.join(base_dir, "affirmAI_data")
db_path = os.path.join(db_dir, "affirmai.db")

# Ensure Database Directory Exists
if not os.path.exists(db_dir):
    os.makedirs(db_dir)

app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{db_path}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Load secret key from environment variable
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "fallback-secret-key")

# Initialize Extensions
db.init_app(app)
jwt = JWTManager(app)

# Logging Setup
log_file_path = "logs/flask_log.txt"
log_dir = os.path.dirname(log_file_path)

# Ensure Logs Directory Exists
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

handler = RotatingFileHandler(log_file_path, maxBytes=1000000, backupCount=5)
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - [%(name)s] %(message)s")
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)

# Database Initialization
try:
    with app.app_context():
        db.create_all()
except Exception as e:
    logging.error(f"Database initialization failed: {e}")
    print("Database error:", e)

@app.route("/")
def home():
    logging.info("Accessed home endpoint")
    return jsonify({"message": "AffirmAI Backend Running"}), 200

# User Registration
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        logging.warning("Missing username or password in registration request")
        return jsonify({"error": "Missing username or password"}), 400

    if User.query.filter_by(username=username).first():
        logging.warning(f"Attempted registration with existing username: {username}")
        return jsonify({"error": "Username already exists"}), 400

    user = User(username=username)
    user.set_password(password)  # Secure password storage
    db.session.add(user)
    db.session.commit()
    logging.info(f"New user registered: {username} from {request.remote_addr}")

    return jsonify({"message": "User registered successfully!"}), 201

# User Login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        logging.warning("Missing username or password in login request")
        return jsonify({"error": "Missing username or password"}), 400

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        access_token = create_access_token(identity=username)
        logging.info(f"User logged in: {username} from {request.remote_addr}")
        return jsonify({"access_token": access_token}), 200

    logging.warning(f"Failed login attempt for username: {username}")
    return jsonify({"error": "Invalid credentials"}), 401

# AI Learning: Log and Retrieve Past Responses
@app.route("/log_interaction", methods=["POST"])
@jwt_required()
def log_interaction():
    data = request.get_json()
    user_input = data.get("user_input")

    if not user_input:
        logging.warning("Missing input in log_interaction request")
        return jsonify({"error": "Missing input"}), 400

    past_responses = Interaction.query.filter(Interaction.user_input.ilike(f"%{user_input}%")).all()
    ai_response = random.choice([resp.ai_response for resp in past_responses]) if past_responses else "I'm still learning! What do you think?"

    interaction = Interaction(user_input=user_input, ai_response=ai_response)
    db.session.add(interaction)
    db.session.commit()
    logging.info(
        f"Logged interaction: {user_input} -> {ai_response}",
        extra={"name": get_jwt_identity()}
    )

    return jsonify({"message": "Logged successfully", "ai_response": ai_response}), 200

# Fetch AI History with Pagination
@app.route("/get_responses", methods=["GET"])
@jwt_required()
def get_responses():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)
    paginated_interactions = Interaction.query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify([{"input": i.user_input, "output": i.ai_response} for i in paginated_interactions.items])

# Start Flask Server
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Render sets $PORT dynamically
    app.run(host="0.0.0.0", port=port)
