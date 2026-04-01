import pytest
from app import app, get_db, PROGRAMS
import sqlite3
from datetime import datetime

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'
    with app.test_client() as client:
        with app.app_context():
            init_db()
        yield client
        clear_db()

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS clients (
            name TEXT PRIMARY KEY,
            age INTEGER,
            weight REAL,
            program TEXT,
            calories INTEGER,
            target_adherence INTEGER
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

def clear_db():
    conn = get_db()
    conn.executescript('''
        DELETE FROM clients;
        DELETE FROM progress;
    ''')
    conn.commit()
    conn.close()


def test_get_clients_empty(client):
    response = client.get('/api/clients')
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_clients_with_data(client):
    conn = get_db()
    conn.execute("""
        INSERT INTO clients (name, age, weight, program, calories, target_adherence)
        VALUES ('John Doe', 30, 70, 'Fat Loss (FL)', 1540, 90)
    """)
    conn.commit()
    conn.close()

    response = client.get('/api/clients')
    assert response.status_code == 200
    clients = response.get_json()
    assert len(clients) == 1
    assert clients[0]['name'] == 'John Doe'

def test_save_client(client):
    data = {
        "name": "Jane Doe",
        "age": 25,
        "weight": 60,
        "program": "Beginner (BG)",
        "adherence": 85
    }
    response = client.post('/api/save_client', json=data)
    assert response.status_code == 200
    assert response.get_json()['status'] == "success"

def test_update_client(client):
    # Save initial client
    client.post('/api/save_client', json={
        "name": "Alice",
        "age": 28,
        "weight": 65,
        "program": "Fat Loss (FL)",
        "adherence": 90
    })

    # Update client
    updated_data = {
        "name": "Alice",
        "age": 29,
        "weight": 68,
        "program": "Muscle Gain (MG)",
        "adherence": 95
    }
    response = client.post('/api/save_client', json=updated_data)
    assert response.status_code == 200
    assert response.get_json()['status'] == "success"

def test_get_progress(client):
    # Save a client and progress
    client.post('/api/save_client', json={
        "name": "Bob",
        "age": 35,
        "weight": 80,
        "program": "Muscle Gain (MG)",
        "adherence": 85
    })
    conn = get_db()
    conn.execute("""
        INSERT INTO progress (client_name, week, adherence)
        VALUES ('Bob', 'Week 13 - 2026', 85)
    """)
    conn.commit()
    conn.close()

    # Retrieve progress
    response = client.get('/api/progress/Bob')
    assert response.status_code == 200
    progress = response.get_json()
    assert len(progress) == 1
    assert progress[0]['adherence'] == 85

def test_get_progress_nonexistent_client(client):
    response = client.get('/api/progress/NonExistent')
    assert response.status_code == 200
    assert response.get_json() == []