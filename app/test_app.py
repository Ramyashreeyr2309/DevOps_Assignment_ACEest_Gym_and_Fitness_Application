import pytest
import sqlite3
import os
import uuid
from app import app

@pytest.fixture
def client():
    # 1. Setup: Create a unique DB for each test to avoid locking/integrity errors
    test_db = f"test_{uuid.uuid4().hex}.db"
    app.config['TESTING'] = True
    app.config['DATABASE'] = test_db
    app.config['SECRET_KEY'] = 'test_secret_key'
    app.config['WTF_CSRF_ENABLED'] = False # Disabling CSRF for easier testing

    # 2. Initialize the schema
    conn = sqlite3.connect(test_db)
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT,
            role TEXT
        );
        CREATE TABLE IF NOT EXISTS clients (
            name TEXT PRIMARY KEY,
            age INTEGER,
            weight REAL,
            program TEXT
        );
    ''')
    conn.commit()
    conn.close()

    with app.test_client() as client:
        yield client

    # 3. Teardown: Clean up the temporary database file
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except PermissionError:
            pass # Handle Windows file locking delays

def test_login_success(client):
    # Insert test user
    db_path = app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "password", "Admin"))
    conn.commit()
    conn.close()

    # Perform actual login to establish session context
    response = client.post('/login', data={"username": "admin", "password": "password"}, follow_redirects=True)
    assert response.status_code == 200
    assert b"Dashboard" in response.data # Check if we reached the dashboard

def test_dashboard_admin(client):
    db_path = app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "password", "Admin"))
    conn.commit()
    conn.close()

    # Use the client to log in properly
    client.post('/login', data={"username": "admin", "password": "password"})
    
    response = client.get('/')
    assert response.status_code == 200


def test_export_pdf(client):
    db_path = app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("client1", "password", "Client"))
    conn.execute("INSERT INTO clients (name, age, weight, program) VALUES (?, ?, ?, ?)", ("client1", 30, 70, "Fat Loss (FL)"))
    conn.commit()
    conn.close()

    client.post('/login', data={"username": "client1", "password": "password"})

    response = client.get('/export_pdf/client1')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/pdf'

def test_logout(client):
    db_path = app.config['DATABASE']
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", ("admin", "password", "Admin"))
    conn.commit()
    conn.close()

    client.post('/login', data={"username": "admin", "password": "password"})
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b"login" in response.data.lower()