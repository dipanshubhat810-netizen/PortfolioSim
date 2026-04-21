import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# ─────────────────────────────────────────────────────────────────────────────
#  MOCK DATA — mirrors the exact portfolio_sim DB schema
#  Every function has the SQL query to replace it with when backend is ready.
#  Schema tables: accounts, profiles, sectors, assets, correlations,
#                 portfolios, portfolio_assets, portfolio_interests
# ─────────────────────────────────────────────────────────────────────────────

RISK_FREE_RATE       = 0.03
TOP_ASSETS_PER_SECTOR = 2
DEFAULT_CORRELATION  = 0.10

# ── Static reference data (mirrors sectors + assets tables) ──────────────────

SECTORS = {
    1: {"name": "Technology",  "description": "Software, hardware and internet companies"},
    2: {"name": "Healthcare",  "description": "Pharma, biotech and medical devices"},
    3: {"name": "Real Estate", "description": "REITs and property investment trusts"},
    4: {"name": "Energy",      "description": "Oil, gas and renewable energy companies"},
    5: {"name": "Finance",     "description": "Banks, insurance and financial services"},
    6: {"name": "Consumer",    "description": "Retail, FMCG and consumer goods"},
}

ASSETS = {
    1:  {"sector_id": 1, "name": "TechAlpha Fund",   "type": "Equity",   "expected_return": 0.1800, "volatility": 0.2200},
    2:  {"sector_id": 1, "name": "DataCore ETF",     "type": "Equity",   "expected_return": 0.1400, "volatility": 0.1600},
    3:  {"sector_id": 1, "name": "CloudBase Bond",   "type": "Bond",     "expected_return": 0.0700, "volatility": 0.0600},
    4:  {"sector_id": 2, "name": "MedGrowth Fund",   "type": "Equity",   "expected_return": 0.1300, "volatility": 0.1500},
    5:  {"sector_id": 2, "name": "PharmaStable ETF", "type": "Equity",   "expected_return": 0.1000, "volatility": 0.1100},
    6:  {"sector_id": 2, "name": "BioTech Bond",     "type": "Bond",     "expected_return": 0.0600, "volatility": 0.0500},
    7:  {"sector_id": 3, "name": "UrbanREIT",        "type": "Property", "expected_return": 0.0900, "volatility": 0.0800},
    8:  {"sector_id": 3, "name": "CommercialREIT",   "type": "Property", "expected_return": 0.0800, "volatility": 0.0700},
    9:  {"sector_id": 3, "name": "LandFund Bond",    "type": "Bond",     "expected_return": 0.0550, "volatility": 0.0400},
    10: {"sector_id": 4, "name": "OilCore ETF",      "type": "Equity",   "expected_return": 0.1100, "volatility": 0.1900},
    11: {"sector_id": 4, "name": "GreenPower Fund",  "type": "Equity",   "expected_return": 0.1200, "volatility": 0.1700},
    12: {"sector_id": 4, "name": "EnergyBond",       "type": "Bond",     "expected_return": 0.0650, "volatility": 0.0550},
    13: {"sector_id": 5, "name": "BankAlpha ETF",    "type": "Equity",   "expected_return": 0.1050, "volatility": 0.1200},
    14: {"sector_id": 5, "name": "InsureFund",       "type": "Equity",   "expected_return": 0.0950, "volatility": 0.1000},
    15: {"sector_id": 5, "name": "FinanceBond",      "type": "Bond",     "expected_return": 0.0600, "volatility": 0.0450},
    16: {"sector_id": 6, "name": "RetailGrowth ETF", "type": "Equity",   "expected_return": 0.0850, "volatility": 0.1000},
    17: {"sector_id": 6, "name": "FMCGStable Fund",  "type": "Equity",   "expected_return": 0.0750, "volatility": 0.0800},
    18: {"sector_id": 6, "name": "ConsumerBond",     "type": "Bond",     "expected_return": 0.0500, "volatility": 0.0350},
}

