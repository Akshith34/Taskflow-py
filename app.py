from flask import Flask, jsonify

app = Flask(__name__)

tasks = [{"id": 1, "title": "Setup CI/CD", "done": False}]

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

if __name__ == '__main__':
    app.run(debug=True)
    
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    # In a real app, you'd delete from the DB here
    return jsonify({"message": f"Task {task_id} deleted!"}), 200