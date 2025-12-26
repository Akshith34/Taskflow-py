import pytest
from app import app, tasks


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_tasks(client):
    response = client.get('/tasks')
    assert response.status_code == 200
    assert b"Setup CI/CD" in response.data

def test_create_task(client):
    response = client.post('/tasks', json={"title": "New item"})
    assert response.status_code == 201
    assert b"New item" in response.data
    assert any(task["title"] == "New item" for task in tasks)

def test_delete_task(client):
    response = client.delete('/tasks/1')
    assert response.status_code == 200
    assert b"deleted" in response.data

def test_homepage(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"TaskFlow" in response.data

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
