import sqlite3
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)
DB_NAME = "aceest_fitness.db"

# Data logic from Aceestver-2.2.1.py
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

@app.route('/save_client', methods=['POST'])
def save_client():
    data = request.json
    weight = float(data.get('weight', 0))
    program = data.get('program')
    calories = int(weight * PROGRAMS.get(program, {"factor": 25})['factor'])

    conn = get_db()
    conn.execute("""
        INSERT INTO clients (name, age, weight, program, calories)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
        age=excluded.age, weight=excluded.weight, program=excluded.program, calories=excluded.calories
    """, (data['name'], data['age'], weight, program, calories))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "calories": calories})

@app.route('/get_progress/<name>')
def get_progress(name):
    conn = get_db()
    cursor = conn.execute("SELECT week, adherence FROM progress WHERE client_name=? ORDER BY id", (name,))
    data = cursor.fetchall()
    conn.close()
    return jsonify([{"week": row["week"], "adherence": row["adherence"]} for row in data])

@app.route('/save_progress', methods=['POST'])
def save_progress():
    data = request.json
    week = datetime.now().strftime("Week %U - %Y")
    conn = get_db()
    conn.execute("INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
                 (data['name'], week, data['adherence']))
    conn.commit()
    conn.close()
    return jsonify({"status": "success"})

if __name__ == '__main__':
    # host='0.0.0.0' is required for Docker connectivity
    app.run(debug=True, host='0.0.0.0', port=5000)