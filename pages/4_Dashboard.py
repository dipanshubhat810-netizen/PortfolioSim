import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from mock_data.dummy_data import (get_all_profiles, get_active_portfolio,
                                   compute_portfolio_value, get_portfolio_history,
                                   get_risk_label)

st.set_page_config(page_title="Dashboard · PortfolioSim", page_icon="📊", layout="wide")
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
</style>""", unsafe_allow_html=True)

PT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
          font=dict(family="Syne", color="#e2e8f0"), margin=dict(l=0,r=0,t=30,b=0))

st.markdown("# 📊 Portfolio Dashboard")
st.caption("mirrors GET /profile/<id>/dashboard — calls get_active_portfolio() + compute_portfolio_value()")
st.markdown("---")

profiles = get_all_profiles(1)
profile_options = {f"{p['name']} (Risk: {p['risk_capacity']}/10)": p["id"] for p in profiles}
sel = st.selectbox("Select Profile", list(profile_options.keys()))
profile_id = profile_options[sel]
profile    = next(p for p in profiles if p["id"] == profile_id)

active = get_active_portfolio(profile_id)

if active is None:
    st.warning("No active portfolio found for this profile. Go to ⚙️ Generate Portfolio to create one.")
    st.stop()

# ── Simulate live value (runs every page load like Flask dashboard route) ─────
sim = compute_portfolio_value(active)

label  = active["recommended_type"]
colors = {"conservative":"#22c55e","balanced":"#f59e0b","aggressive":"#ef4444"}
color  = colors.get(label, "#00d4aa")

# ── Profile + sentiment banner ─────────────────────────────────────────────
sentiment_label = "🟢 Bullish" if sim["sentiment"] > 0.3 else ("🔴 Bearish" if sim["sentiment"] < -0.3 else "🟡 Neutral")
st.markdown(f"""
<div style="background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:18px;margin-bottom:20px;display:flex;justify-content:space-between;align-items:center;">
  <div>
    <div style="font-size:1.2rem;font-weight:800;">{profile['name']}</div>
    <div style="color:#64748b;font-size:0.85rem;">Risk {profile['risk_capacity']}/10 ·
      <span style="color:{color};">{label.title()}</span> ·
      Portfolio #{active['id']} · Created {active['created_at']}</div>
  </div>
  <div style="text-align:right;">
    <div style="font-size:0.75rem;color:#64748b;text-transform:uppercase;letter-spacing:1px;">Market Sentiment</div>
    <div style="font-size:1rem;font-weight:700;">{sentiment_label}</div>
    <div style="font-family:'Space Mono';font-size:0.8rem;color:#64748b;">{sim['sentiment']:+.3f}</div>
  </div>
</div>""", unsafe_allow_html=True)

# ── KPIs ──────────────────────────────────────────────────────────────────
change_color = "#22c55e" if sim["change_pct"] >= 0 else "#ef4444"
m1, m2, m3, m4 = st.columns(4)
m1.metric("Base Investment",  f"₹{sim['base_amount']:,.2f}")
m2.metric("Current Value",    f"₹{sim['current_value']:,.2f}",
          delta=f"{sim['change_pct']:+.2f}%")
m3.metric("Absolute Change",  f"₹{sim['current_value']-sim['base_amount']:+,.2f}")
m4.metric("Assets in Portfolio", len(sim["assets"]))
st.markdown("")

# ── Portfolio history line ─────────────────────────────────────────────────
st.markdown('<div class="section-header">Portfolio Value History (6 Months)</div>', unsafe_allow_html=True)
st.caption("In production: compute from portfolio_assets × stock_prices snapshots over time")

hist = get_portfolio_history(profile_id, 180)
fig_line = go.Figure(go.Scatter(
    x=hist["date"], y=hist["value"], mode="lines",
    line=dict(color="#00d4aa", width=2),
    fill="tozeroy", fillcolor="rgba(0,212,170,0.06)",
))
fig_line.update_layout(**PT, height=250,
    xaxis=dict(showgrid=False, color="#64748b"),
    yaxis=dict(showgrid=True, gridcolor="#1e2d40", tickprefix="₹", color="#64748b"))
st.plotly_chart(fig_line, use_container_width=True)

# ── Per-asset breakdown ────────────────────────────────────────────────────
st.markdown('<div class="section-header">Asset Breakdown — Current Simulation</div>', unsafe_allow_html=True)
st.caption("Values use: base × weight × (1 + snapshot_expected_return + sentiment × volatility) — mirrors simulation.py")

asset_df = pd.DataFrame(sim["assets"])

# Bar chart: allocated vs current
fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(name="Allocated", x=asset_df["name"], y=asset_df["allocated"],
    marker_color="rgba(59,130,246,0.7)"))
fig_bar.add_trace(go.Bar(name="Current",   x=asset_df["name"], y=asset_df["current"],
    marker_color="rgba(0,212,170,0.85)"))
fig_bar.update_layout(**PT, height=280, barmode="group",
    xaxis=dict(color="#64748b", tickangle=-20),
    yaxis=dict(showgrid=True, gridcolor="#1e2d40", tickprefix="₹", color="#64748b"),
    legend=dict(bgcolor="rgba(0,0,0,0)"))
st.plotly_chart(fig_bar, use_container_width=True)

# Table
display = asset_df[["name","type","weight","allocated","current","change","change_pct"]].copy()
display.columns = ["Asset","Type","Weight","Allocated (₹)","Current (₹)","Change (₹)","Change (%)"]
display["Weight"]       = display["Weight"].apply(lambda x: f"{x*100:.1f}%")
display["Allocated (₹)"]= display["Allocated (₹)"].apply(lambda x: f"₹{x:,.2f}")
display["Current (₹)"]  = display["Current (₹)"].apply(lambda x: f"₹{x:,.2f}")
display["Change (₹)"]   = display["Change (₹)"].apply(lambda x: f"+₹{x:,.2f}" if x>=0 else f"-₹{abs(x):,.2f}")
display["Change (%)"]   = display["Change (%)"].apply(lambda x: f"+{x:.2f}%" if x>=0 else f"{x:.2f}%")
st.dataframe(display, use_container_width=True, hide_index=True)

st.markdown("")
st.caption("⚠️ Values are simulated and refresh on every page load — this mirrors modules/simulation.py exactly.")
if st.button("🔄 Refresh Simulation"):
    st.rerun()
