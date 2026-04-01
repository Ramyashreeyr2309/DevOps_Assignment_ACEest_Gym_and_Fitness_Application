import pytest
from app import app, get_db, PROGRAM_FACTORS
import sqlite3
from datetime import datetime

@pytest.fixture(scope='session')
def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS clients (
            name TEXT PRIMARY KEY,
            age INTEGER,
            weight REAL,
            program TEXT,
            calories INTEGER
        );
        CREATE TABLE IF NOT EXISTS progress (
            client_name TEXT,
            week TEXT,
            adherence INTEGER,
            FOREIGN KEY(client_name) REFERENCES clients(name)
        );
    ''')
    conn.commit()
    conn.close()

@pytest.fixture
def client(init_db):
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'
    with app.test_client() as client:
        with app.app_context():
            pass  # Database is already initialized by init_db
        yield client


def test_save_client(client):
    data = {
        "name": "John Doe",
        "age": 30,
        "weight": 70,
        "program": "Fat Loss (FL)"
    }
    response = client.post('/save_client', json=data)
    assert response.status_code == 200
    assert "Client John Doe saved!" in response.get_json()['message']

def test_update_client(client):
    # Save initial client
    data = {
        "name": "Jane Doe",
        "age": 25,
        "weight": 60,
        "program": "Beginner (BG)"
    }
    client.post('/save_client', json=data)

    # Update client
    updated_data = {
        "name": "Jane Doe",
        "age": 26,
        "weight": 62,
        "program": "Muscle Gain (MG)"
    }
    response = client.post('/save_client', json=updated_data)
    assert response.status_code == 200
    assert "Client Jane Doe saved!" in response.get_json()['message']

def test_save_progress(client):
    # Save a client first
    client.post('/save_client', json={
        "name": "Alice",
        "age": 28,
        "weight": 65,
        "program": "Fat Loss (FL)"
    })

    # Save progress for the client
    data = {
        "name": "Alice",
        "adherence": 90
    }
    response = client.post('/save_progress', json=data)
    assert response.status_code == 200
    assert "Weekly progress logged!" in response.get_json()['message']

def test_save_progress_invalid_client(client):
    # Attempt to save progress for a non-existent client
    data = {
        "name": "NonExistent",
        "adherence": 80
    }
    response = client.post('/save_progress', json=data)
    assert response.status_code == 500
    assert "Client does not exist" in response.get_json()['message']