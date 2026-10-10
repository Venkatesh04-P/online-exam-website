import os
import sqlite3
import time
import secrets
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, abort, flash

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "exam.db")

app = Flask(__name__)
app.secret_key = os.environ.get("EXAM_SECRET_KEY", "replace-this-with-a-long-random-secret")
EXAM_DURATION_MINUTES = 15

QUESTIONS = [
    {
        "question": "Which language is primarily used to structure web pages?",
        "options": ["Python", "HTML", "SQL", "Java"],
        "answer": 1
    },
    {
        "question": "Which keyword defines a function in Python?",
        "options": ["func", "define", "def", "function"],
        "answer": 2
    },
    {
        "question": "Which CSS property changes text color?",
        "options": ["font-style", "background", "color", "text-size"],
        "answer": 2
    },
    {
        "question": "What does SQL help you manage?",
        "options": ["Databases", "Images only", "Computer hardware", "Web browsers"],
        "answer": 0
    },
    {
        "question": "Which HTML element creates a hyperlink?",
        "options": ["<p>", "<a>", "<h1>", "<img>"],
        "answer": 1
    },
    {
        "question": "Which of these is a JavaScript data type?",
        "options": ["boolean", "paragraph", "stylesheet", "database-table"],
        "answer": 0
    },
    {
        "question": "What is the result of 5 * 3 in Python?",
        "options": ["8", "15", "53", "2"],
        "answer": 1
    },
    {
        "question": "Which HTTP method is commonly used to submit a form?",
        "options": ["POST", "PAINT", "MOVE", "SHOW"],
        "answer": 0
    },
    {
        "question": "Which Flask function renders an HTML template?",
        "options": ["render_template", "open_html", "show_page", "template_file"],
        "answer": 0
    },
    {
        "question": "Which database is included in Python's standard library?",
        "options": ["MongoDB", "SQLite", "Oracle Database", "Redis"],
        "answer": 1
    }
]


def connect_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with connect_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                attempt_token TEXT NOT NULL UNIQUE,
                student_name TEXT NOT NULL,
                student_id TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL,
                started_at TEXT NOT NULL,
                submitted_at TEXT NOT NULL
            )
        """)


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("student_name", "").strip()
        student_id = request.form.get("student_id", "").strip()

        if not name or not student_id:
            flash("Please enter both your name and student ID.", "error")
            return render_template("index.html")

        if len(name) > 80 or len(student_id) > 40:
            flash("Name or student ID is too long.", "error")
            return render_template("index.html")

        session.clear()
        token = secrets.token_urlsafe(24)
        session["attempt_token"] = token
        session["student_name"] = name
        session["student_id"] = student_id
        session["started_at"] = time.time()
        session["submitted"] = False
        session["answers"] = {}
        return redirect(url_for("instructions"))

    return render_template("index.html")


@app.route("/instructions")
def instructions():
    if not session.get("attempt_token") or session.get("submitted"):
        return redirect(url_for("home"))
    return render_template(
        "instructions.html",
        name=session.get("student_name"),
        count=len(QUESTIONS),
        duration=EXAM_DURATION_MINUTES
    )


@app.route("/start")
def start_exam():
    if not session.get("attempt_token") or session.get("submitted"):
        return redirect(url_for("home"))
    session["started_at"] = time.time()
    session["exam_started"] = True
    return redirect(url_for("exam"))


@app.route("/exam")
def exam():
    if not session.get("attempt_token") or session.get("submitted"):
        return redirect(url_for("home"))
    if not session.get("exam_started"):
        return redirect(url_for("instructions"))

    elapsed = time.time() - session.get("started_at", time.time())
    remaining = max(0, EXAM_DURATION_MINUTES * 60 - int(elapsed))
    if remaining <= 0:
        return redirect(url_for("submit_exam"))

    safe_questions = [
        {"id": i, "question": q["question"], "options": q["options"]}
        for i, q in enumerate(QUESTIONS)
    ]
    return render_template("exam.html", questions=safe_questions, remaining=remaining)


@app.route("/submit", methods=["POST"])
def submit_exam():
    token = session.get("attempt_token")
    if not token:
        return redirect(url_for("home"))

    if session.get("submitted"):
        return redirect(url_for("result"))

    raw_answers = request.form if request.method == "POST" else {}
    answers = {}
    score = 0

    # Only accept question indexes and option indexes that exist on the server.
    for i, q in enumerate(QUESTIONS):
        selected = raw_answers.get(f"q{i}")
        try:
            selected_index = int(selected) if selected is not None else None
        except (TypeError, ValueError):
            selected_index = None
        if selected_index is not None and 0 <= selected_index < len(q["options"]):
            answers[str(i)] = selected_index
            if selected_index == q["answer"]:
                score += 1

    # Prevent a repeated submission from creating another result.
    with connect_db() as db:
        db.execute("""
            INSERT OR IGNORE INTO results
            (attempt_token, student_name, student_id, score, total, started_at, submitted_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            token,
            session.get("student_name", "Student"),
            session.get("student_id", "Unknown"),
            score,
            len(QUESTIONS),
            datetime.fromtimestamp(session.get("started_at", time.time())).isoformat(timespec="seconds"),
            datetime.now().isoformat(timespec="seconds")
        ))

    session["submitted"] = True
    session["score"] = score
    session["total"] = len(QUESTIONS)
    session["answers"] = answers
    return redirect(url_for("result"))


@app.route("/result")
def result():
    if not session.get("submitted"):
        return redirect(url_for("home"))
    return render_template(
        "result.html",
        name=session.get("student_name", "Student"),
        student_id=session.get("student_id", ""),
        score=session.get("score", 0),
        total=session.get("total", len(QUESTIONS)),
        percentage=round(session.get("score", 0) * 100 / max(1, session.get("total", len(QUESTIONS))))
    )


@app.route("/admin/results")
def admin_results():
    # Demo-only view. Add real administrator authentication before deploying.
    with connect_db() as db:
        rows = db.execute(
            "SELECT student_name, student_id, score, total, started_at, submitted_at "
            "FROM results ORDER BY id DESC"
        ).fetchall()
    return render_template("admin_results.html", rows=rows)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
