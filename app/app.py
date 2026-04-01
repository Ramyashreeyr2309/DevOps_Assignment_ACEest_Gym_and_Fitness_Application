import sqlite3
from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)
DB_NAME = "aceest_fitness.db"

# Data factors from your v2.1.2 script
PROGRAM_FACTORS = {
    "Fat Loss (FL)": 22,
    "Muscle Gain (MG)": 35,
    "Beginner (BG)": 26
}

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html', programs=PROGRAM_FACTORS.keys())

@app.route('/save_client', methods=['POST'])
def save_client():
    data = request.json
    name = data.get('name')
    weight = float(data.get('weight', 0))
    program = data.get('program')
    
    # Logic from your save_data method
    factor = PROGRAM_FACTORS.get(program, 25)
    calories = int(weight * factor)

    conn = get_db()
    try:
        conn.execute("""
            INSERT INTO clients (name, age, weight, program, calories)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
            age=excluded.age, weight=excluded.weight, program=excluded.program, calories=excluded.calories
        """, (name, data.get('age'), weight, program, calories))
        conn.commit()
        return jsonify({"status": "success", "message": f"Client {name} saved!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})
    finally:
        conn.close()

@app.route('/save_progress', methods=['POST'])
def save_progress():
    data = request.json
    week = datetime.now().strftime("Week %U - %Y")
    
    conn = get_db()
    try:
        # Check if the client exists
        client = conn.execute("SELECT name FROM clients WHERE name = ?", (data.get('name'),)).fetchone()
        if not client:
            return jsonify({"status": "error", "message": "Client does not exist"}), 500

        conn.execute("""
            INSERT INTO progress (client_name, week, adherence)
            VALUES (?, ?, ?)
        """, (data.get('name'), week, data.get('adherence')))
        conn.commit()
        return jsonify({"status": "success", "message": "Weekly progress logged!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    # host='0.0.0.0' is required for Docker connectivity
    app.run(debug=True, host='0.0.0.0', port=5000)