CORRELATIONS = {
    (1,2):0.720,(1,3):0.210,(2,3):0.180,
    (4,5):0.680,(4,6):0.150,(5,6):0.120,
    (7,8):0.830,(7,9):0.310,(8,9):0.280,
    (10,11):0.650,(10,12):0.200,(11,12):0.170,
    (13,14):0.710,(13,15):0.250,(14,15):0.220,
    (16,17):0.760,(16,18):0.190,(17,18):0.160,
    (1,13):0.450,(2,14):0.400,(1,14):0.350,
    (7,13):0.380,(8,14):0.360,
    (10,13):0.300,(11,14):0.280,
    (4,16):0.150,(5,17):0.140,
    (1,4):0.320,(2,5):0.290,
    (10,16):0.200,(11,17):0.180,
    (1,7):0.100,(2,8):0.100,(4,10):0.100,
}

DEMO_ACCOUNT = {"id": 1, "username": "demo_user", "email": "demo@example.com"}

DEMO_PROFILES = [
    {"id": 1, "acc_id": 1, "name": "Retirement Plan",   "age": 45, "income": 1200000.00, "risk_capacity": 4},
    {"id": 2, "acc_id": 1, "name": "Growth Portfolio",  "age": 28, "income": 800000.00,  "risk_capacity": 8},
]

# ── Helper ────────────────────────────────────────────────────────────────────

def get_risk_label(risk_capacity: int) -> str:
    """Maps risk_capacity 1-10 to a label. REPLACE WITH: modules/recommendations.py → get_risk_label()"""
    if risk_capacity <= 3:   return "conservative"
    elif risk_capacity <= 6: return "balanced"
    else:                    return "aggressive"


def get_correlation(a: int, b: int) -> float:
    """REPLACE WITH: SELECT correlation_value FROM correlations WHERE (asset_one_id=%s AND asset_two_id=%s)"""
    key = (min(a, b), max(a, b))
    return CORRELATIONS.get(key, DEFAULT_CORRELATION)


# ── Data access functions (one per DB table / query) ─────────────────────────

def get_all_sectors():
    """REPLACE WITH: SELECT id, name, description FROM sectors"""
    return [{"id": k, **v} for k, v in SECTORS.items()]


def get_assets_for_sectors(sector_ids: list) -> list:
    """REPLACE WITH: SELECT id, sector_id, name, type, expected_return, volatility
                     FROM assets WHERE sector_id IN (%s, ...)"""
    return [{"id": k, **v} for k, v in ASSETS.items() if v["sector_id"] in sector_ids]


def get_all_profiles(account_id: int = 1):
    """REPLACE WITH: SELECT id, acc_id, name, age, income, risk_capacity
                     FROM profiles WHERE acc_id = %s"""
    return [p for p in DEMO_PROFILES if p["acc_id"] == account_id]


def get_profile(profile_id: int):
    """REPLACE WITH: SELECT * FROM profiles WHERE id = %s"""
    for p in DEMO_PROFILES:
        if p["id"] == profile_id:
            return p
    return None


def get_recommended_portfolios(profile_id: int):
    """
    REPLACE WITH:
      SELECT p.id, pr.name, p.base_amount, p.recommended_type
      FROM portfolios p JOIN profiles pr ON p.profile_id = pr.id
      WHERE p.recommended_type = %s AND p.status = 'active'
    """
    profile = get_profile(profile_id)
    label   = get_risk_label(profile["risk_capacity"])
    samples = [
        {"id": 101, "name": "Safe Harbour",     "base_amount": 500000, "recommended_type": "conservative"},
        {"id": 102, "name": "Steady Climber",   "base_amount": 300000, "recommended_type": "conservative"},
        {"id": 103, "name": "Balanced Blend",   "base_amount": 400000, "recommended_type": "balanced"},
        {"id": 104, "name": "Market Rider",     "base_amount": 250000, "recommended_type": "balanced"},
        {"id": 105, "name": "Growth Engine",    "base_amount": 200000, "recommended_type": "aggressive"},
        {"id": 106, "name": "High Voltage",     "base_amount": 150000, "recommended_type": "aggressive"},
    ]
    return [s for s in samples if s["recommended_type"] == label]


