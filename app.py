from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import pickle
from time import time

app = Flask(__name__)
app.secret_key = "secret123"
@app.context_processor
def inject_user():
    return dict(
        user=session.get('user'),
        role=session.get('role')
    )

# ==============================
# GLOBAL MODES
# ==============================
waf_enabled = False
secure_mode = False

# ==============================
# RATE LIMIT 🔥
# ==============================
requests_log = {}

def is_rate_limited(ip):
    now = time()
    requests = requests_log.get(ip, [])

    # keep only last 10 seconds
    requests = [r for r in requests if now - r < 10]

    if len(requests) >= 5:   # FIXED (>= instead of >)
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
    print("✅ ML Model Loaded")
except:
    print("⚠️ ML Model not found")

def ml_detect(text):
    if not model or not vectorizer:
        return False
    try:
        vec = vectorizer.transform([text])
        prediction = model.predict(vec)
        return prediction[0] == 1
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
# ATTACK TYPE DETECTION
# ==============================
def get_attack_type(text):
    text = text.lower()

    if "select" in text or "drop" in text or "' or" in text:
        return "SQL Injection"
    elif "<script>" in text or "alert(" in text:
        return "XSS"
    else:
        return "Unknown"

# ==============================
# RULE DETECTION
# ==============================
def detect_attack(text):
    patterns = ["' OR '1'='1", "--", "' OR 1=1", "DROP TABLE", "UNION SELECT", "<script>"]
    return any(p.lower() in text.lower() for p in patterns)

# ==============================
# PRODUCTS
# ==============================
products = [
    {"id":1,"name":"Ravens Oversized Street Tee","price":1299,"image":"tee.jpg"},
    {"id":2,"name":"Ravens Urban Black Hoodie","price":2499,"image":"hoodie.jpg"},
    {"id":3,"name":"Ravens Vintage Denim Jacket","price":3999,"image":"jacket.jpg"},
    {"id":4,"name":"Ravens Slim Fit Street Jeans","price":2799,"image":"jeans.jpg"},
    {"id":5,"name":"Ravens Summer Graphic Tee","price":999,"image":"tee2.jpg"},
    {"id":6,"name":"Ravens Minimal White Hoodie","price":2299,"image":"hoodie2.jpg"}
]

# ==============================
# HOME
# ==============================
@app.route('/')
def home():
    return render_template("index.html", products=products, waf=waf_enabled, secure=secure_mode)

# ==============================
# TOGGLE WAF 🔥
# ==============================
@app.route('/toggle_waf')
def toggle_waf():
    global waf_enabled
    waf_enabled = not waf_enabled
    return redirect(request.referrer or url_for('home'))


# ==============================
# TOGGLE MODE 🔥
# ==============================
@app.route('/toggle_mode')
def toggle_mode():
    global secure_mode
    secure_mode = not secure_mode
    return redirect(request.referrer or url_for('home'))

# ==============================
# REGISTER
# ==============================
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
            (username, email, password, "user")
        )

        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template("register.html", waf=waf_enabled, secure=secure_mode)

# ==============================
# LOGIN
# ==============================
@app.route('/login', methods=['GET','POST'])
def login():
    global waf_enabled, secure_mode

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        input_text = username + " " + password

        ip = request.headers.get('X-Forwarded-For', request.remote_addr)

        if is_rate_limited(ip):
            return "🚫 Too many requests! Try later."

        conn = get_db_connection()
        cursor = conn.cursor()

        rule_attack = detect_attack(input_text)
        ml_attack = ml_detect(input_text)
        attack_type = get_attack_type(input_text)

        # BLOCK ATTACK
        if waf_enabled and (rule_attack or ml_attack):
            cursor.execute(
                "INSERT INTO attacks (input, type, status, ip) VALUES (%s, %s, %s, %s)",
                (input_text, attack_type, "Blocked", ip)
            )
            conn.commit()
            conn.close()
            return "🚫 Attack Blocked!"

        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        user = cursor.fetchone()

        login_status = False
        role = "user"

        if user:
            role = user[4]
            if check_password_hash(user[3], password):
                login_status = True

        # LOG ATTACKS
        if rule_attack or ml_attack:
            status = "Blocked" if waf_enabled else "Allowed"
            cursor.execute(
                "INSERT INTO attacks (input, type, status, ip) VALUES (%s, %s, %s, %s)",
                (input_text, attack_type, status, ip)
            )

        conn.commit()
        conn.close()

        if login_status:
            session['user'] = user[1]
            session['role'] = role

            if role == 'admin':
                return redirect('/dashboard')
            else:
                return redirect('/')
        else:
            return "Invalid Credentials!"

    return render_template("login.html", waf=waf_enabled, secure=secure_mode)

# ==============================
# ADMIN PANEL
# ==============================
@app.route('/admin')
def admin_panel():
    if 'user' not in session:
        return redirect('/login')

    if session.get('role') != 'admin':
        return "🚫 Admin Only"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, email, role FROM users")
    users = cursor.fetchall()

    conn.close()

    return render_template("admin.html", users=users)

@app.route('/make_admin/<int:user_id>')
def make_admin(user_id):
    if session.get('role') != 'admin':
        return "🚫 Not allowed"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE users SET role='admin' WHERE id=%s", (user_id,))
    conn.commit()
    conn.close()

    return redirect('/admin')

@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    if session.get('role') != 'admin':
        return "🚫 Not allowed"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
    conn.commit()
    conn.close()

    return redirect('/admin')

# ==============================
# DASHBOARD
# ==============================
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    if session.get('role') != 'admin':
        return "🚫 Access Denied"

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM attacks WHERE status='Blocked'")
    blocked = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM attacks WHERE status='Allowed'")
    allowed = cursor.fetchone()[0]

    cursor.execute("SELECT * FROM attacks ORDER BY id ASC")
    logs = cursor.fetchall()

    conn.close()

    return render_template("dashboard.html",
                           blocked=blocked,
                           allowed=allowed,
                           logs=logs,
                           waf=waf_enabled,
                           secure=secure_mode)

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
    app.run(host="127.0.0.1", port=5500, debug=True)