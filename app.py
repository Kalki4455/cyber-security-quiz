from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

app.secret_key = "secret123"

# =========================
# DATABASE
# =========================

conn = sqlite3.connect("quiz.db")
cursor = conn.cursor()

# USERS TABLE

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

# SCORES TABLE

cursor.execute("""
CREATE TABLE IF NOT EXISTS scores(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    score INTEGER
)
""")

conn.commit()
conn.close()

# =========================
# SIGNUP
# =========================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("quiz.db")
        cursor = conn.cursor()

        try:

            cursor.execute(
                "INSERT INTO users(username, password) VALUES(?, ?)",
                (username, password)
            )

            conn.commit()

            return redirect("/login")

        except:
            return "Username already exists!"

    return render_template("signup.html")

# =========================
# LOGIN
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("quiz.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cursor.fetchone()

        if user:

            session["user"] = username

            return redirect("/")

        else:
            return "Invalid Login!"

    return render_template("login.html")

# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")

# =========================
# HOME
# =========================

@app.route("/", methods=["GET", "POST"])
def home():

    if "user" not in session:
        return redirect("/login")

    score = None

    if request.method == "POST":

        score = 0

        # QUESTION 1

        if request.form.get("q1") == "Time-Based Blind SQL Injection":
            score += 1

        # QUESTION 2

        if request.form.get("q2") == "It encrypts identical plaintext blocks into identical ciphertext blocks":
            score += 1

        # QUESTION 3

        if request.form.get("q3") == "Time-of-Check to Time-of-Use (TOCTOU)":
            score += 1

        # SAVE SCORE

        conn = sqlite3.connect("quiz.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO scores(username, score) VALUES(?, ?)",
            (session["user"], score)
        )

        conn.commit()
        conn.close()

    # LEADERBOARD

    conn = sqlite3.connect("quiz.db")
    cursor = conn.cursor()

    cursor.execute("""
    SELECT username, score
    FROM scores
    ORDER BY score DESC
    LIMIT 5
    """)

    leaderboard = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        score=score,
        leaderboard=leaderboard,
        user=session["user"]
    )

# =========================
# RUN
# =========================

if __name__ == "__main__":
    app.run(debug=True)