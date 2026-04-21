import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from mock_data.dummy_data import (get_all_profiles, get_all_sectors,
                                   generate_portfolio_preview, save_portfolio,
                                   get_risk_label, RISK_FREE_RATE)

st.set_page_config(page_title="Generate Portfolio · PortfolioSim", page_icon="⚙️", layout="wide")
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

st.markdown("# ⚙️ Generate Portfolio")
st.caption("mirrors GET+POST /profile/<id>/generate — calls engine.generate_portfolio_preview()")
st.markdown("---")

# ── Step 1: Inputs ─────────────────────────────────────────────────────────
st.markdown('<div class="section-header">Step 1 — Select Profile & Parameters</div>', unsafe_allow_html=True)

profiles = get_all_profiles(1)
sectors  = get_all_sectors()

c1, c2 = st.columns(2)
with c1:
    profile_options = {f"{p['name']} (Risk: {p['risk_capacity']}/10)": p["id"] for p in profiles}
    sel_profile = st.selectbox("Investor Profile", list(profile_options.keys()))
    profile_id  = profile_options[sel_profile]
    profile     = next(p for p in profiles if p["id"] == profile_id)

with c2:
    base_amount = st.number_input("Base Investment Amount (₹)", min_value=10000,
                                   max_value=100_000_000, value=500000, step=10000)

st.markdown("")
st.markdown('<div class="section-header">Step 2 — Pick Sectors (max 3)</div>', unsafe_allow_html=True)
st.caption("mirrors portfolio_interests table — up to 3 sector_ids stored per portfolio")

sector_cols = st.columns(3)
selected_sectors = []
for i, s in enumerate(sectors):
    with sector_cols[i % 3]:
        if st.checkbox(f"**{s['name']}**\n\n_{s['description']}_", key=f"sec_{s['id']}"):
            selected_sectors.append(s["id"])

if len(selected_sectors) > 3:
    st.warning("⚠️ Maximum 3 sectors allowed. Please deselect one.")
    selected_sectors = selected_sectors[:3]

st.markdown("")
generate = st.button("🔧 Run Markowitz Engine & Generate Preview", use_container_width=True,
                      disabled=(len(selected_sectors) == 0))

if len(selected_sectors) == 0:
    st.info("Select at least 1 sector above to generate a portfolio.")

# ── Step 3: Preview ────────────────────────────────────────────────────────
if generate and len(selected_sectors) > 0:
    with st.spinner("Running Markowitz engine — ranking assets, computing weights, calculating variance..."):
        preview = generate_portfolio_preview(profile_id, selected_sectors, base_amount)
        st.session_state["preview"] = preview

if "preview" in st.session_state:
    preview = st.session_state["preview"]
    st.markdown("---")
    st.markdown('<div class="section-header">Step 3 — Portfolio Preview</div>', unsafe_allow_html=True)
    st.caption("mirrors GET /profile/<id>/preview — data passed via session in Flask")

    label  = preview["recommended_type"]
    colors = {"conservative":"#22c55e","balanced":"#f59e0b","aggressive":"#ef4444"}
    color  = colors[label]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Expected Return",     f"{preview['expected_return']*100:.2f}%")
    m2.metric("Portfolio Variance",  f"{preview['portfolio_variance']*100:.4f}%")
    m3.metric("Risk Profile",        label.title())
    m4.metric("Assets Selected",     len(preview["assets"]))
    st.markdown("")

    # Charts
    ca, cb = st.columns([1, 1.5])
    with ca:
        st.markdown('<div class="section-header">Weight Allocation</div>', unsafe_allow_html=True)
        df_a = pd.DataFrame(preview["assets"])
        fig_pie = go.Figure(go.Pie(
            labels=df_a["name"], values=df_a["weight"],
            hole=0.45,
            marker_colors=["#00d4aa","#3b82f6","#a855f7","#f59e0b","#ef4444","#22c55e","#06b6d4","#8b5cf6"],
            textinfo="label+percent", textfont_size=10,
        ))
        fig_pie.update_layout(**PT, height=300, showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    with cb:
        st.markdown('<div class="section-header">Risk vs Return per Asset</div>', unsafe_allow_html=True)
        fig_sc = go.Figure(go.Scatter(
            x=df_a["volatility"]*100, y=df_a["expected_return"]*100,
            mode="markers+text",
            marker=dict(size=df_a["weight"]*200+8, color="#00d4aa", opacity=0.85,
                        line=dict(color="#0a0e1a", width=1)),
            text=df_a["name"], textposition="top center",
            textfont=dict(color="#e2e8f0", size=10),
        ))
        fig_sc.update_layout(**PT, height=300,
            xaxis=dict(title="Volatility (%)", showgrid=True, gridcolor="#1e2d40", color="#64748b"),
            yaxis=dict(title="Expected Return (%)", showgrid=True, gridcolor="#1e2d40", color="#64748b"))
        st.plotly_chart(fig_sc, use_container_width=True)

    # Asset table
    st.markdown('<div class="section-header">Asset Breakdown</div>', unsafe_allow_html=True)
    display = df_a[["name","type","sector","weight","expected_return","volatility","allocated"]].copy()
    display.columns = ["Asset","Type","Sector","Weight","Exp. Return","Volatility","Allocated (₹)"]
    display["Weight"]       = display["Weight"].apply(lambda x: f"{x*100:.1f}%")
    display["Exp. Return"]  = display["Exp. Return"].apply(lambda x: f"{x*100:.2f}%")
    display["Volatility"]   = display["Volatility"].apply(lambda x: f"{x*100:.2f}%")
    display["Allocated (₹)"]= display["Allocated (₹)"].apply(lambda x: f"₹{x:,.2f}")
    st.dataframe(display, use_container_width=True, hide_index=True)

    # Save / Discard
    st.markdown("")
    col_save, col_discard = st.columns(2)
    with col_save:
        if st.button("✅ Adopt This Portfolio", use_container_width=True):
            result = save_portfolio(profile_id, preview)
            if result["success"]:
                st.success(f"✅ {result['message']} Portfolio ID: #{result['portfolio_id']}\n\n"
                           f"In production: INSERT INTO portfolios + portfolio_assets + portfolio_interests")
                del st.session_state["preview"]
            else:
                st.error("Failed to save portfolio.")
    with col_discard:
        if st.button("❌ Discard", use_container_width=True):
            del st.session_state["preview"]
            st.rerun()
