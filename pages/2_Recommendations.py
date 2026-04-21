import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from mock_data.dummy_data import get_all_profiles, get_recommended_portfolios, get_risk_label

st.set_page_config(page_title="Recommendations · PortfolioSim", page_icon="📋", layout="wide")
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
.port-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:10px;}
</style>""", unsafe_allow_html=True)

RISK_COLORS = {"conservative":"#22c55e","balanced":"#f59e0b","aggressive":"#ef4444"}
RISK_BG     = {"conservative":"rgba(34,197,94,0.12)","balanced":"rgba(245,158,11,0.12)","aggressive":"rgba(239,68,68,0.12)"}

st.markdown("# 📋 Portfolio Recommendations")
st.caption("mirrors GET /profile/<id>/recommendations — REPLACE with: SELECT from portfolios WHERE recommended_type = %s")
st.markdown("---")

profiles = get_all_profiles(1)
profile_options = {f"{p['name']} (ID #{p['id']})": p["id"] for p in profiles}
selected = st.selectbox("Select Profile", list(profile_options.keys()))
profile_id = profile_options[selected]

profile = next(p for p in profiles if p["id"] == profile_id)
label   = get_risk_label(profile["risk_capacity"])
color   = RISK_COLORS[label]
bg      = RISK_BG[label]

st.markdown(f"""
<div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:18px;margin:16px 0;">
  <span style="font-weight:800;font-size:1.05rem;">{profile['name']}</span>
  <span style="margin-left:12px;background:{bg};color:{color};padding:4px 12px;border-radius:20px;font-size:0.75rem;font-weight:700;text-transform:uppercase;">{label}</span>
  <span style="color:#64748b;font-size:0.85rem;margin-left:12px;">Risk Capacity: {profile['risk_capacity']}/10</span>
</div>""", unsafe_allow_html=True)

recs = get_recommended_portfolios(profile_id)

st.markdown(f'<div class="section-header">Pre-Made {label.title()} Portfolios</div>', unsafe_allow_html=True)

if not recs:
    st.info("No pre-made portfolios match this risk profile yet.")
else:
    cols = st.columns(2)
    for i, r in enumerate(recs):
        with cols[i % 2]:
            rc = RISK_COLORS[r["recommended_type"]]
            rb = RISK_BG[r["recommended_type"]]
            st.markdown(f"""
            <div class="port-card">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <div style="font-size:1.05rem;font-weight:800;">{r['name']}</div>
                <span style="background:{rb};color:{rc};padding:3px 10px;border-radius:20px;font-size:0.72rem;font-weight:700;">{r['recommended_type'].title()}</span>
              </div>
              <div style="margin-top:10px;font-family:'Space Mono';font-size:1.2rem;color:#00d4aa;">₹{r['base_amount']:,.0f}</div>
              <div style="color:#64748b;font-size:0.78rem;margin-top:4px;">Base Investment</div>
            </div>""", unsafe_allow_html=True)

st.markdown("---")
st.markdown('<div class="section-header">Or Generate Your Own</div>', unsafe_allow_html=True)
st.info("👉 Go to **⚙️ Generate Portfolio** in the sidebar to run the Markowitz engine with your own sector picks.")
