import pytest
from app import app

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_tasks(client):
    """Test if the tasks endpoint returns a 200 status."""
    response = client.get('/tasks')
    assert response.status_code == 200
    assert b"Setup CI/CD" in response.data