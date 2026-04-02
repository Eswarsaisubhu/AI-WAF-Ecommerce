from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import pickle
from time import time

app = Flask(__name__)
app.secret_key = "secret123"

# ==============================
# GLOBAL USER CONTEXT
# ==============================
@app.context_processor
def inject_user():
    return dict(user=session.get('user'), role=session.get('role'))

# ==============================
# GLOBAL MODES
# ==============================
waf_enabled = False
secure_mode = False

# ==============================
# RATE LIMIT
# ==============================
requests_log = {}

def is_rate_limited(ip):
    now = time()
    requests = requests_log.get(ip, [])
    requests = [r for r in requests if now - r < 10]

    if len(requests) >= 5:
        return True

    requests.append(now)
    requests_log[ip] = requests
    return False

# ==============================
# LOAD ML MODEL
# ==============================
model = None
vectorizer = None

try:
    model = pickle.load(open("model.pkl", "rb"))
    vectorizer = pickle.load(open("vectorizer.pkl", "rb"))
except:
    print("⚠️ ML Model not found")

def ml_detect(text):
    if not model or not vectorizer:
        return False
    try:
        vec = vectorizer.transform([text])
        return model.predict(vec)[0] == 1
    except:
        return False

# ==============================
# DATABASE
# ==============================
def get_db_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="@Subhu4224",
        database="waf_db"
    )

# ==============================
# ATTACK TYPE
# ==============================
def get_attack_type(text):
    text = text.lower()
    if "select" in text or "drop" in text or "' or" in text:
        return "SQL Injection"
    elif "<script>" in text or "alert(" in text:
        return "XSS"
    return "Unknown"

def detect_attack(text):
    patterns = ["' OR '1'='1", "--", "' OR 1=1", "DROP TABLE", "UNION SELECT", "<script>"]
    return any(p.lower() in text.lower() for p in patterns)

# ==============================
# HOME
# ==============================
@app.route('/')
def home():
    return render_template("index.html", waf=waf_enabled, secure=secure_mode)

# ==============================
# TOGGLES
# ==============================
@app.route('/toggle_waf')
def toggle_waf():
    global waf_enabled
    waf_enabled = not waf_enabled
    return redirect(request.referrer or '/')

@app.route('/toggle_mode')
def toggle_mode():
    global secure_mode
    secure_mode = not secure_mode
    return redirect(request.referrer or '/')

# ==============================
# REGISTER
# ==============================
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username,email,password,role) VALUES (%s,%s,%s,%s)",
            (
                request.form['username'],
                request.form['email'],
                generate_password_hash(request.form['password']),
                "user"
            )
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template("register.html")

# ==============================
# LOGIN
# ==============================
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']
        input_text = username + " " + password
        ip = request.remote_addr

        if is_rate_limited(ip):
            return "🚫 Too many requests! Try later."

        conn = get_db_connection()
        cursor = conn.cursor()

        rule = detect_attack(input_text)
        ml = ml_detect(input_text)
        attack_type = get_attack_type(input_text)

        if waf_enabled and (rule or ml):
            cursor.execute(
                "INSERT INTO attacks (input,type,status,ip) VALUES (%s,%s,%s,%s)",
                (input_text, attack_type, "Blocked", ip)
            )
            conn.commit()
            conn.close()
            return "🚫 Attack Blocked!"

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        if user and check_password_hash(user[3], password):
            session['user'] = user[1]
            session['role'] = user[4]

            if user[4] == "admin":
                return redirect('/dashboard')
            return redirect('/')

        return "Invalid Credentials!"

    return render_template("login.html")

# ==============================
# REPORT
# ==============================
@app.route('/report')
def report():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM attacks")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attacks WHERE status='Blocked'")
    blocked = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attacks WHERE status='Allowed'")
    allowed = cursor.fetchone()[0]

    cursor.execute("SELECT type, COUNT(*) FROM attacks GROUP BY type ORDER BY COUNT(*) DESC LIMIT 1")
    result = cursor.fetchone()

    most_common = result[0] if result else "None"

    conn.close()

    blocked_percent = (blocked/total*100) if total else 0
    allowed_percent = (allowed/total*100) if total else 0

    return render_template("report.html",
                           total=total,
                           blocked=blocked,
                           allowed=allowed,
                           blocked_percent=round(blocked_percent,2),
                           allowed_percent=round(allowed_percent,2),
                           most_common=most_common)

# ==============================
# DASHBOARD
# ==============================
@app.route('/dashboard')
def dashboard():
    if session.get('role') != 'admin':
        return "🚫 Admin Only"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM attacks WHERE status='Blocked'")
    blocked = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attacks WHERE status='Allowed'")
    allowed = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM attacks ORDER BY id ASC")
    logs = cursor.fetchall()

    conn.close()

    return render_template("dashboard.html", blocked=blocked, allowed=allowed, logs=logs)

# ==============================
# LOGOUT
# ==============================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app.run(debug=True)