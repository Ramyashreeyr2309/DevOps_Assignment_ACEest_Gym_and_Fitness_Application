import sqlite3
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)
DB_NAME = "aceest_fitness.db"

# Logic constants from Aceestver-2.2.4.py
PROGRAMS = {
    "Fat Loss (FL)": {"factor": 22},
    "Muscle Gain (MG)": {"factor": 35},
    "Beginner (BG)": {"factor": 26}
}

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html', programs=PROGRAMS.keys())

@app.route('/api/clients', methods=['GET'])
def get_clients():
    db = get_db()
    clients = db.execute("SELECT name, program, target_adherence FROM clients").fetchall()
    return jsonify([dict(row) for row in clients])

@app.route('/api/save_client', methods=['POST'])
def save_client():
    data = request.json
    name = data['name']
    weight = float(data['weight'])
    program = data['program']
    
    # Calculate calories based on your version 2.2.4 logic
    factor = PROGRAMS.get(program, {"factor": 25})['factor']
    calories = int(weight * factor)

    db = get_db()
    db.execute("""
        INSERT INTO clients (name, age, weight, program, calories, target_adherence)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
        weight=excluded.weight, program=excluded.program, calories=excluded.calories
    """, (name, data['age'], weight, program, calories, data['adherence']))
    db.commit()
    return jsonify({"status": "success", "message": f"Saved {name}!"})

@app.route('/api/progress/<name>')
def get_progress(name):
    db = get_db()
    rows = db.execute("SELECT week, adherence FROM progress WHERE client_name=? ORDER BY id", (name,)).fetchall()
    return jsonify([dict(row) for row in rows])

if __name__ == '__main__':
    # host='0.0.0.0' is required for Docker connectivity
    app.run(debug=True, host='0.0.0.0', port=5000)