import streamlit as st
import sqlite3
import pandas as pd
import altair as alt
from io import BytesIO

# =============================================
# DATABASE SETUP (Gunakan /tmp supaya Cloud aman)
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
              (open_price, tp, sl, result, reason, profit, trade_id, user_id))
    conn.commit()
    conn.close()

def delete_trade(trade_id, user_id):
    conn = sqlite3.connect(DB_PATH)
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
if "user_id" not in st.session_state:
    st.session_state.user_id = None

if not st.session_state.logged_in:
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
                st.experimental_rerun()
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
    st.stop()

# =============================================
# MAIN APP
# =============================================
st.markdown("<div class='title'>📊 Trading Journal</div>", unsafe_allow_html=True)

menu = st.sidebar.radio("Menu", ["Tambah Catatan", "Lihat Catatan", "Grafik Profit/Loss", "Export Data", "Logout"])

user_id = st.session_state.user_id

# ---------------------------------------------
# TAMBAH CATATAN
# ---------------------------------------------
if menu == "Tambah Catatan":
    st.header("Tambah Catatan Trading")

    col1, col2 = st.columns(2)

    with col1:
        open_price = st.number_input("Open Price", value=0.0)
        tp = st.number_input("Take Profit", value=0.0)
        sl = st.number_input("Stop Loss", value=0.0)

    with col2:
        result = st.selectbox("Hasil", ["Profit", "Loss"])
        profit = st.number_input("Profit (+) / Loss (-)", value=0.0)

    reason = st.text_area("Catatan / Alasan")

    if st.button("Simpan"):
        insert_trade(user_id, open_price, tp, sl, result, reason, profit)
        st.success("Catatan trading disimpan!")

# ---------------------------------------------
# LIHAT CATATAN (EDIT / DELETE)
# ---------------------------------------------
elif menu == "Lihat Catatan":
    st.header("Daftar Catatan Trading")

    data = get_trades(user_id)

    if not data:
        st.info("Belum ada data.")
    else:
        df = pd.DataFrame(data, columns=["ID", "User ID", "Open", "TP", "SL", "Hasil", "Catatan", "Profit"])
        st.dataframe(df)

        st.subheader("Edit / Delete Data")
        selected_id = st.number_input("Masukkan ID", value=0)

        if st.button("Edit Data"):
            record = df[df["ID"] == selected_id]
            if not record.empty:
                rec = record.iloc[0]
                open_price = st.number_input("Open Price", value=float(rec["Open"]))
                tp = st.number_input("Take Profit", value=float(rec["TP"]))
                sl = st.number_input("Stop Loss", value=float(rec["SL"]))
                result = st.selectbox("Hasil", ["Profit", "Loss"], index=0 if rec["Hasil"]=="Profit" else 1)
                profit = st.number_input("Profit", value=float(rec["Profit"]))
                reason = st.text_area("Catatan", rec["Catatan"])

                if st.button("Simpan Perubahan"):
                    update_trade(selected_id, user_id, open_price, tp, sl, result, reason, profit)
                    st.success("Data berhasil diperbarui!")
                    st.experimental_rerun()

        if st.button("Hapus Data"):
            delete_trade(selected_id, user_id)
            st.success("Data berhasil dihapus!")
            st.experimental_rerun()

# ---------------------------------------------
# GRAFIK PROFIT / LOSS
# ---------------------------------------------
elif menu == "Grafik Profit/Loss":
    st.header("Grafik Profit/Loss")

    data = get_trades(user_id)

    if not data:
        st.info("Belum ada data.")
    else:
        df = pd.DataFrame(data, columns=["ID", "User ID", "Open", "TP", "SL", "Hasil", "Catatan", "Profit"])
        chart = alt.Chart(df).mark_line(point=True).encode(
            x="ID",
            y="Profit",
            color=alt.value("#3498db")
        )
        st.altair_chart(chart, use_container_width=True)

# ---------------------------------------------
# EXPORT DATA
# ---------------------------------------------
elif menu == "Export Data":
    st.header("Export ke Excel")

    data = get_trades(user_id)

    if not data:
        st.info("Belum ada data.")
    else:
        df = pd.DataFrame(data, columns=["ID", "User ID", "Open", "TP", "SL", "Hasil", "Catatan", "Profit"])

        buffer = BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)

        st.download_button("Download Excel", data=buffer, file_name="trading_journal.xlsx")

# ---------------------------------------------
# LOGOUT
# ---------------------------------------------
elif menu == "Logout":
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.experimental_rerun()
