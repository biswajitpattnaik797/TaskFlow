import os
import requests
from flask import Flask, request, render_template
from pymongo import MongoClient
from bson import ObjectId

app = Flask(__name__)
STATISTICS_SERVICE_URL = os.getenv("STATISTICS_SERVICE_URL", "http://127.0.0.1:5001/api/statistics")
client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
db = client["taskflow"]
tasks_collection = db["tasks"]

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/dashboard/statistics', methods=['GET'])
def dashboard_statistics():
    try:
        response = requests.get(STATISTICS_SERVICE_URL, timeout=5)
        response.raise_for_status()
        return response.json(), 200

    except (requests.exceptions.RequestException, ValueError) as error:
        app.logger.error("Statistics Service request failed: %s", error)
        return {"error": "Statistics Service is unavailable"}, 503

@app.route('/api/health', methods=['GET'])
def health():
    return {"status": "healthy", "service": "Task Service"}

tasks = [
    {
        "id": 1,
        "title": "Complete Kubernetes Assignment",
        "description": "Build and deploy TaskFlow",
        "priority": "High",
        "status": "In Progress"
    },
    {
        "id": 2,
        "title": "Prepare Assignment Report",
        "description": "Document the architecture and design decisions",
        "priority": "Medium",
        "status": "To Do"
    }
]

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    tasks = list(tasks_collection.find())

    for task in tasks:
        task["id"] = str(task.pop("_id"))

    return {"tasks": tasks}

@app.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.get_json(silent=True)

    if not isinstance(data, dict) or not isinstance(data.get("title"), str) or not data["title"].strip():
        return {"error": "A task title is required"}, 400

    new_task = {
        "title": data["title"].strip(),
        "description": data.get("description", ""),
        "priority": data.get("priority", "Medium"),
        "status": data.get("status", "To Do")
    }

    tasks_collection.insert_one(new_task)
    new_task["id"] = str(new_task.pop("_id"))

    return {"message": "Task created successfully", "task": new_task}, 201

@app.route('/api/tasks/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return {"error": "Valid JSON data is required"}, 400

    if not ObjectId.is_valid(task_id):
        return {"error": "Invalid task ID"}, 400

    allowed_fields = ["title", "description", "priority", "status"]
    updates = {key: value for key, value in data.items()
               if key in allowed_fields}

    if not updates:
        return {"error": "No valid fields to update"}, 400

    result = tasks_collection.update_one(
        {"_id": ObjectId(task_id)},
        {"$set": updates}
    )

    if result.matched_count == 0:
        return {"error": "Task not found"}, 404

    return {"message": "Task updated successfully"}, 200

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):

    if not ObjectId.is_valid(task_id):
        return {"error": "Invalid task ID"}, 400

    result = tasks_collection.delete_one(
        {"_id": ObjectId(task_id)}
    )

    if result.deleted_count == 0:
        return {"error": "Task not found"}, 404

    return {"message": "Task deleted successfully"}, 200