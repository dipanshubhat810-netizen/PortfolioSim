import streamlit as st
from auth_utils import init_auth_db, ensure_session_state, require_login, render_sidebar, current_user

st.set_page_config(
    page_title="Profiles - PortfolioSim",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_auth_db()
ensure_session_state()
require_login()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');
:root{--bg:#0a0e1a;--surface:#111827;--border:#1e2d40;--accent:#00d4aa;--accent2:#3b82f6;--red:#ef4444;--green:#22c55e;--text:#e2e8f0;--muted:#64748b;}
html,body,[data-testid="stAppViewContainer"]{background-color:var(--bg)!important;color:var(--text)!important;font-family:'Syne',sans-serif!important;}
[data-testid="stSidebar"]{background-color:var(--surface)!important;border-right:1px solid var(--border)!important;}
[data-testid="stSidebar"] *{color:var(--text)!important;}
h1,h2,h3,h4{font-family:'Syne',sans-serif!important;color:var(--text)!important;}
.stButton>button{background:var(--accent)!important;color:#0a0e1a!important;font-family:'Syne',sans-serif!important;font-weight:700!important;border:none!important;border-radius:8px!important;}
</style>
""", unsafe_allow_html=True)

render_sidebar()
user = current_user()

st.title("👤 Profiles")
st.success(f"Logged in as {user['username']}")
st.write("This is the Profiles page.")
st.info("Add your profile-related content here.")
