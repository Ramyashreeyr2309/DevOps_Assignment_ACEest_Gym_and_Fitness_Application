import sqlite3
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
DB_PATH = 'aceest_fitness.db'

# Program data migrated from Aceestver-1.1.py
PROGRAMS = {
    "Fat Loss (FL)": {
        "workout": "Mon: Back Squat 5x5 + Core\nTue: EMOM 20min Assault Bike\nWed: Bench Press + 21-15-9\nThu: Deadlift + Box Jumps\nFri: Zone 2 Cardio 30min",
        "diet": "Breakfast: Egg Whites + Oats\nLunch: Grilled Chicken + Brown Rice\nDinner: Fish Curry + Millet Roti\nTarget: ~2000 kcal",
        "color": "#e74c3c",
        "calorie_factor": 22
    },
    "Muscle Gain (MG)": {
        "workout": "Mon: Squat 5x5\nTue: Bench 5x5\nWed: Deadlift 4x6\nThu: Front Squat 4x8\nFri: Incline Press 4x10\nSat: Barbell Rows 4x10",
        "diet": "Breakfast: Eggs + Peanut Butter Oats\nLunch: Chicken Biryani\nDinner: Mutton Curry + Rice\nTarget: ~3200 kcal",
        "color": "#2ecc71",
        "calorie_factor": 35
    },
    "Beginner (BG)": {
        "workout": "Full Body Circuit:\n- Air Squats\n- Ring Rows\n- Push-ups\nFocus: Technique & Consistency",
        "diet": "Balanced Tamil Meals\nIdli / Dosa / Rice + Dal\nProtein Target: 120g/day",
        "color": "#3498db",
        "calorie_factor": 26
    }
}

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html', programs=PROGRAMS)

@app.route('/save_client', methods=['POST'])
def save_client():
    data = request.json
    try:
        conn = get_db_connection()
        # Inserting into the 'clients' table based on your DB schema 
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

if __name__ == '__main__':
    # host='0.0.0.0' is required for Docker connectivity
    app.run(debug=True, host='0.0.0.0', port=5000)