import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import random
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = "aceest_ultra_premium_key"

# --- AUTHENTICATION CONFIG ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, username, role):
        self.id = username
        self.username = username
        self.role = role

def get_db():
    db_path = app.config.get('DATABASE', 'aceest_fitness.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@login_manager.user_loader
def load_user(username):
    db = get_db()
    user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if user:
        return User(user['username'], user['role'])
    return None

# --- CORE ROUTES ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        if user:
            login_user(User(user['username'], user['role']))
            return redirect(url_for('dashboard'))
        flash("Access Denied: Invalid Credentials")
    return render_template('login.html')

@app.route('/')
@login_required
def dashboard():
    db = get_db()
    if current_user.role == "Admin":
        data = db.execute("SELECT * FROM clients").fetchall()
    else:
        data = db.execute("SELECT * FROM clients WHERE name = ?", (current_user.username,)).fetchall()
    return render_template('dashboard.html', clients=data)

# --- AI WORKOUT GENERATOR (v3.2.4 Logic) ---
@app.route('/api/generate_workout/<program>')
@login_required
def ai_workout(program):
    # Replicates the random workout generation from your code
    pools = {
        "Fat Loss (FL)": ["Burpees", "Thrusters", "Box Jumps", "Sprints"],
        "Muscle Gain (MG)": ["Bench Press", "Squats", "Deadlifts", "Rows"]
    }
    exercises = pools.get(program, ["Pushups", "Plank", "Lunges"])
    workout = []
    for ex in random.sample(exercises, min(len(exercises), 3)):
        workout.append({
            "name": ex,
            "sets": random.randint(3, 5),
            "reps": random.randint(8, 12)
        })
    return jsonify(workout)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- DATABASE INITIALIZATION ROUTE ---
@app.route('/init_db')
def init_db():
    db = get_db()
    cur = db.cursor()

    # Users (for role-based login)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT
    )
    """)

    # Clients
    cur.execute("""
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
    )
    """)

    # Progress
    cur.execute("""
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        week TEXT,
        adherence INTEGER
    )
    """)

    # Workouts
    cur.execute("""
    CREATE TABLE IF NOT EXISTS workouts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        date TEXT,
        workout_type TEXT,
        duration_min INTEGER,
        notes TEXT
    )
    """)

    # Exercises
    cur.execute("""
    CREATE TABLE IF NOT EXISTS exercises (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        workout_id INTEGER,
        name TEXT,
        sets INTEGER,
        reps INTEGER,
        weight REAL
    )
    """)

    # Metrics
    cur.execute("""
    CREATE TABLE IF NOT EXISTS metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_name TEXT,
        date TEXT,
        weight REAL,
        waist REAL,
        bodyfat REAL
    )
    """)

    # Add default admin if not exists
    cur.execute("SELECT * FROM users WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users VALUES ('admin','admin','Admin')")

    db.commit()
    db.close()
    return "Database initialized successfully!"

# --- CLIENT MANAGEMENT ROUTES ---
@app.route('/clients', methods=['GET'])
@login_required
def get_clients():
    db = get_db()
    clients = db.execute("SELECT * FROM clients").fetchall()
    return jsonify([dict(client) for client in clients])

@app.route('/clients', methods=['POST'])
@login_required
def add_client():
    data = request.json
    db = get_db()
    try:
        db.execute(
            """
            INSERT INTO clients (name, age, height, weight, program, calories, target_weight, target_adherence, membership_status, membership_end)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data['name'], data['age'], data['height'], data['weight'], data['program'],
                data['calories'], data['target_weight'], data['target_adherence'],
                data['membership_status'], data['membership_end']
            )
        )
        db.commit()
        return jsonify({"message": "Client added successfully!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/clients/<name>', methods=['GET'])
@login_required
def load_client(name):
    db = get_db()
    client = db.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
    if client:
        return jsonify(dict(client))
    return jsonify({"error": "Client not found"}), 404

# --- AI PROGRAM GENERATOR ROUTE ---
@app.route('/clients/<name>/generate_program', methods=['POST'])
@login_required
def generate_program(name):
    db = get_db()
    client = db.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
    if not client:
        return jsonify({"error": "Client not found"}), 404

    program_templates = {
        "Fat Loss": ["Full Body HIIT", "Circuit Training", "Cardio + Weights"],
        "Muscle Gain": ["Push/Pull/Legs", "Upper/Lower Split", "Full Body Strength"],
        "Beginner": ["Full Body 3x/week", "Light Strength + Mobility"]
    }

    program_type = random.choice(list(program_templates.keys()))
    program_detail = random.choice(program_templates[program_type])

    db.execute("UPDATE clients SET program = ? WHERE name = ?", (program_detail, name))
    db.commit()

    return jsonify({"message": f"Program generated for {name}: {program_detail}", "program": program_detail})

# --- MEMBERSHIP MANAGEMENT ROUTE ---
@app.route('/clients/<name>/membership', methods=['GET'])
@login_required
def check_membership(name):
    db = get_db()
    client = db.execute("SELECT membership_status, membership_end FROM clients WHERE name = ?", (name,)).fetchone()
    if not client:
        return jsonify({"error": "Client not found"}), 404

    status, end = client["membership_status"], client["membership_end"]
    return jsonify({"membership_status": status, "membership_end": end if end else "N/A"})

# --- PDF REPORT GENERATION ROUTE ---
@app.route('/clients/<name>/generate_pdf', methods=['GET'])
@login_required
def generate_pdf(name):
    db = get_db()
    client = db.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
    if not client:
        return jsonify({"error": "Client not found"}), 404

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"ACEest Client Report - {name}", ln=True)

    columns = ["ID", "Name", "Age", "Height", "Weight", "Program", "Calories", "Target Weight", "Target Adherence", "Membership", "End"]
    pdf.set_font("Arial", "", 12)
    for i, col in enumerate(columns):
        pdf.cell(0, 10, f"{col}: {client[i]}", ln=True)

    file_path = f"{name}_report.pdf"
    pdf.output(file_path)

    return jsonify({"message": f"PDF report generated: {file_path}", "file": file_path})

# --- CLIENT SUMMARY ROUTE ---
@app.route('/clients/<name>/summary', methods=['GET'])
@login_required
def get_summary(name):
    db = get_db()
    client = db.execute("SELECT * FROM clients WHERE name = ?", (name,)).fetchone()
    if not client:
        return jsonify({"error": "Client not found"}), 404

    summary = {
        "name": client["name"],
        "program": client["program"],
        "calories": client["calories"],
        "membership_status": client["membership_status"]
    }
    return jsonify(summary)

# --- ADHERENCE CHART DATA ROUTE ---
@app.route('/clients/<name>/adherence', methods=['GET'])
@login_required
def get_adherence_data(name):
    db = get_db()
    data = db.execute("SELECT week, adherence FROM progress WHERE client_name = ? ORDER BY id", (name,)).fetchall()
    if not data:
        return jsonify({"error": "No adherence data found"}), 404

    adherence_data = {"weeks": [d["week"] for d in data], "adherence": [d["adherence"] for d in data]}
    return jsonify(adherence_data)

# --- WORKOUT MANAGEMENT ROUTES ---
@app.route('/clients/<name>/workouts', methods=['GET'])
@login_required
def get_workouts(name):
    db = get_db()
    workouts = db.execute("SELECT * FROM workouts WHERE client_name = ? ORDER BY date DESC", (name,)).fetchall()
    return jsonify([{
        "date": workout["date"],
        "workout_type": workout["workout_type"],
        "duration_min": workout["duration_min"],
        "notes": workout["notes"]
    } for workout in workouts])

@app.route('/clients/<name>/workouts', methods=['POST'])
@login_required
def add_workout(name):
    data = request.json
    workout_type = data.get("workout_type")
    duration_min = data.get("duration_min")
    notes = data.get("notes", "")

    if not workout_type or not duration_min:
        return jsonify({"error": "Workout type and duration are required"}), 400

    db = get_db()
    db.execute("INSERT INTO workouts (client_name, date, workout_type, duration_min, notes) VALUES (?, DATE('now'), ?, ?, ?)",
               (name, workout_type, duration_min, notes))
    db.commit()
    return jsonify({"message": "Workout added successfully"})

@app.route('/test')
def test():
    return "Test route is working!"

@app.route('/routes')
def list_routes():
    import urllib
    output = []
    for rule in app.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote(f"{rule.endpoint}: {rule.rule} ({methods})")
        output.append(line)
    return '<br>'.join(output)

if __name__ == '__main__':
    # host='0.0.0.0' is required for Docker connectivity
    app.run(debug=True, host='0.0.0.0', port=5000)