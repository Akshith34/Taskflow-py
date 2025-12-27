from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

# Simple in-memory list to keep the demo flowing
tasks = [{"id": 1, "title": "Setup CI/CD", "done": False}]

@app.route('/tasks', methods=['GET', 'POST'])
def get_tasks():
    if request.method == 'POST':
        data = request.get_json() or {}
        title = (data.get('title') or '').strip()

        if not title:
            return jsonify({"message": "Title is required."}), 400

        new_id = tasks[-1]["id"] + 1 if tasks else 1
        task = {"id": new_id, "title": title, "done": False}
        tasks.append(task)
        return jsonify(task), 201

    return jsonify(tasks)

@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    # In a real app, you'd delete from the DB here
    return jsonify({"message": f"Task {task_id} deleted!"}), 200

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

@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.get_json()
    # ... logic ...
    return jsonify({"message": "Task added!"}), 500 # Changed 201 to 500 (Error)

if __name__ == '__main__':
    app.run(debug=True)
