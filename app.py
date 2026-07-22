from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from datetime import datetime
import json, os, hashlib

app = Flask(__name__)
app.secret_key = "smartexam_major_2025_secure"

# ── STUDENTS ─────────────────────────────────────────────────────────────────
STUDENTS = {
    "SE2025001": {"name": "Urmita Arora",    "password": "SE2025001", "dob": "2005-11-16"},
    "SE2025002": {"name": "Riya Sharma",      "password": "SE2025002", "dob": "2004-05-31"},
    "SE2025003": {"name": "Manjot Kaur",      "password": "SE2025003", "dob": "2003-04-02"},
    "SE2025004": {"name": "Kamalpreet",      "password": "SE2025004", "dob": "2004-12-04"},
    "SE2025005": {"name": "Preyanjal",      "password": "SE2025005", "dob": "2005-11-19"},
    "SE2025006": {"name": "Vinni",          "password": "SE2025006", "dob": "2005-10-21"},
    "SE2025007": {"name": "Sneha Patel",     "password": "SE2025007", "dob": "2003-01-25"},
    "SE2025008": {"name": "Vikram Singh",    "password": "SE2025008", "dob": "2002-12-03"},
    "SE2025009": {"name": "Ananya Reddy",    "password": "SE2025009", "dob": "2003-05-19"},
    "SE2025010": {"name": "Karan Nair",      "password": "SE2025010", "dob": "2002-08-07"},
    "SE2025011": {"name": "Divya Joshi",     "password": "SE2025011", "dob": "2003-03-14"},
    "SE2025012": {"name": "Aditya Kumar",    "password": "SE2025012", "dob": "2002-10-29"},
    "SE2025013": {"name": "Neha Sinha",      "password": "SE2025013", "dob": "2003-08-16"},
    "SE2025014": {"name": "Saurabh Tiwari", "password": "SE2025014", "dob": "2002-07-04"},
    "SE2025015": {"name": "Pooja Mishra",    "password": "SE2025015", "dob": "2003-09-21"},
    "SE2025016": {"name": "Rahul Yadav",     "password": "SE2025016", "dob": "2002-06-11"},
    "SE2025017": {"name": "Simran Bhatia",   "password": "SE2025017", "dob": "2003-12-05"},
    "SE2025018": {"name": "Nikhil Arora",    "password": "SE2025018", "dob": "2002-05-28"},
    "SE2025019": {"name": "Tanya Chopra",    "password": "SE2025019", "dob": "2003-10-17"},
    "SE2025020": {"name": "Gaurav Saxena",   "password": "SE2025020", "dob": "2002-04-09"},
    "SE2025021": {"name": "Ishita Bansal",   "password": "SE2025021", "dob": "2003-11-23"},
    "SE2025022": {"name": "Abhishek Pandey", "password": "SE2025022", "dob": "2002-03-31"},
    "SE2025023": {"name": "Shruti Agarwal",  "password": "SE2025023", "dob": "2003-07-08"},
    "SE2025024": {"name": "Mohit Sharma",    "password": "SE2025024", "dob": "2002-02-14"},
    "SE2025025": {"name": "Kavya Menon",     "password": "SE2025025", "dob": "2003-06-02"},
}

ADMIN = {"username": "admin", "password": "admin123"}

# In-memory stores (replace with DB in production)
exam_attempts = {}   # roll_no -> { score, total, timestamp, violations }
cheating_logs = []   # list of dicts

QUESTIONS = [
    {
        "id": "q1",
        "text": "What data structure follows the LIFO principle?",
        "options": {
            "a": "Queue",
            "b": "Stack",
            "c": "Linked List",
            "d": "Tree"
        },
        "answer": "b"
    },
    {
        "id": "q2",
        "text": "What is the time complexity of Binary Search?",
        "options": {
            "a": "O(n)",
            "b": "O(log n)",
            "c": "O(n²)",
            "d": "O(1)"
        },
        "answer": "b"
    },
    {
        "id": "q3",
        "text": "Which sorting algorithm has average-case complexity O(n log n)?",
        "options": {
            "a": "Bubble Sort",
            "b": "Selection Sort",
            "c": "Merge Sort",
            "d": "Insertion Sort"
        },
        "answer": "c"
    },
    {
        "id": "q4",
        "text": "Which HTML tag is used to create a hyperlink?",
        "options": {
            "a": "<link>",
            "b": "<a>",
            "c": "<href>",
            "d": "<url>"
        },
        "answer": "b"
    },
    {
        "id": "q5",
        "text": "Which CSS property is used to change text color?",
        "options": {
            "a": "font-style",
            "b": "text-color",
            "c": "color",
            "d": "background"
        },
        "answer": "c"
    },
    {
        "id": "q6",
        "text": "Which protocol is mainly used to send emails?",
        "options": {
            "a": "HTTP",
            "b": "SMTP",
            "c": "FTP",
            "d": "TCP"
        },
        "answer": "b"
    },
    {
        "id": "q7",
        "text": "What does IP stand for in networking?",
        "options": {
            "a": "Internet Process",
            "b": "Internal Protocol",
            "c": "Internet Protocol",
            "d": "Integrated Program"
        },
        "answer": "c"
    },
    {
        "id": "q8",
        "text": "Which of the following is an OOP concept?",
        "options": {
            "a": "Compilation",
            "b": "Encapsulation",
            "c": "Linking",
            "d": "Execution"
        },
        "answer": "b"
    },
    {
        "id": "q9",
        "text": "Which file extension is commonly used for CSS files?",
        "options": {
            "a": ".html",
            "b": ".py",
            "c": ".css",
            "d": ".js"
        },
        "answer": "c"
    },
    {
        "id": "q10",
        "text": "Which of these is used for structuring web pages?",
        "options": {
            "a": "CSS",
            "b": "Python",
            "c": "HTML",
            "d": "SQL"
        },
        "answer": "c"
    }
]

