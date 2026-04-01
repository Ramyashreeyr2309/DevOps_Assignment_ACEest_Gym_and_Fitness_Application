import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_get_program_valid(client):
    """Test retrieving a valid program."""
    response = client.get('/get_program/Fat Loss (FL)')
    assert response.status_code == 200
    data = response.get_json()
    assert data['workout']
    assert data['diet']

def test_get_program_invalid(client):
    """Test retrieving an invalid program."""
    response = client.get('/get_program/InvalidProgram')
    assert response.status_code == 404
    data = response.get_json()
    assert "error" in data

def test_program_colors(client):
    """Test that each program has a color defined."""
    for program in ['Fat Loss (FL)', 'Muscle Gain (MG)', 'Beginner (BG)']:
        response = client.get(f'/get_program/{program}')
        assert response.status_code == 200
        data = response.get_json()
        assert 'color' in data

def test_program_targets(client):
    """Test that each program has a target calorie value."""
    for program in ['Fat Loss (FL)', 'Muscle Gain (MG)']:
        response = client.get(f'/get_program/{program}')
        assert response.status_code == 200
        data = response.get_json()
        assert 'Target' in data['diet']