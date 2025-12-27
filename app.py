from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

tasks = [{"id": 1, "title": "Setup CI/CD", "done": False}]


def _find_task(task_id: int):
    return next((task for task in tasks if task["id"] == task_id), None)


def _next_id() -> int:
    return max((task["id"] for task in tasks), default=0) + 1


@app.route('/tasks', methods=['GET', 'POST'])
def tasks_endpoint():
    if request.method == 'POST':
        data = request.get_json() or {}
        title = (data.get('title') or '').strip()

        if not title:
            return jsonify({"message": "Title is required."}), 400

        task = {"id": _next_id(), "title": title, "done": False}
        tasks.append(task)
        return jsonify(task), 201

    return jsonify(tasks)

@app.route('/tasks/<int:task_id>', methods=['GET', 'PATCH', 'PUT', 'DELETE'])
def task_detail(task_id):
    task = _find_task(task_id)
    if not task:
        return jsonify({"message": "Task not found."}), 404

    if request.method == 'GET':
        return jsonify(task), 200

    if request.method == 'DELETE':
        tasks.remove(task)
        return jsonify({"message": f"Task {task_id} deleted!"}), 200

    data = request.get_json() or {}
    updated = False

    if "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"message": "Title cannot be empty."}), 400
        task["title"] = title
        updated = True

    if "done" in data:
        done_value = data.get("done")
        if not isinstance(done_value, bool):
            return jsonify({"message": "Done must be a boolean."}), 400
        task["done"] = done_value
        updated = True

    if not updated:
        return jsonify({"message": "No valid fields to update."}), 400

    return jsonify(task), 200

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() or request.form
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()

        if not username or not password:
            return jsonify({"message": "Username and password are required."}), 400

        # Placeholder success response for this demo
        return jsonify({"message": f"Welcome, {username}!"}), 200

    return render_template('login.html')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
