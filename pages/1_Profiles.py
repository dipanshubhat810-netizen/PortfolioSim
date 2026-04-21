import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from mock_data.dummy_data import get_all_profiles, get_risk_label

st.set_page_config(page_title="Profiles · PortfolioSim", page_icon="👤", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');
:root{--bg:#0a0e1a;--surface:#111827;--border:#1e2d40;--accent:#00d4aa;--red:#ef4444;--green:#22c55e;--text:#e2e8f0;--muted:#64748b;}
html,body,[data-testid="stAppViewContainer"]{background-color:var(--bg)!important;color:var(--text)!important;font-family:'Syne',sans-serif!important;}
[data-testid="stSidebar"]{background-color:var(--surface)!important;border-right:1px solid var(--border)!important;}
h1,h2,h3,h4{font-family:'Syne',sans-serif!important;color:var(--text)!important;}
div[data-testid="stMetric"]{background:var(--surface);border-radius:10px;padding:16px;border:1px solid var(--border);}
div[data-testid="stMetric"] label{color:var(--muted)!important;font-size:0.75rem!important;text-transform:uppercase;letter-spacing:1px;}
div[data-testid="stMetric"] [data-testid="stMetricValue"]{font-family:'Space Mono',monospace;color:var(--text)!important;}
.stButton>button{background:var(--accent)!important;color:#0a0e1a!important;font-family:'Syne',sans-serif!important;font-weight:700!important;border:none!important;border-radius:8px!important;}
.section-header{font-size:1rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:2px;border-bottom:1px solid var(--border);padding-bottom:8px;margin-bottom:16px;}
.profile-card{background:var(--surface);border:1px solid var(--border);border-radius:14px;padding:22px;margin-bottom:12px;}
.risk-badge{display:inline-block;padding:4px 12px;border-radius:20px;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:1px;}
</style>""", unsafe_allow_html=True)

RISK_COLORS = {"conservative": "#22c55e", "balanced": "#f59e0b", "aggressive": "#ef4444"}
RISK_BG     = {"conservative": "rgba(34,197,94,0.12)", "balanced": "rgba(245,158,11,0.12)", "aggressive": "rgba(239,68,68,0.12)"}

st.markdown("# 👤 Investor Profiles")
st.caption("mirrors GET /home — REPLACE get_all_profiles() with: SELECT * FROM profiles WHERE acc_id = %s")
st.markdown("---")

profiles = get_all_profiles(account_id=1)

st.markdown('<div class="section-header">Your Profiles</div>', unsafe_allow_html=True)

for p in profiles:
    label = get_risk_label(p["risk_capacity"])
    color = RISK_COLORS[label]
    bg    = RISK_BG[label]
    st.markdown(f"""
    <div class="profile-card">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;">
        <div>
          <div style="font-size:1.2rem;font-weight:800;">{p['name']}</div>
          <div style="color:#64748b;font-size:0.85rem;margin-top:4px;">Profile ID: #{p['id']} · Age: {p['age']} · Income: ₹{p['income']:,.0f}</div>
        </div>
        <span class="risk-badge" style="background:{bg};color:{color};">{label}</span>
      </div>
      <div style="display:flex;gap:24px;margin-top:16px;">
        <div><span style="color:#64748b;font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;">Risk Capacity</span><br>
             <span style="font-family:'Space Mono';font-size:1.1rem;">{p['risk_capacity']} / 10</span></div>
        <div><span style="color:#64748b;font-size:0.75rem;text-transform:uppercase;letter-spacing:1px;">Risk Type</span><br>
             <span style="font-family:'Space Mono';font-size:1.1rem;color:{color};">{label.title()}</span></div>
      </div>
    </div>""", unsafe_allow_html=True)

st.markdown("")
st.markdown('<div class="section-header">Create New Profile</div>', unsafe_allow_html=True)
st.caption("mirrors POST /profile/new — REPLACE with: INSERT INTO profiles (acc_id, name, age, income, risk_capacity)")

with st.form("new_profile"):
    c1, c2 = st.columns(2)
    with c1:
        name   = st.text_input("Profile Name", placeholder="e.g. Retirement Plan")
        age    = st.number_input("Age", min_value=1, max_value=119, value=30)
    with c2:
        income = st.number_input("Annual Income (₹)", min_value=0, value=500000, step=10000)
        risk   = st.selectbox("Risk Capacity", options=list(range(1, 11)),
                              format_func=lambda x: {
                                  1:"1 — Very Safe",2:"2 — Very Safe",3:"3 — Conservative",
                                  4:"4 — Conservative",5:"5 — Balanced",6:"6 — Balanced",
                                  7:"7 — Aggressive",8:"8 — Aggressive",9:"9 — Very Aggressive",
                                  10:"10 — Maximum Risk"
                              }[x])
    submitted = st.form_submit_button("➕ Create Profile", use_container_width=True)
    if submitted:
        if name:
            st.success(f"✅ Profile **{name}** created! (Mock — no DB write yet)\n\nIn production: `INSERT INTO profiles (acc_id, name, age, income, risk_capacity) VALUES (1, '{name}', {age}, {income}, {risk})`")
        else:
            st.error("Please enter a profile name.")
