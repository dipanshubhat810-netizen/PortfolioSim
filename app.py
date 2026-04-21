import streamlit as st
from auth_utils import (
    init_auth_db,
    ensure_session_state,
    register_user,
    login_user,
    render_sidebar,
    current_user,
)

st.set_page_config(
    page_title="PortfolioSim",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_auth_db()
ensure_session_state()

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

if not st.session_state.logged_in:
    st.markdown("## 💼 Welcome to PortfolioSim")
    st.info("Please login or register to continue.")

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        st.subheader("Login")

        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")

        if st.button("Login Now"):
            success, message, user = login_user(login_username, login_password)

            if success:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success(message)
                st.rerun()
            else:
                st.error(message)

    with register_tab:
        st.subheader("Register")

        reg_username = st.text_input("Choose Username", key="reg_username")
        reg_email = st.text_input("Email", key="reg_email")
        reg_password = st.text_input("Choose Password", type="password", key="reg_password")
        reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")

        if st.button("Create Account"):
            if not reg_username or not reg_email or not reg_password or not reg_confirm:
                st.warning("Please fill all fields.")
            elif reg_password != reg_confirm:
                st.error("Passwords do not match.")
            elif len(reg_password) < 4:
                st.error("Password must be at least 4 characters.")
            else:
                success, message = register_user(reg_username, reg_email, reg_password)
                if success:
                    st.success(message)
                else:
                    st.error(message)

    st.stop()

render_sidebar()

user = current_user()

st.markdown("## 💼 Welcome to PortfolioSim")
st.success(f"Logged in as {user['username']}")

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
