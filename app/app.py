import sqlite3
import csv
import io
from flask import Flask, render_template, jsonify, request, Response

app = Flask(__name__)
DB_PATH = 'aceest_fitness.db'

# Data Store from Aceestver1.1.2.py 
PROGRAMS = {
    "Fat Loss (FL)": {"workout": "Back Squat, Cardio, Bench, Deadlift, Recovery",
                      "diet": "Egg Whites, Chicken, Fish Curry",
                      "color": "#e74c3c", "calorie_factor": 22},
    "Muscle Gain (MG)": {"workout": "Squat, Bench, Deadlift, Press, Rows",
                         "diet": "Eggs, Biryani, Mutton Curry",
                         "color": "#2ecc71", "calorie_factor": 35},
    "Beginner (BG)": {"workout": "Air Squats, Ring Rows, Push-ups",
                      "diet": "Balanced Tamil Meals",
                      "color": "#3498db", "calorie_factor": 26}
}

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    clients = conn.execute('SELECT * FROM clients').fetchall()
    conn.close()
    return render_template('index.html', programs=PROGRAMS, clients=clients)

@app.route('/save_client', methods=['POST'])
def save_client():
    data = request.json
    try:
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO clients (name, age, weight, program, target_adherence)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
            age=excluded.age, weight=excluded.weight, program=excluded.program, target_adherence=excluded.target_adherence
        ''', (data['name'], data['age'], data['weight'], data['program'], data['adherence']))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": f"Client {data['name']} saved!"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/export_csv')
def export_csv():
    conn = get_db_connection()
    clients = conn.execute('SELECT name, age, weight, program, target_adherence FROM clients').fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Age", "Weight", "Program", "Adherence"])
    for row in clients:
        writer.writerow(list(row))
    
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=clients_export.csv"}
    )

if __name__ == '__main__':
    # host='0.0.0.0' is required for Docker connectivity
    app.run(debug=True, host='0.0.0.0', port=5000)