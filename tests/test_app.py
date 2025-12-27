import pytest
from app import app, db, User, Task


@pytest.fixture(autouse=True)
def setup_db():
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["TESTING"] = True
    with app.app_context():
        db.drop_all()
        db.create_all()
        user = User(username="demo")
        user.set_password("secret")
        db.session.add(user)
        db.session.commit()

        task = Task(title="Setup CI/CD", user_id=user.id)
        db.session.add(task)
        db.session.commit()
    yield
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_client(client):
    client.post('/login', json={"username": "demo", "password": "secret"})
    return client


def test_register_creates_user(client):
    response = client.post('/register', json={"username": "alex", "password": "pass"})
    assert response.status_code == 201
    with app.app_context():
        assert User.query.filter_by(username="alex").first() is not None


def test_login_success(client):
    response = client.post('/login', json={"username": "demo", "password": "secret"})
    assert response.status_code == 200
    assert b"Welcome back" in response.data


def test_login_requires_fields(client):
    response = client.post('/login', json={"username": "", "password": ""})
    assert response.status_code == 400


def test_tasks_require_auth(client):
    response = client.get('/tasks')
    assert response.status_code == 401


def test_get_tasks(auth_client):
    response = auth_client.get('/tasks')
    assert response.status_code == 200
    body = response.get_json()
    assert body[0]["title"] == "Setup CI/CD"


def test_create_task(auth_client):
    response = auth_client.post('/tasks', json={"title": "New item"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "New item"
    with app.app_context():
        assert Task.query.filter_by(title="New item").first() is not None


def test_create_task_requires_title(auth_client):
    response = auth_client.post('/tasks', json={"title": "  "})
    assert response.status_code == 400


def test_task_detail_get(auth_client):
    response = auth_client.get('/tasks/1')
    assert response.status_code == 200
    assert response.get_json()["title"] == "Setup CI/CD"


def test_update_task_title(auth_client):
    response = auth_client.patch('/tasks/1', json={"title": "Updated"})
    assert response.status_code == 200
    assert response.get_json()["title"] == "Updated"


def test_toggle_done(auth_client):
    response = auth_client.patch('/tasks/1', json={"done": True})
    assert response.status_code == 200
    assert response.get_json()["done"] is True


def test_delete_task(auth_client):
    response = auth_client.delete('/tasks/1')
    assert response.status_code == 200
    with app.app_context():
        assert Task.query.filter_by(id=1).first() is None


def test_delete_missing_task(auth_client):
    response = auth_client.delete('/tasks/999')
    assert response.status_code == 404


def test_cannot_access_other_user_tasks(auth_client):
    with app.app_context():
        other = User(username="other")
        other.set_password("secret")
        db.session.add(other)
        db.session.commit()
        other_task = Task(title="Other task", user_id=other.id)
        db.session.add(other_task)
        db.session.commit()
        other_task_id = other_task.id
    response = auth_client.get(f'/tasks/{other_task_id}')
    assert response.status_code == 404
