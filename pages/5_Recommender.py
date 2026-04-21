import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from mock_data.dummy_data import (get_all_profiles, get_all_sectors, get_assets_for_sectors,
                                   compute_sharpe, get_risk_label, RISK_FREE_RATE, SECTORS)

st.set_page_config(page_title="Recommender · PortfolioSim", page_icon="🎯", layout="wide")
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
.rec-card{background:var(--surface);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:12px;}
</style>""", unsafe_allow_html=True)

PT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
          font=dict(family="Syne", color="#e2e8f0"), margin=dict(l=0,r=0,t=30,b=0))

st.markdown("# 🎯 Smart Recommender")
st.markdown('<p style="color:#64748b;margin-top:-12px;">Monte Carlo simulation across all assets — personalised to your profile</p>', unsafe_allow_html=True)
st.caption("Uses assets + correlations tables via generate_portfolio_preview() — REPLACE with Quant API endpoint")
st.markdown("---")

st.markdown('<div class="section-header">Your Preferences</div>', unsafe_allow_html=True)

profiles = get_all_profiles(1)
sectors  = get_all_sectors()

c1, c2, c3 = st.columns(3)
with c1:
    profile_opts = {f"{p['name']} (Risk {p['risk_capacity']}/10)": p["id"] for p in profiles}
    sel_profile  = st.selectbox("👤 Profile", list(profile_opts.keys()))
    profile_id   = profile_opts[sel_profile]
    profile      = next(p for p in profiles if p["id"] == profile_id)
    budget       = st.number_input("💰 Budget (₹)", min_value=10000, max_value=100_000_000, value=500000, step=10000)

with c2:
    min_return = st.slider("📈 Min Expected Return (%)", 0, 30, 8)
    max_risk   = st.slider("⚠️ Max Volatility (%)", 2, 50, 20)

with c3:
    sector_names = [s["name"] for s in sectors]
    sel_sectors  = st.multiselect("🏭 Sectors (max 3)", sector_names, default=sector_names[:3])
    sel_sector_ids = [s["id"] for s in sectors if s["name"] in sel_sectors][:3]

st.markdown("")
run = st.button("🔍 Run Simulation (500 Portfolios)", use_container_width=True)

if run:
    if not sel_sector_ids:
        st.warning("Select at least one sector.")
    else:
        with st.spinner("Running Monte Carlo across 500 random portfolio combinations..."):
            all_assets = get_assets_for_sectors(sel_sector_ids)
            if len(all_assets) < 2:
                st.error("Not enough assets in selected sectors.")
                st.stop()

            results = []
            np.random.seed(42)
            for _ in range(500):
                n       = np.random.randint(2, min(len(all_assets)+1, 7))
                chosen  = np.random.choice(all_assets, n, replace=False)
                weights = np.random.dirichlet(np.ones(n))
                p_ret   = sum(a["expected_return"] * w for a, w in zip(chosen, weights))
                p_vol   = sum(a["volatility"] * w for a, w in zip(chosen, weights))
                p_shrp  = (p_ret - RISK_FREE_RATE) / p_vol if p_vol > 0 else 0
                results.append({
                    "return":  round(p_ret * 100, 2),
                    "vol":     round(p_vol * 100, 2),
                    "sharpe":  round(p_shrp, 3),
                    "assets":  [a["id"] for a in chosen],
                    "weights": list(weights.round(3)),
                })

            df = pd.DataFrame(results)
            df = df[(df["return"] >= min_return) & (df["vol"] <= max_risk)]

        st.markdown("---")
        if df.empty:
            st.error("❌ No portfolios matched your criteria. Try relaxing the return/risk filters.")
        else:
            label = get_risk_label(profile["risk_capacity"])
            if label == "conservative":
                top3 = df.sort_values("vol").head(3)
            elif label == "aggressive":
                top3 = df.sort_values("return", ascending=False).head(3)
            else:
                top3 = df.sort_values("sharpe", ascending=False).head(3)

            top3 = top3.reset_index(drop=True)
            st.success(f"✅ {len(df)} portfolios matched · Showing top 3 for **{label}** profile")

            colors = ["#00d4aa","#3b82f6","#a855f7"]
            labels = ["🥇 Best Pick","🥈 Runner Up","🥉 Alternative"]

            for i, row in top3.iterrows():
                color = colors[i]
                asset_details = []
                for aid, w in zip(row["assets"], row["weights"]):
                    a = next((x for x in all_assets if x["id"] == aid), None)
                    if a:
                        asset_details.append({
                            "name":   a["name"], "type": a["type"],
                            "sector": SECTORS[a["sector_id"]]["name"],
                            "weight": round(w*100,1),
                            "allocated": round(budget*w, 2),
                            "exp_return": f"{a['expected_return']*100:.2f}%",
                            "volatility": f"{a['volatility']*100:.2f}%",
                        })

                adf = pd.DataFrame(asset_details)
                st.markdown(f"""
                <div class="rec-card" style="border-color:{color};">
                  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;">
                    <span style="font-size:1.1rem;font-weight:800;color:{color};">{labels[i]}</span>
                    <div style="display:flex;gap:20px;font-family:'Space Mono';">
                      <div style="text-align:center;">
                        <div style="font-size:1.2rem;font-weight:700;color:#22c55e;">+{row['return']}%</div>
                        <div style="font-size:0.65rem;color:#64748b;text-transform:uppercase;">Return</div>
                      </div>
                      <div style="text-align:center;">
                        <div style="font-size:1.2rem;font-weight:700;color:#f59e0b;">{row['vol']}%</div>
                        <div style="font-size:0.65rem;color:#64748b;text-transform:uppercase;">Volatility</div>
                      </div>
                      <div style="text-align:center;">
                        <div style="font-size:1.2rem;font-weight:700;color:{color};">{row['sharpe']}</div>
                        <div style="font-size:0.65rem;color:#64748b;text-transform:uppercase;">Sharpe</div>
                      </div>
                    </div>
                  </div>
                </div>""", unsafe_allow_html=True)

                ca, cb = st.columns([1, 1.5])
                with ca:
                    fig_pie = go.Figure(go.Pie(
                        labels=adf["name"], values=adf["weight"], hole=0.45,
                        marker_colors=[color,"#1e3a5f","#0f4c3a","#3b1f5e","#5e1f2e","#5e4a1f"],
                        textinfo="label+percent", textfont_size=10))
                    fig_pie.update_layout(**PT, height=220, showlegend=False)
                    st.plotly_chart(fig_pie, use_container_width=True)
                with cb:
                    d = adf[["name","type","sector","weight","allocated","exp_return","volatility"]].copy()
                    d.columns = ["Asset","Type","Sector","Weight (%)","Invest (₹)","Exp. Return","Volatility"]
                    d["Weight (%)"] = d["Weight (%)"].apply(lambda x: f"{x}%")
                    d["Invest (₹)"] = d["Invest (₹)"].apply(lambda x: f"₹{x:,.2f}")
                    st.dataframe(d, use_container_width=True, hide_index=True)
                st.markdown("---")

            # Efficient Frontier
            st.markdown('<div class="section-header">Efficient Frontier</div>', unsafe_allow_html=True)
            all_df = pd.DataFrame(results)
            fig_ef = go.Figure()
            fig_ef.add_trace(go.Scatter(
                x=all_df["vol"], y=all_df["return"], mode="markers",
                marker=dict(size=4, color=all_df["sharpe"],
                            colorscale=[[0,"#1e2d40"],[0.5,"#3b82f6"],[1,"#00d4aa"]],
                            showscale=True,
                            colorbar=dict(title=dict(text="Sharpe", font=dict(color="#e2e8f0")),
                                          tickfont=dict(color="#e2e8f0"))),
                name="All portfolios", opacity=0.5,
            ))
            for i, row in top3.iterrows():
                fig_ef.add_trace(go.Scatter(
                    x=[row["vol"]], y=[row["return"]], mode="markers+text",
                    marker=dict(size=16, color=colors[i], symbol="star"),
                    text=[f"#{i+1}"], textposition="top center",
                    textfont=dict(color=colors[i], size=12), name=f"Pick #{i+1}",
                ))
            fig_ef.update_layout(**PT, height=360,
                xaxis=dict(title="Volatility (%)", showgrid=True, gridcolor="#1e2d40", color="#64748b"),
                yaxis=dict(title="Return (%)", showgrid=True, gridcolor="#1e2d40", color="#64748b"),
                legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e2d40"))
            st.plotly_chart(fig_ef, use_container_width=True)
            st.caption("Stars = your top 3 picks. Color = Sharpe ratio (brighter = better risk-adjusted return).")
