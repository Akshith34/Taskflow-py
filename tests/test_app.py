import pytest
from app import app, tasks


@pytest.fixture(autouse=True)
def reset_tasks():
    tasks.clear()
    tasks.extend([{"id": 1, "title": "Setup CI/CD", "done": False}])


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_tasks(client):
    response = client.get('/tasks')
    assert response.status_code == 200
    body = response.get_json()
    assert body[0]["title"] == "Setup CI/CD"

def test_create_task(client):
    response = client.post('/tasks', json={"title": "New item"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["title"] == "New item"
    assert data["id"] == 2
    assert any(task["title"] == "New item" for task in tasks)

def test_create_task_requires_title(client):
    response = client.post('/tasks', json={"title": "  "})
    assert response.status_code == 400

def test_task_detail_get(client):
    response = client.get('/tasks/1')
    assert response.status_code == 200
    assert response.get_json()["title"] == "Setup CI/CD"

def test_update_task_title(client):
    client.post('/tasks', json={"title": "Old"})
    response = client.patch('/tasks/2', json={"title": "Updated"})
    assert response.status_code == 200
    assert response.get_json()["title"] == "Updated"

def test_toggle_done(client):
    response = client.patch('/tasks/1', json={"done": True})
    assert response.status_code == 200
    assert response.get_json()["done"] is True

def test_delete_task(client):
    response = client.delete('/tasks/1')
    assert response.status_code == 200
    assert all(task["id"] != 1 for task in tasks)

def test_delete_missing_task(client):
    response = client.delete('/tasks/999')
    assert response.status_code == 404

def test_login_page(client):
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Welcome back" in response.data

def test_login_success(client):
    response = client.post('/login', json={"username": "alex", "password": "secret"})
    assert response.status_code == 200
    assert b"Welcome, alex!" in response.data

def test_login_requires_fields(client):
    response = client.post('/login', json={"username": "", "password": ""})
    assert response.status_code == 400
