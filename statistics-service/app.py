import os
import requests
from flask import Flask

app = Flask(__name__)
TASK_SERVICE_URL = os.getenv("TASK_SERVICE_URL", "http://127.0.0.1:5007/api/tasks")

@app.route('/api/health', methods=['GET'])
def health():
    return {"status": "healthy", "service": "Statistics Service"}

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    try:
        response = requests.get(TASK_SERVICE_URL, timeout=5)
        response.raise_for_status()

        tasks = response.json()["tasks"]

        total = len(tasks)
        todo = sum(1 for task in tasks if task["status"] == "To Do")
        in_progress = sum(1 for task in tasks if task["status"] == "In Progress")
        done = sum(1 for task in tasks if task["status"] == "Done")

        completion_percentage = round((done / total) * 100, 2) if total > 0 else 0

        return {
            "total_tasks": total,
            "to_do": todo,
            "in_progress": in_progress,
            "done": done,
            "completion_percentage": completion_percentage
        }

    except (requests.exceptions.RequestException, ValueError, KeyError, TypeError):
        return {"error": "Unable to retrieve task information"}, 503