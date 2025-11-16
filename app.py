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
@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    messages = [{"role": "system", "content": "You are a helpful AI study coach. Use tools when needed."}]
    
    if request.method == 'POST':
        user_msg = request.form['message']
        messages.append({"role": "user", "content": user_msg})
        
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "log_study_session",
                    "description": "Log a study session",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "topic": {"type": "string"},
                            "minutes": {"type": "integer"}
                        },
                        "required": ["topic", "minutes"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_streak_data",
                    "description": "Get current streak",
                    "parameters": {"type": "object", "properties": {}, "required": []}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_study_plan",
                    "description": "Create a study plan",
                    "parameters": {
                        "type": "object",
                        "properties": {"goal": {"type": "string"}},
                        "required": ["goal"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "generate_motivation",
                    "description": "Generate motivation based on streak",
                    "parameters": {"type": "object", "properties": {}, "required": []}
                }
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )

        msg = response.choices[0].message
        messages.append(msg)

        if msg.tool_calls:
            for tool in msg.tool_calls:
                func_name = tool.function.name
                args = json.loads(tool.function.arguments)

                if func_name == "log_study_session":
                    db = get_db()
                    db.execute(
                        "INSERT INTO study_logs (user_id, topic, minutes, log_date) VALUES (?, ?, ?, ?)",
                        (current_user.id, args["topic"], args["minutes"], date.today().isoformat())
                    )
                    db.commit()
                    result = f"Logged {args['minutes']} min of {args['topic']}"

                elif func_name == "get_streak_data":
                    result = f"Current streak: {get_streak(current_user.id)} days"

                elif func_name == "create_study_plan":
                    db = get_db()
                    db.execute(
                        "INSERT INTO study_plans (user_id, goal, created_at) VALUES (?, ?, ?)",
                        (current_user.id, args["goal"], date.today().isoformat())
                    )
                    db.commit()
                    result = f"Plan created: {args['goal']}"

                elif func_name == "generate_motivation":
                    streak = get_streak(current_user.id)
                    result = f"You're on a {streak}-day streak! Keep pushing!"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool.id,
                    "name": func_name,
                    "content": result
                })

            # Final response
            final = client.chat.completions.create(
                model="gpt-4o",
                messages=messages
            )
            bot_reply = final.choices[0].message.content
        else:
            bot_reply = msg.content

        return render_template('chat.html', messages=messages, bot_reply=bot_reply)

    return render_template('chat.html')
if __name__ == '__main__':
    init_db()
    app.run(debug=True)