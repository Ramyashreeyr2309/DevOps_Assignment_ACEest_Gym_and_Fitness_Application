import pytest
from app import app, get_db, PROGRAMS
import sqlite3
from unittest.mock import patch
from flask import g

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
    assert "Saved John Doe with" in response.get_json()['message']

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
    assert "Saved Jane Doe with" in response.get_json()['message']

def test_load_client(client):
    # Save a client
    data = {
        "name": "Alice",
        "age": 28,
        "weight": 65,
        "program": "Fat Loss (FL)"
    }
    client.post('/save_client', json=data)

    # Load the client
    response = client.get('/load_client/Alice')
    assert response.status_code == 200
    client_data = response.get_json()
    assert client_data['name'] == "Alice"
    assert client_data['age'] == 28
    assert client_data['weight'] == 65
    assert client_data['program'] == "Fat Loss (FL)"

def test_load_nonexistent_client(client):
    response = client.get('/load_client/NonExistent')
    assert response.status_code == 404
    assert "Client not found" in response.get_json()['error']