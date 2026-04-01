import pytest
from app import app, get_db, PROGRAMS
import sqlite3
from datetime import datetime
from unittest.mock import patch
import flask_login 

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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            with patch('flask_login.current_user') as mock_current_user:
                mock_current_user.is_authenticated = True
                mock_current_user.name = "Test User"
            yield client

@pytest.fixture(autouse=True)
def clear_db():
    conn = get_db()
    conn.executescript('''
        DELETE FROM clients;
        DELETE FROM progress;
    ''')
    conn.commit()
    conn.close()


def test_save_client(client):
    data = {
        "name": "John Doe",
        "age": 30,
        "weight": 70,
        "program": "Fat Loss (FL)"
    }
    response = client.post('/save_client', json=data)
    assert response.status_code == 200
    assert response.get_json()['status'] == "success"
    assert response.get_json()['calories'] == 1540

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
    assert response.get_json()['status'] == "success"
    assert response.get_json()['calories'] == 2170

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
    assert response.get_json()['status'] == "success"

def test_get_progress(client):
    # Save a client and progress
    client.post('/save_client', json={
        "name": "Bob",
        "age": 35,
        "weight": 80,
        "program": "Muscle Gain (MG)"
    })
    client.post('/save_progress', json={
        "name": "Bob",
        "adherence": 85
    })

    # Retrieve progress
    response = client.get('/get_progress/Bob')
    assert response.status_code == 200
    progress = response.get_json()
    assert len(progress) == 1
    assert progress[0]['adherence'] == 85

def test_get_progress_nonexistent_client(client):
    response = client.get('/get_progress/NonExistent')
    assert response.status_code == 200
    assert response.get_json() == []