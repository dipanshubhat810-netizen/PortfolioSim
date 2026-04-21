import sqlite3
import hashlib
import os
import hmac
import streamlit as st

DB_FILE = "users.db"


def get_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)


def init_auth_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()

    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        100000
    ).hex()

    return pwd_hash, salt


def verify_password(password, stored_hash, stored_salt):
    pwd_hash, _ = hash_password(password, stored_salt)
    return hmac.compare_digest(pwd_hash, stored_hash)


def register_user(username, email, password):
    conn = get_connection()
    cur = conn.cursor()

    try:
        password_hash, salt = hash_password(password)
        cur.execute("""
            INSERT INTO users (username, email, password_hash, salt)
            VALUES (?, ?, ?, ?)
        """, (username.strip(), email.strip(), password_hash, salt))
        conn.commit()
        return True, "Registration successful. Please login."
    except sqlite3.IntegrityError:
        return False, "Username or email already exists."
    finally:
        conn.close()


def login_user(username, password):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, username, email, password_hash, salt
        FROM users
        WHERE username = ?
    """, (username.strip(),))

    user = cur.fetchone()
    conn.close()

    if not user:
        return False, "User not found.", None

    user_id, db_username, db_email, password_hash, salt = user

    if verify_password(password, password_hash, salt):
        return True, "Login successful.", {
            "id": user_id,
            "username": db_username,
            "email": db_email
        }

    return False, "Incorrect password.", None


def ensure_session_state():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "user" not in st.session_state:
        st.session_state.user = None


def logout_user():
    st.session_state.logged_in = False
    st.session_state.user = None
    st.rerun()


def require_login():
    ensure_session_state()

    if not st.session_state.logged_in:
        st.warning("Please login first.")
        st.stop()


def current_user():
    ensure_session_state()
    return st.session_state.user


def render_sidebar():
    ensure_session_state()
    user = st.session_state.user or {"username": "Guest", "email": "Not logged in"}

    with st.sidebar:
        st.markdown(
            '<div style="font-size:1.6rem;font-weight:800;color:#00d4aa;letter-spacing:-1px;">PortfolioSim</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div style="font-size:0.7rem;color:#64748b;letter-spacing:3px;text-transform:uppercase;">Investment Simulator</div>',
            unsafe_allow_html=True
        )
        st.markdown("---")
        st.markdown(f"**👤 {user['username']}**")
        st.markdown(
            f'<span style="color:#64748b;font-size:0.8rem;">{user["email"]}</span>',
            unsafe_allow_html=True
        )
        st.markdown("---")
        st.markdown(
            '<span style="color:#f59e0b;font-size:0.75rem;">⚠️ Mock Data Mode</span>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<span style="color:#64748b;font-size:0.72rem;">DB: portfolio_sim (not connected)</span>',
            unsafe_allow_html=True
        )

        if st.session_state.logged_in:
            if st.button("Logout"):
                logout_user()
