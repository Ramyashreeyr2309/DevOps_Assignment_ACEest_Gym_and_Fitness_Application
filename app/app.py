import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime

app = Flask(__name__)
DB_NAME = "aceest_fitness.db"

# Core Program Logic from v3.0.1
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
def dashboard():
    db = get_db()
    clients = db.execute("SELECT * FROM clients").fetchall()
    return render_template('index.html', clients=clients, programs=PROGRAMS.keys())

@app.route('/api/save_client', methods=['POST'])
def save_client():
    data = request.json
    weight = float(data['weight'])
    program = data['program']
    calories = int(weight * PROGRAMS.get(program, {"factor": 25})['factor'])

    db = get_db()
    db.execute("""
        INSERT INTO clients (name, age, weight, program, calories)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
        weight=excluded.weight, program=excluded.program, calories=excluded.calories
    """, (data['name'], data['age'], weight, program, calories))
    db.commit()
    return jsonify({"status": "success", "calories": calories})

@app.route('/history/<client_name>')
def view_history(client_name):
    db = get_db()
    # Replicates the Workout History Treeview logic
    history = db.execute("""
        SELECT date, workout_type, duration_min, notes 
        FROM workouts WHERE client_name=? ORDER BY date DESC
    """, (client_name,)).fetchall()
    return render_template('history.html', client=client_name, history=history)

@app.route('/api/progress/<name>')
def get_progress(name):
    db = get_db()
    # Data for the Matplotlib-style chart
    rows = db.execute("SELECT week, adherence FROM progress WHERE client_name=? ORDER BY id", (name,)).fetchall()
    return jsonify([dict(row) for row in rows])

if __name__ == '__main__':
    # host='0.0.0.0' is required for Docker connectivity
    app.run(debug=True, host='0.0.0.0', port=5000)