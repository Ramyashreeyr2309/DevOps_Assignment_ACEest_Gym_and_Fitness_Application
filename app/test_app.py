import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client




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

def test_export_csv(client):
    """Test exporting client data as CSV."""
    response = client.get('/export_csv')
    assert response.status_code == 200
    assert response.headers['Content-Type'].startswith("text/csv")  # Allow charset variations
    assert "attachment; filename=clients_export.csv" in response.headers['Content-disposition']
    assert "Name,Age,Weight,Program,Adherence" in response.data.decode('utf-8')
