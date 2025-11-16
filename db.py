# db.py
import sqlite3
from datetime import date
from datetime import datetime, timedelta

DB_NAME = "studystreak.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS study_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            topic TEXT,
            minutes INTEGER,
            log_date TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            goal TEXT,
            created_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT UNIQUE NOT NULL,
            description TEXT,
            lessons_count INTEGER DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS enrollments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            course_id INTEGER,
            enrolled_at TEXT,
            progress_percent INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        );

        CREATE TABLE IF NOT EXISTS quizzes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id INTEGER,
            question TEXT NOT NULL,
            option_a TEXT,
            option_b TEXT,
            option_c TEXT,
            option_d TEXT,
            correct_answer TEXT,
            FOREIGN KEY(course_id) REFERENCES courses(id)
        );

        CREATE TABLE IF NOT EXISTS quiz_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            quiz_id INTEGER,
            score INTEGER,
            completed_at TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(quiz_id) REFERENCES quizzes(id)
        );

        CREATE TABLE IF NOT EXISTS weak_topics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            course_id INTEGER,
            topic TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        );
    ''')
    conn.executescript('''
        INSERT OR IGNORE INTO courses (id, title, description, lessons_count) VALUES
        (1, 'SQL Basics', 'Learn database querying from scratch', 10),
        (2, 'Python Fundamentals', 'Build your first programs', 8),
        (3, 'Machine Learning Intro', 'AI for beginners', 12);

        INSERT OR IGNORE INTO quizzes (id, course_id, question, option_a, option_b, option_c, option_d, correct_answer) VALUES
        (1, 1, 'What does SELECT * FROM users do?', 'Deletes users', 'Shows all users', 'Updates users', 'Inserts users', 'B'),
        (2, 1, 'What is a JOIN?', 'Math operation', 'Combine tables', 'Delete data', 'Sort rows', 'B'),
        (3, 2, 'What is a list in Python?', 'Function', 'Array-like structure', 'String', 'Number', 'B');
    ''')
    conn.commit()
    conn.close()
    print("EdTech DB initialized: courses, quizzes, progress")

def get_streak(user_id):
    db = get_db()
    logs = db.execute(
        "SELECT log_date FROM study_logs WHERE user_id = ? ORDER BY log_date DESC",
        (user_id,)
    ).fetchall()
    
    if not logs:
        return 0
    
    dates = {row["log_date"] for row in logs}
    today = date.today().isoformat()
    streak = 0
    check_date = today
    
    while check_date in dates:
        streak += 1
        check_date = (datetime.fromisoformat(check_date) - timedelta(days=1)).date().isoformat()
    
    return streak