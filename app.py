from flask import Flask, request, redirect, session
from flask import render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = "ganti-ini"

# ========================
# DATABASE SETUP
# ========================
def init_db():
    conn = sqlite3.connect("data.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            open_price REAL,
            tp REAL,
            sl REAL,
            result TEXT,
            note TEXT,
            profit REAL
        )
    """)
    conn.commit()
    conn.close()

init_db()


# ========================
# HTML TEMPLATE DI DALAM PYTHON
# ========================

login_page = """
<h2>Login / Daftar Akun</h2>
<form method="POST">
    <input name="username" placeholder="Username"><br><br>
    <input name="password" type="password" placeholder="Password"><br><br>
    <button type="submit">Login</button>
</form>
<p style='color:red;'>{{error}}</p>
"""


dashboard_page = """
<h2>Trading Journal</h2>

<a href="/add">Tambah Catatan</a> |
<a href="/logout">Logout</a>

<table border="1" cellpadding="5" cellspacing="0">
<tr>
  <th>Open</th>
  <th>TP</th>
  <th>SL</th>
  <th>Hasil</th>
  <th>Catatan</th>
  <th>Profit</th>
  <th>Aksi</th>
</tr>

{% for t in trades %}
<tr>
  <td>{{t[2]}}</td>
  <td>{{t[3]}}</td>
  <td>{{t[4]}}</td>
  <td>{{t[5]}}</td>
  <td>{{t[6]}}</td>
  <td>{{t[7]}}</td>
  <td>
    <a href="/edit/{{t[0]}}">Edit</a> |
    <a href="/delete/{{t[0]}}">Hapus</a>
  </td>
</tr>
{% endfor %}

</table>
"""


add_page = """
<h2>Tambah Catatan Trading</h2>
<form method="POST">
    <input name="open_price" placeholder="Open Price"><br><br>
    <input name="tp" placeholder="Take Profit"><br><br>
    <input name="sl" placeholder="Stop Loss"><br><br>

    <select name="result">
        <option value="Profit">Profit</option>
        <option value="Loss">Loss</option>
    </select><br><br>

    <textarea name="note" placeholder="Alasan / Catatan"></textarea><br><br>
    <input name="profit" placeholder="Jumlah Profit / Loss"><br><br>

    <button type="submit">Simpan</button>
</form>
"""


# ========================
# LOGIN
# ========================
@app.route("/", methods=["GET", "POST"])
def login():
    error = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("data.db")
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()

        if user:
            session["uid"] = user[0]
            return redirect("/dashboard")

        # jika user tidak ada → register otomatis
        try:
            c.execute("INSERT INTO users(username, password) VALUES (?,?)", (username, password))
            conn.commit()

            c.execute("SELECT * FROM users WHERE username=?", (username,))
            new_user = c.fetchone()
            session["uid"] = new_user[0]
            conn.close()
