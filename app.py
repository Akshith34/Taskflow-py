import os
from flask import Flask, render_template, jsonify, request, redirect
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///taskflow.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = "login"


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("User", backref="tasks")

    def to_dict(self):
        return {"id": self.id, "title": self.title, "done": self.done}


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@login_manager.unauthorized_handler
def unauthorized():
    accept_header = request.headers.get("Accept", "")
    wants_json = "application/json" in accept_header
    if wants_json or request.path.startswith("/tasks"):
        return jsonify({"message": "Login required."}), 401
    return redirect("/login")


@app.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks_endpoint():
    if request.method == "POST":
        data = request.get_json() or {}
        title = (data.get("title") or "").strip()

        if not title:
            return jsonify({"message": "Title is required."}), 400

        task = Task(title=title, done=False, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        return jsonify(task.to_dict()), 201

    user_tasks = (
        Task.query.filter_by(user_id=current_user.id)
        .order_by(Task.id.asc())
        .all()
    )
    return jsonify([task.to_dict() for task in user_tasks])


@app.route("/tasks/<int:task_id>", methods=["GET", "PATCH", "PUT", "DELETE"])
@login_required
def task_detail(task_id):
    task = Task.query.filter_by(id=task_id, user_id=current_user.id).first()
    if not task:
        return jsonify({"message": "Task not found."}), 404

    if request.method == "GET":
        return jsonify(task.to_dict()), 200

    if request.method == "DELETE":
        db.session.delete(task)
        db.session.commit()
        return jsonify({"message": f"Task {task_id} deleted!"}), 200

    data = request.get_json() or {}
    updated = False

    if "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"message": "Title cannot be empty."}), 400
        task.title = title
        updated = True

    if "done" in data:
        done_value = data.get("done")
        if not isinstance(done_value, bool):
            return jsonify({"message": "Done must be a boolean."}), 400
        task.done = done_value
        updated = True

    if not updated:
        return jsonify({"message": "No valid fields to update."}), 400

    db.session.commit()
    return jsonify(task.to_dict()), 200


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.get_json() or request.form
        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()

        if not username or not password:
            return jsonify({"message": "Username and password are required."}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"message": "Username already taken."}), 400

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return jsonify({"message": f"Account created for {username}."}), 201

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json() or request.form
        username = (data.get("username") or "").strip()
        password = (data.get("password") or "").strip()

        if not username or not password:
            return jsonify({"message": "Username and password are required."}), 400

        user = User.query.filter_by(username=username).first()
        if not user or not user.check_password(password):
            return jsonify({"message": "Invalid credentials."}), 401

        login_user(user)
        return jsonify({"message": f"Welcome back, {username}!"}), 200

    return render_template("login.html")


@app.route("/logout", methods=["POST", "GET"])
@login_required
def logout():
    logout_user()
    if request.accept_mimetypes.accept_json:
        return jsonify({"message": "Logged out."}), 200
    return redirect("/login")


@app.route("/")
@login_required
def index():
    return render_template("index.html")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
