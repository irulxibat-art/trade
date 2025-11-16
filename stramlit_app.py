import streamlit as st
import sqlite3

# === Database ===
def init_db():
    conn = sqlite3.connect("trading.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
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


# === UI ===
st.title("📊 Trading Journal App")
st.write("Catatan trading sederhana berbasis Streamlit")


menu = st.sidebar.selectbox("Menu", ["Tambah Catatan", "Lihat Catatan"])


# === Tambah Catatan ===
if menu == "Tambah Catatan":
    st.header("✏️ Tambah Catatan Trading")

    open_price = st.number_input("Open Price", value=0.0)
    tp = st.number_input("Take Profit", value=0.0)
    sl = st.number_input("Stop Loss", value=0.0)
    result = st.selectbox("Hasil", ["Profit", "Loss"])
    reason = st.text_area("Catatan / Alasan")
    profit = st.number_input("Profit (+) / Loss (-)", value=0.0)

    if st.button("Simpan"):
        conn = sqlite3.connect("trading.db")
        c = conn.cursor()
        c.execute("""
        INSERT INTO trades (open_price, tp, sl, result, reason, profit)
        VALUES (?,?,?,?,?,?)
        """, (open_price, tp, sl, result, reason, profit))
        conn.commit()
        conn.close()
        st.success("Catatan berhasil disimpan!")


# === Lihat Catatan ===
if menu == "Lihat Catatan":
    st.header("📒 Daftar Catatan Trading")

    conn = sqlite3.connect("trading.db")
    c = conn.cursor()
    c.execute("SELECT * FROM trades")
    data = c.fetchall()
    conn.close()

    if data:
        st.table(data)
    else:
        st.info("Belum ada catatan trading.")
