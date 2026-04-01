import pytest
import sqlite3
import os
import uuid
from app import app

@pytest.fixture
def client():
    """
    Creates a fresh, unique database for every single test 
    to prevent locks and integrity errors.
    """
    # 1. Setup: Create a unique DB name for this specific test
    test_db = f"test_{uuid.uuid4().hex}.db"
    app.config['TESTING'] = True
    app.config['DATABASE'] = test_db
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['WTF_CSRF_ENABLED'] = False

    # 2. Initialize the schema
    conn = sqlite3.connect(test_db)
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT
        );
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE,
            age INTEGER,
            height REAL,
            weight REAL,
            program TEXT,
            calories INTEGER,
            target_weight REAL,
            target_adherence INTEGER,
            membership_status TEXT,
            membership_end TEXT
        );
    ''')
    conn.commit()
    conn.close()

    # 3. Yield the test client
    with app.test_client() as client:
        yield client

    # 4. Teardown: Remove the unique DB file after the test finishes
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except PermissionError:
            pass # Windows occasionally holds a lock for a few ms

def test_login_success(client):
    # Setup user
    db_path = app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                 ("admin", "password", "Admin"))
    conn.commit()
    conn.close()

    response = client.post('/login', data={'username': 'admin', 'password': 'password'}, follow_redirects=True)
    assert response.status_code == 200
    # Check for dashboard content
    assert b"Dashboard" in response.data or b"Clients" in response.data

def test_invalid_login(client):
    response = client.post('/login', data={'username': 'wrong', 'password': 'wrong'}, follow_redirects=True)
    assert b"Access Denied" in response.data

def test_dashboard_admin(client):
    # Setup
    db_path = app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "password", "Admin"))
    conn.execute("INSERT INTO clients (name, age, height, weight, program) VALUES (?, ?, ?, ?, ?)", 
                 ("Test Client", 30, 175, 80, "Fat Loss (FL)"))
    conn.commit()
    conn.close()

    # Login
    client.post('/login', data={'username': 'admin', 'password': 'password'})
    
    # Access Dashboard
    response = client.get('/')
    assert response.status_code == 200
    assert b"Test Client" in response.data

def test_generate_workout(client):
    # Setup user
    db_path = app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("user1", "pass", "Client"))
    conn.commit()
    conn.close()

    client.post('/login', data={'username': 'user1', 'password': 'pass'})
    
    # Test valid program
    response = client.get('/api/generate_workout/Fat Loss (FL)')
    assert response.status_code == 200
    assert b"name" in response.data


def test_add_client(client):
    db_path = app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "password", "Admin"))
    conn.commit()
    conn.close()

    client.post('/login', data={'username': 'admin', 'password': 'password'})
    
    payload = {
        "name": "New Client", "age": 25, "height": 180, "weight": 75, "program": "Muscle Gain (MG)",
        "calories": 2500, "target_weight": 80, "target_adherence": 95,
        "membership_status": "Active", "membership_end": "2025-01-01"
    }
    response = client.post('/clients', json=payload)
    assert response.status_code == 201
    assert b"Client added successfully" in response.data

def test_duplicate_client_addition(client):
    db_path = app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "password", "Admin"))
    conn.execute("INSERT INTO clients (name, age) VALUES (?, ?)", ("Duplicate", 30))
    conn.commit()
    conn.close()

    client.post('/login', data={'username': 'admin', 'password': 'password'})
    
    payload = {"name": "Duplicate", "age": 30} # Rest of fields omitted for brevity
    response = client.post('/clients', json=payload)
    assert response.status_code == 400

def test_logout(client):
    db_path = app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "password", "Admin"))
    conn.commit()
    conn.close()

    client.post('/login', data={'username': 'admin', 'password': 'password'})
    response = client.get('/logout', follow_redirects=True)
    assert b"login" in response.data or response.status_code == 200

    #tested completely