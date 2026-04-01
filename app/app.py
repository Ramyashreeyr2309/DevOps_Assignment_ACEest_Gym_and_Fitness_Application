import sqlite3
import io
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from fpdf import FPDF
import random

app = Flask(__name__)
app.secret_key = "aceest_premium_secret_key"

# --- Authentication Setup ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

class User(UserMixin):
    def __init__(self, id, username, role):
        self.id = id
        self.username = username
        self.role = role

def get_db_connection():
    db_path = app.config.get('DATABASE', 'aceest_fitness.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

@login_manager.user_loader
def load_user(user_id):
    db = get_db_connection()
    user = db.execute("SELECT * FROM users WHERE username = ?", (user_id,)).fetchone()
    if user:
        return User(user['username'], user['username'], user['role'])
    return None

# --- Application Routes ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db_connection()
        user = db.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password)).fetchone()
        if user:
            user_obj = User(user['username'], user['username'], user['role'])
            login_user(user_obj)
            return redirect(url_for('dashboard'))
        flash("Invalid credentials. Access denied.")
    return render_template('login.html')

@app.route('/')
@login_required
def dashboard():
    db = get_db_connection()
    if current_user.role == "Admin":
        clients = db.execute("SELECT * FROM clients").fetchall()
        return render_template('dashboard.html', clients=clients)
    else:
        client = db.execute("SELECT * FROM clients WHERE name = ?", (current_user.username,)).fetchone()
        return render_template('dashboard.html', client=client)

@app.route('/api/generate_workout/<program>')
@login_required
def generate_workout(program):
    # Logic from your AI workout generation method
    exercises = {
        "Fat Loss (FL)": ["Burpees", "Mountain Climbers", "Kettlebell Swings"],
        "Muscle Gain (MG)": ["Bench Press", "Squats", "Deadlifts"]
    }
    selected = exercises.get(program, ["Pushups", "Plank"])
    workout = [{"exercise": ex, "sets": random.randint(3, 5), "reps": random.randint(8, 15)} for ex in selected]
    return jsonify(workout)

@app.route('/export_pdf/<client_name>')
@login_required
def export_pdf(client_name):
    db = get_db_connection()
    row = db.execute("SELECT * FROM clients WHERE name=?", (client_name,)).fetchone()
    
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"ACEest Fitness Report: {client_name}", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Program: {row['program']}", ln=True)
    pdf.cell(0, 10, f"Current Weight: {row['weight']} kg", ln=True)
    
    return send_file(io.BytesIO(pdf.output(dest='S').encode('latin-1')), 
                     download_name=f"{client_name}_report.pdf", as_attachment=True)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)