def get_active_portfolio(profile_id: int):
    """
    REPLACE WITH:
      SELECT po.*, pa.asset_id, pa.weight, pa.snapshot_expected_return,
             a.name, a.volatility, a.type
      FROM portfolios po
      JOIN portfolio_assets pa ON po.id = pa.portfolio_id
      JOIN assets a ON pa.asset_id = a.id
      WHERE po.profile_id = %s AND po.status = 'active'
    """
    if profile_id == 1:
        return {
            "id": 1, "profile_id": 1, "base_amount": 500000.00,
            "recommended_type": "conservative", "status": "active",
            "created_at": "2024-11-01",
            "assets": [
                {"asset_id": 7,  "name": "UrbanREIT",        "weight": 0.20, "snapshot_expected_return": 0.0900, "volatility": 0.0800, "type": "Property"},
                {"asset_id": 8,  "name": "CommercialREIT",   "weight": 0.15, "snapshot_expected_return": 0.0800, "volatility": 0.0700, "type": "Property"},
                {"asset_id": 13, "name": "BankAlpha ETF",    "weight": 0.18, "snapshot_expected_return": 0.1050, "volatility": 0.1200, "type": "Equity"},
                {"asset_id": 14, "name": "InsureFund",       "weight": 0.17, "snapshot_expected_return": 0.0950, "volatility": 0.1000, "type": "Equity"},
                {"asset_id": 16, "name": "RetailGrowth ETF", "weight": 0.16, "snapshot_expected_return": 0.0850, "volatility": 0.1000, "type": "Equity"},
                {"asset_id": 17, "name": "FMCGStable Fund",  "weight": 0.14, "snapshot_expected_return": 0.0750, "volatility": 0.0800, "type": "Equity"},
            ]
        }
    return None


def get_portfolio_history(profile_id: int, days: int = 180):
    """
    REPLACE WITH: Compute daily portfolio value from portfolio_assets + simulate
                  or store snapshots in a new portfolio_snapshots table
    """
    np.random.seed(profile_id * 7)
    base   = 500000 if profile_id == 1 else 300000
    dates  = pd.date_range(end=datetime.today(), periods=days, freq="B")
    values = [base]
    for _ in range(days - 1):
        values.append(round(values[-1] * (1 + np.random.normal(0.0005, 0.010)), 2))
    return pd.DataFrame({"date": dates, "value": values})


# ── Markowitz engine (mirrors modules/engine.py) ──────────────────────────────

def compute_sharpe(expected_return: float, volatility: float) -> float:
    """mirrors engine.compute_sharpe() — REPLACE WITH: modules/engine.py"""
    if volatility == 0: return 0
    return (expected_return - RISK_FREE_RATE) / volatility


def rank_and_filter_assets(assets: list, top_n: int = TOP_ASSETS_PER_SECTOR) -> list:
    """mirrors engine.rank_and_filter_assets() — REPLACE WITH: modules/engine.py"""
    by_sector = {}
    for a in assets:
        by_sector.setdefault(a["sector_id"], []).append(a)
    result = []
    for sector_assets in by_sector.values():
        ranked = sorted(sector_assets, key=lambda x: compute_sharpe(x["expected_return"], x["volatility"]), reverse=True)
        result.extend(ranked[:top_n])
    return result


def compute_weights(assets: list, risk_capacity: int) -> dict:
    """mirrors engine.compute_weights() — REPLACE WITH: modules/engine.py"""
    if risk_capacity < 5:
        raw = {a["id"]: 1 / a["volatility"] for a in assets}
    else:
        raw = {a["id"]: a["expected_return"] for a in assets}
    total = sum(raw.values())
    return {k: round(v / total, 4) for k, v in raw.items()}


