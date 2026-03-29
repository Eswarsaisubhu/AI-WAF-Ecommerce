# 🛡️ AI-Powered Hybrid WAF E-Commerce Application

An advanced **Flask-based E-Commerce Web Application** integrated with a **Hybrid Web Application Firewall (WAF)** using both **Rule-Based Detection** and **Machine Learning**.

---

## 🚀 Features

### 🛒 E-Commerce System
- User Registration & Login  
- Product Listing  
- Session Management  
- Secure Authentication (Password Hashing)  

### 🔐 Security (WAF)
- Rule-Based Attack Detection  
- Machine Learning Attack Detection  
- SQL Injection Detection  
- Cross-Site Scripting (XSS) Detection  
- Real-time Attack Logging  

### 📊 Dashboard & Monitoring
- Admin Dashboard  
- Attack Logs Viewer  
- Blocked vs Allowed Statistics  
- Live Logs API  
- Reports with Analytics  

### ⚡ Advanced Features
- Rate Limiting (Anti-Brute Force)  
- Secure Mode (Parameterized Queries)  
- WAF Toggle Mode (ON/OFF)  
- Attack Lab for Testing Payloads  

---

## 🧠 Tech Stack

- **Backend:** Flask (Python)  
- **Database:** MySQL  
- **Machine Learning:** Scikit-learn (Pickle Model)  
- **Frontend:** HTML, CSS, Bootstrap  
- **Security:** WAF + Password Hashing + Rate Limiting  

---

## 📂 Project Structure

```
Hybrid-WAF-Ecommerce/
│
├── app.py
├── model.pkl
├── vectorizer.pkl
├── templates/
├── static/
├── .gitignore
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository
```bash
git clone https://github.com/Eswarsaisubhu/AI-WAF-Ecommerce.git
cd AI-WAF-Ecommerce
```

### 2️⃣ Create Virtual Environment
```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate  

# Windows
venv\Scripts\activate
```

### 3️⃣ Install Dependencies
```bash
pip install flask mysql-connector-python scikit-learn
```

### 4️⃣ Setup Database

Create database:
```sql
CREATE DATABASE waf_db;
```

Create tables:
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(100),
    password VARCHAR(255),
    role VARCHAR(20) DEFAULT 'user'
);

CREATE TABLE attacks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    input TEXT,
    type VARCHAR(50),
    status VARCHAR(20),
    ip VARCHAR(50)
);
```

---

### 5️⃣ Run Application
```bash
python app.py
```

👉 Open in browser:  
```
http://127.0.0.1:5500
```

---

## 🔥 How It Works

1. User sends input (login or payload)  
2. Input is analyzed using:
   - Rule-Based Detection  
   - Machine Learning Model  
3. WAF decision:
   - ✅ Allow  
   - 🚫 Block  
4. Attacks are logged in the database  
5. Admin dashboard displays analytics  

---

## 🧪 Attack Examples

Test in **Attack Lab**:

```sql
' OR '1'='1
<script>alert(1)</script>
DROP TABLE users;
UNION SELECT * FROM users;
```

---

## 📊 Dashboard Features

- Total Attacks  
- Blocked Attacks (%)  
- Allowed Attacks (%)  
- Most Common Attack Type  
- Live Logs  

---

## 🔐 Security Highlights

- Password hashing using Werkzeug  
- SQL Injection prevention (Secure Mode)  
- Rate limiting (Anti-bot protection)  
- Machine Learning-based anomaly detection  

---

## 💼 Resume Description

> Developed a Hybrid Web Application Firewall (WAF) integrated E-Commerce platform using Flask and Machine Learning. Implemented real-time attack detection (SQL Injection & XSS), secure authentication, rate limiting, and an admin dashboard for monitoring cyber threats.

---

## 🎯 Future Enhancements

- Role-Based Access Control (Admin/User UI)  
- Payment Gateway Integration  
- JWT Authentication  
- Cloud Deployment (AWS)  
- Advanced AI Threat Detection  

---

## 👨‍💻 Author

**Eswar Sai Subrahmanyam Chennam**
