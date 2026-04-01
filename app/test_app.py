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
            calories INTEGER
        );
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            week TEXT,
            adherence INTEGER,
            FOREIGN KEY(client_name) REFERENCES clients(name)
        );
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT,
            date TEXT,
            workout_type TEXT,
            duration_min INTEGER,
            notes TEXT,
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
        DELETE FROM workouts;
    ''')
    conn.commit()
    conn.close()


def test_save_client(client):
    data = {
        "name": "Jane Doe",
        "age": 25,
        "weight": 60,
        "program": "Beginner (BG)"
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
        "program": "Fat Loss (FL)"
    })

    # Update client
    updated_data = {
        "name": "Alice",
        "age": 29,
        "weight": 68,
        "program": "Muscle Gain (MG)"
    }
    response = client.post('/api/save_client', json=updated_data)
    assert response.status_code == 200
    assert response.get_json()['status'] == "success"

def test_view_history(client):
    # Save a client and workout history
    client.post('/api/save_client', json={
        "name": "Bob",
        "age": 35,
        "weight": 80,
        "program": "Muscle Gain (MG)"
    })
    conn = get_db()
    conn.execute("""
        INSERT INTO workouts (client_name, date, workout_type, duration_min, notes)
        VALUES ('Bob', '2026-03-30', 'Cardio', 30, 'Morning run')
    """)
    conn.commit()
    conn.close()

    # Retrieve workout history
    response = client.get('/history/Bob')
    assert response.status_code == 200
    assert 'Cardio' in response.get_data(as_text=True)

def test_view_history_nonexistent_client(client):
    response = client.get('/history/NonExistent')
    assert response.status_code == 200
    assert 'No history found' in response.get_data(as_text=True)

def test_get_progress(client):
    # Save a client and progress
    client.post('/api/save_client', json={
        "name": "Bob",
        "age": 35,
        "weight": 80,
        "program": "Muscle Gain (MG)"
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