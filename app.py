import streamlit as st

st.set_page_config(
    page_title="PortfolioSim",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------
# Session state setup
# -----------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Demo in-memory users
# NOTE: This is only for demo/testing.
if "users" not in st.session_state:
    st.session_state.users = {
        "demo_user": {
            "email": "demo@example.com",
            "password": "1234"
        }
    }

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');
:root{--bg:#0a0e1a;--surface:#111827;--border:#1e2d40;--accent:#00d4aa;--accent2:#3b82f6;--red:#ef4444;--green:#22c55e;--text:#e2e8f0;--muted:#64748b;}
html,body,[data-testid="stAppViewContainer"]{background-color:var(--bg)!important;color:var(--text)!important;font-family:'Syne',sans-serif!important;}
[data-testid="stSidebar"]{background-color:var(--surface)!important;border-right:1px solid var(--border)!important;}
[data-testid="stSidebar"] *{color:var(--text)!important;}
h1,h2,h3,h4{font-family:'Syne',sans-serif!important;color:var(--text)!important;}
div[data-testid="stMetric"]{background:var(--surface);border-radius:10px;padding:16px;border:1px solid var(--border);}
div[data-testid="stMetric"] label{color:var(--muted)!important;font-size:0.75rem!important;text-transform:uppercase;letter-spacing:1px;}
div[data-testid="stMetric"] [data-testid="stMetricValue"]{font-family:'Space Mono',monospace;color:var(--text)!important;}
.stButton>button{background:var(--accent)!important;color:#0a0e1a!important;font-family:'Syne',sans-serif!important;font-weight:700!important;border:none!important;border-radius:8px!important;}
.section-header{font-size:1rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid var(--border);padding-bottom:8px;margin-bottom:16px;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Login/Register screen
# -----------------------------
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center;'>💼 PortfolioSim</h1>", unsafe_allow_html=True)
    st.markdown(
        "<p style='text-align:center; color:#64748b;'>Login or create an account to continue</p>",
        unsafe_allow_html=True
    )

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        st.subheader("Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login"):
            if login_username in st.session_state.users:
                saved_password = st.session_state.users[login_username]["password"]
                if login_password == saved_password:
                    st.session_state.logged_in = True
                    st.session_state.current_user = login_username
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Incorrect password")
            else:
                st.error("User not found")

    with register_tab:
        st.subheader("Create Account")
        reg_username = st.text_input("Choose a username", key="reg_username")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Choose a password", type="password", key="reg_password")
        reg_confirm = st.text_input("Confirm password", type="password", key="reg_confirm")

        if st.button("Register"):
            if not reg_username or not reg_email or not reg_password or not reg_confirm:
                st.warning("Please fill all fields")
            elif reg_username in st.session_state.users:
                st.error("Username already exists")
            elif reg_password != reg_confirm:
                st.error("Passwords do not match")
            else:
                st.session_state.users[reg_username] = {
                    "email": reg_email,
                    "password": reg_password
                }
                st.success("Registration successful! Please login.")

    st.stop()

# -----------------------------
# Sidebar after login
# -----------------------------
current_username = st.session_state.current_user
current_email = st.session_state.users[current_username]["email"]

with st.sidebar:
    st.markdown('<div style="font-size:1.6rem;font-weight:800;color:#00d4aa;letter-spacing:-1px;">PortfolioSim</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-size:0.7rem;color:#64748b;letter-spacing:3px;text-transform:uppercase;">Investment Simulator</div>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown(f"**👤 {current_username}**")
    st.markdown(f'<span style="color:#64748b;font-size:0.8rem;">{current_email}</span>', unsafe_allow_html=True)
    st.markdown("---")
    st.markdown('<span style="color:#f59e0b;font-size:0.75rem;">⚠️ Mock Data Mode</span>', unsafe_allow_html=True)
    st.markdown('<span style="color:#64748b;font-size:0.72rem;">DB: portfolio_sim (not connected)</span>', unsafe_allow_html=True)

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

# -----------------------------
# Main app content
# -----------------------------
st.markdown("## 💼 Welcome to PortfolioSim")
st.info("Running on **mock data** matching the `portfolio_sim` database schema. Connect the DB by replacing functions in `mock_data/dummy_data.py`.")
st.markdown("""
| Page | Maps To | Description |
|------|---------|-------------|
| 👤 Profiles | `/home` | View & create investor profiles |
| 📋 Recommendations | `/profile/<id>/recommendations` | Pre-made portfolios matching your risk |
| ⚙️ Generate Portfolio | `/profile/<id>/generate` | Pick sectors, run Markowitz engine |
| 📊 Dashboard | `/profile/<id>/dashboard` | Live simulated portfolio value |
| 🎯 Recommender | Custom | MPT-based Monte Carlo suggestions |
""")
