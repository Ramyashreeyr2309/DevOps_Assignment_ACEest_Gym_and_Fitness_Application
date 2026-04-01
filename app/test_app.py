import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_route(client):
    """Test the index route for a successful response."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"programs" in response.data  # Check if 'programs' is in the response

def test_save_client_success(client):
    """Test saving a client successfully."""
    data = {
        "name": "John Doe",
        "age": 30,
        "weight": 75,
        "program": "Fat Loss (FL)",
        "adherence": 90
    }
    response = client.post('/save_client', json=data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == "success"
    assert "Client John Doe saved!" in json_data['message']

def test_save_client_error(client):
    """Test saving a client with missing data."""
    data = {
        "name": "Jane Doe",
        "age": 25
        # Missing weight, program, and adherence
    }
    response = client.post('/save_client', json=data)
    assert response.status_code == 500
    json_data = response.get_json()
    assert json_data['status'] == "error"
    assert "message" in json_data

def test_program_data(client):
    """Test that all programs have required fields."""
    response = client.get('/')
    assert response.status_code == 200
    data = response.data.decode('utf-8')
    for program in ["Fat Loss (FL)", "Muscle Gain (MG)", "Beginner (BG)"]:
        assert program in data