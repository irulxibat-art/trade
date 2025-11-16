import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
from io import BytesIO

# =============================================
# DATABASE SETUP
# =============================================
DB_PATH = "/tmp/trading.db"  # Untuk Streamlit Cloud

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Tabel user
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Tabel trading
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
    )
    """)

    conn.commit()
    conn.close()

init_db()

# =============================================
# DATABASE FUNCTIONS
# =============================================
def register_user(username, password):
    try:
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO users(username, password) VALUES (?,?)", (username, password))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def login_user(username, password):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user

def insert_trade(user_id, open_price, tp, sl, result, reason, profit):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""INSERT INTO trades (user_id, open_price, tp, sl, result, reason, profit)
                 VALUES (?,?,?,?,?,?,?)""",
              (user_id, open_price, tp, sl, result, reason,
