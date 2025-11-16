# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from db import get_db, init_db
import hashlib
import os
from flask import jsonify
from datetime import date
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id, email):
        self.id = id
        self.email = email

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user = db.execute("SELECT id, email FROM users WHERE id = ?", (user_id,)).fetchone()
    return User(user["id"], user["email"]) if user else None

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password)).fetchone()
        if user:
            login_user(User(user['id'], user['email']))
            return redirect(url_for('dashboard'))
        flash("Invalid credentials")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        db = get_db()
        try:
            db.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            db.commit()
            flash("Registered! Log in.")
            return redirect(url_for('login'))
        except:
            flash("Email exists")
    return render_template('register.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', user=current_user)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/log', methods=['GET', 'POST'])
@login_required
def log_session():
    if request.method == 'POST':
        topic = request.form['topic']
        minutes = int(request.form['minutes'])
        log_date = request.form.get('log_date', date.today().isoformat())
        
        db = get_db()
        db.execute(
            "INSERT INTO study_logs (user_id, topic, minutes, log_date) VALUES (?, ?, ?, ?)",
            (current_user.id, topic, minutes, log_date)
        )
        db.commit()
        flash("Session logged!")
        return redirect(url_for('dashboard'))
    
    return render_template('log.html')

@app.route('/api/streak')
@login_required
def api_streak():
    streak = get_streak(current_user.id)
    return jsonify({"streak": streak})

@app.route('/api/logs')
@login_required
def api_logs():
    db = get_db()
    logs = db.execute(
        "SELECT topic, minutes, log_date FROM study_logs WHERE user_id = ? ORDER BY log_date DESC LIMIT 30",
        (current_user.id,)
    ).fetchall()
    return jsonify([dict(log) for log in logs])

if __name__ == '__main__':
    init_db()
    app.run(debug=True)