def compute_portfolio_variance(assets: list, weights: dict) -> float:
    """mirrors engine.compute_portfolio_variance() — full Markowitz formula"""
    variance = 0.0
    for a in assets:
        variance += (weights[a["id"]] ** 2) * (a["volatility"] ** 2)
    for i, a in enumerate(assets):
        for j, b in enumerate(assets):
            if i < j:
                corr = get_correlation(a["id"], b["id"])
                variance += 2 * weights[a["id"]] * weights[b["id"]] * corr * a["volatility"] * b["volatility"]
    return round(variance, 6)


def compute_portfolio_return(assets: list, weights: dict) -> float:
    """mirrors engine.compute_portfolio_return()"""
    return round(sum(weights[a["id"]] * a["expected_return"] for a in assets), 4)


def generate_portfolio_preview(profile_id: int, sector_ids: list, base_amount: float) -> dict:
    """
    mirrors engine.generate_portfolio_preview()
    REPLACE WITH: POST /api/generate { profile_id, sector_ids, base_amount }
    """
    profile  = get_profile(profile_id)
    assets   = get_assets_for_sectors(sector_ids)
    filtered = rank_and_filter_assets(assets)
    weights  = compute_weights(filtered, profile["risk_capacity"])
    exp_ret  = compute_portfolio_return(filtered, weights)
    variance = compute_portfolio_variance(filtered, weights)
    label    = get_risk_label(profile["risk_capacity"])

    return {
        "profile_id":         profile_id,
        "base_amount":        base_amount,
        "recommended_type":   label,
        "expected_return":    exp_ret,
        "portfolio_variance": variance,
        "sector_ids":         sector_ids,
        "assets": [
            {
                "asset_id":        a["id"],
                "name":            a["name"],
                "type":            a["type"],
                "sector":          SECTORS[a["sector_id"]]["name"],
                "weight":          weights[a["id"]],
                "expected_return": a["expected_return"],
                "volatility":      a["volatility"],
                "allocated":       round(base_amount * weights[a["id"]], 2),
            }
            for a in filtered
        ]
    }


# ── Simulation (mirrors modules/simulation.py) ────────────────────────────────

def generate_market_sentiment() -> float:
    """mirrors simulation.generate_market_sentiment() — random float -1 to 1"""
    return random.uniform(-1, 1)


def compute_portfolio_value(active_portfolio: dict) -> dict:
    """
    mirrors simulation.compute_portfolio_value()
    REPLACE WITH: call simulation module directly — no DB writes needed
    """
    sentiment  = generate_market_sentiment()
    base       = active_portfolio["base_amount"]
    asset_rows = []
    total_now  = 0.0

    for a in active_portfolio["assets"]:
        allocated = round(base * a["weight"], 2)
        current   = round(allocated * (1 + a["snapshot_expected_return"] + sentiment * a["volatility"]), 2)
        total_now += current
        asset_rows.append({
            "name":      a["name"],
            "type":      a["type"],
            "weight":    a["weight"],
            "allocated": allocated,
            "current":   current,
            "change":    round(current - allocated, 2),
            "change_pct": round((current - allocated) / allocated * 100, 2),
        })

    change_pct = round((total_now - base) / base * 100, 2)
    return {
        "base_amount":   base,
        "current_value": round(total_now, 2),
        "change_pct":    change_pct,
        "sentiment":     round(sentiment, 3),
        "assets":        asset_rows,
    }


def save_portfolio(profile_id: int, preview: dict) -> dict:
    """
    REPLACE WITH: modules/portfolio.py → save_portfolio()
      BEGIN TRANSACTION
        INSERT INTO portfolios (profile_id, base_amount, recommended_type, status)
        UPDATE old portfolio SET status='inactive' WHERE profile_id=%s
        INSERT INTO portfolio_interests (portfolio_id, sector_id) for each sector
        INSERT INTO portfolio_assets (portfolio_id, asset_id, weight, snapshot_expected_return)
      COMMIT
    """
    return {"success": True, "portfolio_id": random.randint(100, 999),
            "message": "Portfolio saved and set as active."}
