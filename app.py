import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
from io import BytesIO

# =============================================
# DATABASE SETUP (Gunakan /tmp untuk Streamlit Cloud)
# =============================================
DB_PATH = "/tmp/trading.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
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
              (user_id, open_price, tp, sl, result, reason, profit))
    conn.commit()
    conn.close()

def get_trades(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM trades WHERE user_id=?", (user_id,))
    data = c.fetchall()
    conn.close()
    return data

def update_trade(trade_id, user_id, open_price, tp, sl, result, reason, profit):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""UPDATE trades SET open_price=?, tp=?, sl=?, result=?, reason=?, profit=?
                 WHERE id=? AND user_id=?""",
              (open_price, tp, sl, resul_
