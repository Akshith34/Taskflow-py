from flask import Flask, jsonify

app = Flask(__name__)

tasks = [{"id": 1, "title": "Setup CI/CD", "done": False}]

@app.route('/tasks', methods=['GET'])
def get_tasks():
    return jsonify(tasks)

if __name__ == '__main__':
    app.run(debug=True)