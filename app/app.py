import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DB_NAME = "aceest_fitness.db"

# Program data from Aceestver2.0.1.py
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
    name = data.get('name')
    age = int(data.get('age', 0))
    weight = float(data.get('weight', 0))
    program = data.get('program')
    
    # Calculate calories using the factor from your logic
    factor = PROGRAMS.get(program, {}).get('factor', 25)
    calories = int(weight * factor)

    try:
        conn = get_db()
        conn.execute("""
            INSERT INTO clients (name, age, weight, program, calories)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
            age=excluded.age, weight=excluded.weight, program=excluded.program, calories=excluded.calories
        """, (name, age, weight, program, calories))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": f"Saved {name} with {calories} kcal/day"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/load_client/<name>')
def load_client(name):
    conn = get_db()
    row = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
    conn.close()
    if row:
        return jsonify(dict(row))
    return jsonify({"error": "Client not found"}), 404

if __name__ == '__main__':
    # host='0.0.0.0' is required for Docker connectivity
    app.run(debug=True, host='0.0.0.0', port=5000)