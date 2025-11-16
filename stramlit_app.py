import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
from io import BytesIO

# =============================================
# DATABASE SETUP
# =============================================
def init_db():
    conn = sqlite3.connect("trading.db")
    c = conn.cursor()

    # User login table
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )""")

    # Trading table
    c.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        open_price REAL,
        tp REAL,
        sl REAL,
        result TEXT,
        reason TEXT,
        profit REAL
    )""")

    conn.commit()
    conn.close()

init_db()

# =============================================
# DATABASE FUNCTIONS
# =============================================
def register_user(username, password):
    try:
        conn = sqlite3.connect("trading.db")
        c = conn.cursor()
        c.execute("INSERT INTO users(username, password) VALUES (?,?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def login_user(username, password):
    conn = sqlite3.connect("trading.db")
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user


def insert_trade(user_id, open_price, tp, sl, result, reason, profit):
    conn = sqlite3.connect("trading.db")
    c = conn.cursor()
    c.execute("""INSERT INTO trades (user_id, open_price, tp, sl, result, reason, profit)
                 VALUES (?,?,?,?,?,?,?)""",
              (user_id, open_price, tp, sl, result, reason, profit))
    conn.commit()
    conn.close()

def get_trades(user_id):
    conn = sqlite3.connect("trading.db")
    c = conn.cursor()
    c.execute("SELECT * FROM trades WHERE user_id=?", (user_id,))
    data = c.fetchall()
    conn.close()
    return data

def update_trade(trade_id, user_id, open_price, tp, sl, result, reason, profit):
    conn = sqlite3.connect("trading.db")
    c = conn.cursor()
    c.execute("""UPDATE trades SET open_price=?, tp=?, sl=?, result=?, reason=?, profit=?
                 WHERE id=? AND user_id=?""",
              (open_price, tp, sl, result, reason, profit, trade_id, user_id))
    conn.commit()
    conn.close()

def delete_trade(trade_id, user_id):
    conn = sqlite3.connect("trading.db")
    c = conn.cursor()
    c.execute("DELETE FROM trades WHERE id=? AND user_id=?", (trade_id, user_id))
    conn.commit()
    conn.close()

# =============================================
# STREAMLIT UI
# =============================================

st.set_page_config(page_title="Trading Journal", layout="wide")

st.markdown(
    """
    <style>
        body { background-color: #f4f6f9; }
        .title { font-size:40px; font-weight:700; color:#2c3e50; }
        .sub { font-size:20px; font-weight:500; color:#34495e; }
    </style>
    """, unsafe_allow_html=True
)

# =============================================
# LOGIN SYSTEM
# =============================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in == False:
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        st.markdown("<div class='title'>Login</div>", unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user[0]
                st.success("Login berhasil!")
                st.rerun()
            else:
                st.error("Username atau password salah.")

    with tab2:
        st.markdown("<div class='title'>Daftar Akun</div>", unsafe_allow_html=True)
        reg_user = st.text_input("Username Baru")
        reg_pass = st.text_input("Password Baru", type="password")
        if st.button("Register"):
            if register_user(reg_user, reg_pass):
                st.success("Registrasi berhasil! Silakan login.")
            else:
                st.error("Username sudah dipakai.")
    st.s