# ── HELPERS ───────────────────────────────────────────────────────────────────
def load_logs():
    logs = []
    try:
        with open("cheating_log.txt", "r") as f:
            for line in f:
                line = line.strip()
                if not line: continue
                parts = line.split(" | ")
                if len(parts) >= 3:
                    logs.append({"time": parts[0], "user": parts[1], "event": parts[2]})
                else:
                    logs.append({"time": "", "user": "unknown", "event": line})
    except: pass
    return logs

def write_log(user, event):
    with open("cheating_log.txt", "a") as f:
        f.write(f"{datetime.now()} | {user} | {event}\n")

# ── HOME / LOGIN ──────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def home():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"].strip()
    password = request.form["password"].strip()
    role     = request.form.get("role", "student")

    if role == "admin":
        if username == ADMIN["username"] and password == ADMIN["password"]:
            session["user"] = "admin"
            session["role"] = "admin"
            session["student_name"] = "Administrator"
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin credentials.", "error")
        return redirect(url_for("home"))

    if username in STUDENTS and STUDENTS[username]["password"] == password:
        roll = username
        if roll in exam_attempts:
            flash("You have already attempted this exam. Re-attempts are not allowed.", "error")
            return redirect(url_for("home"))
        session["user"] = roll
        session["role"] = "student"
        session["student_name"] = STUDENTS[roll]["name"]
        return redirect(url_for("dashboard"))

    flash("Invalid credentials. Please try again.", "error")
    return redirect(url_for("home"))

@app.route("/forgot_password", methods=["POST"])
def forgot_password():
    roll_no = request.form["roll_no"].strip().upper()
    dob     = request.form["dob"].strip()
    if roll_no in STUDENTS and STUDENTS[roll_no]["dob"] == dob:
        flash(f"✅ Your password is: {STUDENTS[roll_no]['password']}", "success")
    else:
        flash("❌ Roll number or date of birth does not match.", "error")
    return redirect(url_for("home"))

# ── STUDENT ROUTES ────────────────────────────────────────────────────────────
@app.route("/dashboard")
def dashboard():
    if session.get("role") != "student": return redirect(url_for("home"))
    roll = session["user"]
    attempted = roll in exam_attempts
    result = exam_attempts.get(roll)
    return render_template("student_dashboard.html", attempted=attempted, result=result)

@app.route("/exam")
def exam():
    if session.get("role") != "student": return redirect(url_for("home"))
    roll = session["user"]
    if roll in exam_attempts:
        flash("You have already attempted this exam.", "error")
        return redirect(url_for("dashboard"))
    return render_template("exam.html", questions=QUESTIONS)

@app.route("/submit_exam", methods=["POST"])
def submit_exam():
    if session.get("role") != "student": return redirect(url_for("home"))
    roll = session["user"]
    if roll in exam_attempts:
        return redirect(url_for("dashboard"))

    score = 0
    total = len(QUESTIONS)
    for q in QUESTIONS:
        if request.form.get(q["id"]) == q["answer"]:
            score += 1

    violations = int(request.form.get("violations", 0))
    exam_attempts[roll] = {
        "score": score, "total": total,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "violations": violations,
        "name": STUDENTS[roll]["name"]
    }
    write_log(roll, f"Exam submitted — score {score}/{total}, violations: {violations}")
    return render_template("result.html", score=score, total=total,
                           name=session["student_name"], violations=violations)

# ── ADMIN ROUTES ──────────────────────────────────────────────────────────────
@app.route("/admin")
def admin_dashboard():
    if session.get("role") != "admin": return redirect(url_for("home"))
    logs = load_logs()
    total_students = len(STUDENTS)
    attempted = len(exam_attempts)
    passed = sum(1 for v in exam_attempts.values() if v["score"] >= 5)
    failed = attempted - passed
    avg_score = round(sum(v["score"] for v in exam_attempts.values()) / attempted, 1) if attempted else 0
    violation_count = len(logs)
    return render_template("admin_dashboard.html",
        logs=logs[-50:][::-1],
        results=exam_attempts,
        stats={"total": total_students, "attempted": attempted,
               "passed": passed, "failed": failed,
               "avg_score": avg_score, "violations": violation_count},
        students=STUDENTS
    )

@app.route("/admin/reset/<roll>", methods=["POST"])
def reset_student(roll):
    if session.get("role") != "admin": return jsonify({"error": "Unauthorized"}), 403
    if roll in exam_attempts:
        del exam_attempts[roll]
        write_log("admin", f"Reset exam attempt for {roll}")
    return jsonify({"status": "ok"})

@app.route("/admin/students")
def admin_students():
    if session.get("role") != "admin": return redirect(url_for("home"))
    return render_template("admin_students.html", students=STUDENTS, attempts=exam_attempts)

# ── SHARED ────────────────────────────────────────────────────────────────────
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/log_event", methods=["POST"])
def log_event():
    data  = request.json
    event = data.get("event", "unknown")
    user  = session.get("user", "unknown")
    write_log(user, event)
    return jsonify({"status": "logged"})

@app.route("/api/stats")
def api_stats():
    if session.get("role") != "admin": return jsonify({}), 403
    logs = load_logs()
    events = {}
    for l in logs:
        e = l["event"]
        events[e] = events.get(e, 0) + 1
    return jsonify({"events": events, "total": len(logs)})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
