import os
import json
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import redis

app = Flask(__name__)

POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db")
POSTGRES_DB = os.getenv("POSTGRES_DB", "tasks")
POSTGRES_USER = os.getenv("POSTGRES_USER", "admin")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "admin")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
cache = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }

@app.before_first_request
def init_db():
    db.create_all()

@app.route("/tasks", methods=["GET"])
def list_tasks():
    visits = cache.incr("tasks_visit_count")
    cached = cache.get("tasks_cache")
    if cached:
        tasks = json.loads(cached)
    else:
        tasks = [task.to_dict() for task in Task.query.order_by(Task.id).all()]
        cache.setex("tasks_cache", 10, json.dumps(tasks))
    return jsonify({"visits": int(visits), "tasks": tasks})

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json() or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "Le champ title est requis."}), 400

    task = Task(title=title, description=data.get("description", ""))
    db.session.add(task)
    db.session.commit()
    cache.delete("tasks_cache")
    return jsonify(task.to_dict()), 201

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    task = Task.query.get(task_id)
    if task is None:
        return jsonify({"error": "Tâche non trouvée."}), 404

    db.session.delete(task)
    db.session.commit()
    cache.delete("tasks_cache")
    return jsonify({"message": "Tâche supprimée."})

@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
