import streamlit as st
import pandas as pd
import json
from datetime import datetime
import io

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GHG Carbon Calculator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg:       #0d1117;
    --surface:  #161b22;
    --border:   #21262d;
    --accent:   #2ea043;
    --accent2:  #388bfd;
    --warn:     #f0883e;
    --danger:   #da3633;
    --muted:    #8b949e;
    --text:     #e6edf3;
    --head:     #f0f6fc;
}

html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border);
}

h1, h2, h3 { font-family: 'DM Serif Display', serif; color: var(--head); }

/* KPI cards */
.kpi-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 20px 24px;
    text-align: center;
}
.kpi-label {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1.5px;
    color: var(--muted);
    margin-bottom: 6px;
}
.kpi-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: var(--head);
    line-height: 1;
}
.kpi-unit {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--muted);
    margin-top: 4px;
}

/* Section headers */
.section-tag {
    display: inline-block;
    background: rgba(46,160,67,0.15);
    color: var(--accent);
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 4px;
    margin-bottom: 8px;
}
.scope-header {
    font-family: 'DM Serif Display', serif;
    font-size: 1.3rem;
    color: var(--head);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin-bottom: 16px;
}

/* Factor badge */
.ef-badge {
    background: rgba(56,139,253,0.15);
    color: var(--accent2);
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
}

/* Override Streamlit inputs */
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] select {
    background: #0d1117 !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
}

.stButton>button {
    background: var(--accent);
    color: #fff;
    border: none;
    border-radius: 6px;
    font-family: 'DM Sans', sans-serif;
    font-weight: 600;
    padding: 8px 20px;
}
.stButton>button:hover { background: #3fb950; }

div[data-testid="metric-container"] {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 16px;
}

footer { display: none; }
</style>
""", unsafe_allow_html=True)


# ─── SESSION STATE INIT ───────────────────────────────────────────────────────
def init_state():
    defaults = {
        # Assumptions
        "company_name": "My Company",
        "industry": "Technology",
        "country": "United States",
        "reporting_year": 2025,
        "prior_year": 2024,
        "revenue_musd": 0.0,
        "employees": 0,
        # GWP
        "gwp_ch4_fossil": 29.8,
        "gwp_n2o": 273.0,
        "gwp_hfc134a": 1526.0,
        "gwp_sf6": 25200.0,
        # Scope 1 — Stationary
        "s1_natgas_mmbtu": 0.0,
        "s1_diesel_litres": 0.0,
        "s1_lpg_litres": 0.0,
        "s1_coal_shorttons": 0.0,
        # Scope 1 — Mobile
        "s1_gasoline_litres": 0.0,
        "s1_diesel_fleet_litres": 0.0,
        "s1_jet_litres": 0.0,
        # Scope 1 — Fugitive
        "s1_hfc134a_kg": 0.0,
        "s1_hfc410a_kg": 0.0,
        "s1_sf6_kg": 0.0,
        # Scope 2
        "s2_elec_mwh": 0.0,
        "s2_grid_ef": 386.0,
        "s2_market_ef": 0.0,
        "s2_recs_mwh": 0.0,
        "s2_steam_gj": 0.0,
        # Scope 3
        "s3_cat1_spend": 0.0,
        "s3_cat1_ef": 0.35,
        "s3_cat3_elec_mwh": 0.0,
        "s3_cat6_air_km": 0.0,
        "s3_cat6_rail_km": 0.0,
        "s3_cat7_km_per_emp": 0.0,
        "s3_cat11_units": 0.0,
        "s3_cat11_ef": 0.0,
        # Prior year totals (for intensity trend)
        "prior_s1": 0.0,
        "prior_s2mb": 0.0,
        "prior_s3": 0.0,
        # Targets
        "target_year": 2030,
        "target_reduction_pct": 50.0,
        "target_baseline": 0.0,
        # Industry benchmark
        "benchmark_revenue_intensity": 0.0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── EMISSION FACTORS (locked, EPA/DEFRA/IEA 2023) ───────────────────────────
EF = {
    # Stationary (kgCO2/unit)
    "natgas_co2": 53.06,   # per MMBtu
    "natgas_ch4": 1.0,     # g/MMBtu
    "natgas_n2o": 0.1,     # g/MMBtu
    "diesel_co2": 2.663,   # per litre
    "diesel_ch4": 0.139,
    "diesel_n2o": 0.014,
    "lpg_co2": 1.555,
    "lpg_ch4": 0.0617,
    "lpg_n2o": 0.0062,
    "coal_co2": 2325.0,    # per short ton
    "coal_ch4": 274.0,
    "coal_n2o": 40.0,
    # Mobile
    "gasoline_co2": 2.312,
    "gasoline_ch4": 0.339,
    "gasoline_n2o": 0.033,
    "jet_co2": 2.553,
    # Fugitive GWP (kgCO2e per kg)
    "hfc134a_gwp": 1526,
    "hfc410a_gwp": 2088,
    "sf6_gwp": 22800,
    # Scope 3
    "s3_cat3_td_loss": 0.05,   # 5% T&D loss on electricity
    "s3_cat6_air": 0.255,       # kgCO2e/km
    "s3_cat6_rail": 0.041,      # kgCO2e/km
    "s3_cat7_car": 0.170,       # kgCO2e/km
    "s2_steam_ef": 66.4,        # kgCO2e/GJ
}

# ─── CALCULATIONS ─────────────────────────────────────────────────────────────
def calc_scope1():
    s = st.session_state
    gwp_ch4 = s["gwp_ch4_fossil"]
    gwp_n2o = s["gwp_n2o"]

    def co2e(co2_kg, ch4_g, n2o_g, qty):
        return (
            co2_kg * qty / 1000,
            ch4_g * qty / 1e6 * gwp_ch4,
            n2o_g * qty / 1e6 * gwp_n2o,
        )

    results = {}
    results["natgas"] = co2e(EF["natgas_co2"], EF["natgas_ch4"], EF["natgas_n2o"], s["s1_natgas_mmbtu"])
    results["diesel"] = co2e(EF["diesel_co2"], EF["diesel_ch4"], EF["diesel_n2o"], s["s1_diesel_litres"])
    results["lpg"]    = co2e(EF["lpg_co2"],    EF["lpg_ch4"],    EF["lpg_n2o"],    s["s1_lpg_litres"])
    results["coal"]   = co2e(EF["coal_co2"],   EF["coal_ch4"],   EF["coal_n2o"],   s["s1_coal_shorttons"])
    results["gas_fleet"] = co2e(EF["gasoline_co2"], EF["gasoline_ch4"], EF["gasoline_n2o"], s["s1_gasoline_litres"])
    results["diesel_fleet"] = co2e(EF["diesel_co2"], EF["diesel_ch4"], EF["diesel_n2o"], s["s1_diesel_fleet_litres"])
    results["jet"] = (EF["jet_co2"] * s["s1_jet_litres"] / 1000, 0, 0)

    # Fugitive
    fug_hfc134a = s["s1_hfc134a_kg"] * s["gwp_hfc134a"] / 1000
    fug_hfc410a = s["s1_hfc410a_kg"] * EF["hfc410a_gwp"] / 1000
    fug_sf6     = s["s1_sf6_kg"]     * s["gwp_sf6"] / 1000
    results["fugitive"] = (fug_hfc134a + fug_hfc410a + fug_sf6, 0, 0)

    total = sum(sum(v) for v in results.values())
    return results, total

def calc_scope2():
    s = st.session_state
    net_market_mwh = max(0, s["s2_elec_mwh"] - s["s2_recs_mwh"])
    location_based = s["s2_elec_mwh"] * s["s2_grid_ef"] / 1000
    market_based   = net_market_mwh * s["s2_market_ef"] / 1000
    steam          = s["s2_steam_gj"] * EF["s2_steam_ef"] / 1000
    return {
        "location_based": location_based + steam,
        "market_based": market_based + steam,
        "net_market_mwh": net_market_mwh,
    }

def calc_scope3():
    s = st.session_state
    cat1 = s["s3_cat1_spend"] * s["s3_cat1_ef"] / 1000   # spend ($000s) × ef → tCO2e
    cat3 = s["s3_cat3_elec_mwh"] * s["s2_grid_ef"] * EF["s3_cat3_td_loss"] / 1000
    cat6 = (s["s3_cat6_air_km"] * EF["s3_cat6_air"] + s["s3_cat6_rail_km"] * EF["s3_cat6_rail"]) / 1000
    cat7 = s["s3_cat7_km_per_emp"] * s["employees"] * EF["s3_cat7_car"] / 1000
    cat11 = s["s3_cat11_units"] * s["s3_cat11_ef"] / 1000
    total = cat1 + cat3 + cat6 + cat7 + cat11
    return {"cat1": cat1, "cat3": cat3, "cat6": cat6, "cat7": cat7, "cat11": cat11, "total": total}

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🌍 GHG Calculator")
    st.caption("GHG Protocol Framework")
    st.divider()

    page = st.radio(
        "Navigate",
        ["🏠 Assumptions", "🔥 Scope 1", "⚡ Scope 2", "🔗 Scope 3", "📊 Dashboard", "📄 Report"],
        label_visibility="collapsed",
    )
    st.divider()

    # Quick totals preview
    _, s1_total = calc_scope1()
    s2 = calc_scope2()
    s3 = calc_scope3()
    grand_total = s1_total + s2["market_based"] + s3["total"]

    st.markdown("**Live Totals**")
    st.metric("Scope 1", f"{s1_total:,.0f} tCO₂e")
    st.metric("Scope 2 (MB)", f"{s2['market_based']:,.0f} tCO₂e")
    st.metric("Scope 3", f"{s3['total']:,.0f} tCO₂e")
    st.metric("**TOTAL**", f"{grand_total:,.0f} tCO₂e")


# ─── PAGE: ASSUMPTIONS ────────────────────────────────────────────────────────
if page == "🏠 Assumptions":
    st.markdown('<div class="section-tag">Step 1</div>', unsafe_allow_html=True)
    st.title("Central Assumptions")
    st.caption("All scopes reference these values. Fill this page first.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Company Info")
        st.session_state["company_name"] = st.text_input("Company Name", st.session_state["company_name"])
        st.session_state["industry"] = st.selectbox("Industry / Sector", [
            "Technology", "Manufacturing", "Retail", "Financial Services",
            "Healthcare", "Energy", "Real Estate", "Transportation", "Food & Beverage", "Other"
        ], index=["Technology","Manufacturing","Retail","Financial Services",
                  "Healthcare","Energy","Real Estate","Transportation","Food & Beverage","Other"].index(st.session_state["industry"]))
        st.session_state["country"] = st.selectbox("Primary Country of Operations", [
            "United States", "United Kingdom", "Germany", "France", "China",
            "India", "Japan", "Australia", "Brazil", "Canada", "Other"
        ])
        st.session_state["reporting_year"] = st.number_input("Reporting Year", min_value=2000, max_value=2030,
                                                               value=st.session_state["reporting_year"])

    with col2:
        st.markdown("#### Financial Metrics")
        st.session_state["revenue_musd"] = st.number_input(
            "Annual Revenue (USD Millions)", min_value=0.0,
            value=st.session_state["revenue_musd"], step=100.0,
            help="Used for carbon intensity ratios")
        st.session_state["employees"] = st.number_input(
            "Number of Employees (FTE)", min_value=0,
            value=st.session_state["employees"], step=100,
            help="Used for per-employee intensity")
        st.session_state["prior_s1"] = st.number_input("Prior Year — Scope 1 (tCO₂e)", min_value=0.0, value=st.session_state["prior_s1"])
        st.session_state["prior_s2mb"] = st.number_input("Prior Year — Scope 2 MB (tCO₂e)", min_value=0.0, value=st.session_state["prior_s2mb"])
        st.session_state["prior_s3"] = st.number_input("Prior Year — Scope 3 (tCO₂e)", min_value=0.0, value=st.session_state["prior_s3"])

    st.divider()
    st.markdown("#### GWP Factors — IPCC AR6 (2021)")
    st.caption("Change only if your regulatory regime requires a different AR version.")
    gc1, gc2, gc3, gc4 = st.columns(4)
    with gc1:
        st.session_state["gwp_ch4_fossil"] = st.number_input("CH₄ (fossil) GWP", value=st.session_state["gwp_ch4_fossil"])
    with gc2:
        st.session_state["gwp_n2o"] = st.number_input("N₂O GWP", value=st.session_state["gwp_n2o"])
    with gc3:
        st.session_state["gwp_hfc134a"] = st.number_input("HFC-134a GWP", value=st.session_state["gwp_hfc134a"])
    with gc4:
        st.session_state["gwp_sf6"] = st.number_input("SF₆ GWP", value=st.session_state["gwp_sf6"])

    st.divider()
    st.markdown("#### Reduction Targets")
    t1, t2, t3 = st.columns(3)
    with t1:
        st.session_state["target_year"] = st.number_input("Target Year", min_value=2025, max_value=2050, value=st.session_state["target_year"])
    with t2:
        st.session_state["target_reduction_pct"] = st.slider("Reduction Target (%)", 0, 100, int(st.session_state["target_reduction_pct"]))
    with t3:
        st.session_state["target_baseline"] = st.number_input("Baseline Emissions (tCO₂e)", min_value=0.0, value=st.session_state["target_baseline"])

    if st.session_state["target_baseline"] > 0:
        target_val = st.session_state["target_baseline"] * (1 - st.session_state["target_reduction_pct"] / 100)
        years_left = st.session_state["target_year"] - st.session_state["reporting_year"]
        annual = (st.session_state["target_baseline"] - target_val) / max(1, years_left)
        st.info(f"🎯 Target: **{target_val:,.0f} tCO₂e** by {st.session_state['target_year']} — requires **{annual:,.0f} tCO₂e/year** reduction")

    st.session_state["benchmark_revenue_intensity"] = st.number_input(
        "Industry Benchmark — Carbon Intensity (tCO₂e / $M revenue)", min_value=0.0,
        value=st.session_state["benchmark_revenue_intensity"],
        help="Leave 0 if unknown. Used in dashboard comparison.")


# ─── PAGE: SCOPE 1 ────────────────────────────────────────────────────────────
elif page == "🔥 Scope 1":
    st.markdown('<div class="section-tag">Direct Emissions</div>', unsafe_allow_html=True)
    st.title("Scope 1 — Direct GHG Emissions")
    st.caption("Sources your organization directly controls: combustion, fleet, and fugitives.")

    results, s1_total = calc_scope1()

    # KPI header
    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Scope 1 Total</div>
            <div class="kpi-value">{s1_total:,.0f}</div>
            <div class="kpi-unit">tCO₂e</div></div>""", unsafe_allow_html=True)
    with k2:
        stationary = sum(sum(results[k]) for k in ["natgas","diesel","lpg","coal"])
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Stationary Combustion</div>
            <div class="kpi-value">{stationary:,.0f}</div>
            <div class="kpi-unit">tCO₂e</div></div>""", unsafe_allow_html=True)
    with k3:
        fug = sum(results["fugitive"])
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Fugitive Emissions</div>
            <div class="kpi-value">{fug:,.0f}</div>
            <div class="kpi-unit">tCO₂e</div></div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Part A — Stationary
    st.markdown('<p class="scope-header">Part A — Stationary Combustion</p>', unsafe_allow_html=True)

    fuel_rows = [
        ("Natural Gas", "s1_natgas_mmbtu", "MMBtu", EF["natgas_co2"], "natgas"),
        ("Diesel / Fuel Oil No.2", "s1_diesel_litres", "Litres", EF["diesel_co2"], "diesel"),
        ("LPG", "s1_lpg_litres", "Litres", EF["lpg_co2"], "lpg"),
        ("Coal (Bituminous)", "s1_coal_shorttons", "Short Tons", EF["coal_co2"] / 1000, "coal"),
    ]

    for label, key, unit, ef, rkey in fuel_rows:
        with st.expander(f"**{label}** — {sum(results[rkey]):,.2f} tCO₂e", expanded=False):
            c1, c2, c3 = st.columns([3, 2, 2])
            with c1:
                st.session_state[key] = st.number_input(
                    f"Activity Quantity ({unit})", min_value=0.0,
                    value=st.session_state[key], key=f"inp_{key}",
                    step=1.0 if "tons" in unit.lower() else 100.0)
            with c2:
                st.markdown(f'<br><span class="ef-badge">CO₂ EF: {ef:.3f} kgCO₂/{unit}</span>', unsafe_allow_html=True)
            with c3:
                st.metric("Calculated", f"{sum(results[rkey]):,.2f} tCO₂e")

    st.divider()
    # Part B — Mobile
    st.markdown('<p class="scope-header">Part B — Mobile Combustion (Fleet)</p>', unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)
    with m1:
        st.session_state["s1_gasoline_litres"] = st.number_input(
            "Gasoline / Petrol (Litres)", min_value=0.0, value=st.session_state["s1_gasoline_litres"], step=100.0)
    with m2:
        st.session_state["s1_diesel_fleet_litres"] = st.number_input(
            "Diesel Fleet (Litres)", min_value=0.0, value=st.session_state["s1_diesel_fleet_litres"], step=100.0)
    with m3:
        st.session_state["s1_jet_litres"] = st.number_input(
            "Aviation Fuel / Jet-A (Litres)", min_value=0.0, value=st.session_state["s1_jet_litres"], step=100.0)

    st.divider()
    # Part C — Fugitive
    st.markdown('<p class="scope-header">Part C — Fugitive Emissions (Refrigerants)</p>', unsafe_allow_html=True)
    f1, f2, f3 = st.columns(3)
    with f1:
        st.session_state["s1_hfc134a_kg"] = st.number_input("HFC-134a leaked (kg)", min_value=0.0, value=st.session_state["s1_hfc134a_kg"])
    with f2:
        st.session_state["s1_hfc410a_kg"] = st.number_input("HFC-410A leaked (kg)", min_value=0.0, value=st.session_state["s1_hfc410a_kg"])
    with f3:
        st.session_state["s1_sf6_kg"] = st.number_input("SF₆ leaked (kg)", min_value=0.0, value=st.session_state["s1_sf6_kg"])


# ─── PAGE: SCOPE 2 ────────────────────────────────────────────────────────────
elif page == "⚡ Scope 2":
    st.markdown('<div class="section-tag">Purchased Energy</div>', unsafe_allow_html=True)
    st.title("Scope 2 — Purchased Energy")
    st.caption("Dual reporting required by GHG Protocol: Location-Based and Market-Based.")

    s2 = calc_scope2()

    k1, k2, k3 = st.columns(3)
    with k1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Location-Based</div>
            <div class="kpi-value">{s2['location_based']:,.0f}</div>
            <div class="kpi-unit">tCO₂e</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Market-Based (Primary)</div>
            <div class="kpi-value">{s2['market_based']:,.0f}</div>
            <div class="kpi-unit">tCO₂e</div></div>""", unsafe_allow_html=True)
    with k3:
        recs_pct = (st.session_state["s2_recs_mwh"] / max(1, st.session_state["s2_elec_mwh"])) * 100
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Renewable Coverage</div>
            <div class="kpi-value">{recs_pct:.1f}%</div>
            <div class="kpi-unit">of electricity</div></div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<p class="scope-header">Part A — Purchased Electricity</p>', unsafe_allow_html=True)
    ea, eb, ec = st.columns(3)
    with ea:
        st.session_state["s2_elec_mwh"] = st.number_input(
            "Total Electricity Consumed (MWh)", min_value=0.0,
            value=st.session_state["s2_elec_mwh"], step=100.0)
    with eb:
        country_ef = {
            "United States": 386, "United Kingdom": 207, "Germany": 380,
            "China": 581, "India": 713, "Japan": 471,
            "Australia": 680, "Brazil": 119, "Canada": 130,
            "European Union": 231,
        }
        country = st.session_state.get("country", "United States")
        default_ef = country_ef.get(country, 386)
        st.session_state["s2_grid_ef"] = st.number_input(
            "Location-Based Grid EF (kgCO₂e/MWh)",
            min_value=0.0, value=float(default_ef), step=1.0,
            help=f"Auto-suggested for {country}: {default_ef} kgCO₂e/MWh (IEA 2023)")
    with ec:
        st.session_state["s2_market_ef"] = st.number_input(
            "Market-Based Supplier EF (kgCO₂e/MWh)", min_value=0.0,
            value=st.session_state["s2_market_ef"], step=1.0,
            help="From your energy supplier contract or residual mix")

    st.session_state["s2_recs_mwh"] = st.slider(
        "RECs / PPAs Covered (MWh)", min_value=0.0,
        max_value=max(st.session_state["s2_elec_mwh"], 1.0),
        value=min(st.session_state["s2_recs_mwh"], st.session_state["s2_elec_mwh"]),
        step=100.0)
    st.info(f"Net Market-Based MWh (after RECs): **{s2['net_market_mwh']:,.0f} MWh**")

    st.divider()
    st.markdown('<p class="scope-header">Part B — Purchased Steam / Heat / Cooling</p>', unsafe_allow_html=True)
    st.session_state["s2_steam_gj"] = st.number_input(
        "Purchased Steam / Heat / Cooling (GJ)", min_value=0.0,
        value=st.session_state["s2_steam_gj"],
        help=f"Default EF: {EF['s2_steam_ef']} kgCO₂e/GJ")


# ─── PAGE: SCOPE 3 ────────────────────────────────────────────────────────────
elif page == "🔗 Scope 3":
    st.markdown('<div class="section-tag">Value Chain</div>', unsafe_allow_html=True)
    st.title("Scope 3 — Value Chain Emissions")
    st.caption("Typically 70–90% of total footprint. Cover categories most material to your industry.")

    s3 = calc_scope3()
    k1, k2 = st.columns([1, 3])
    with k1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Scope 3 Total</div>
            <div class="kpi-value">{s3['total']:,.0f}</div>
            <div class="kpi-unit">tCO₂e</div></div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Cat 1
    with st.expander(f"**Cat 1 — Purchased Goods & Services** (spend-based) — {s3['cat1']:,.1f} tCO₂e"):
        c1a, c1b, c1c = st.columns(3)
        with c1a:
            st.session_state["s3_cat1_spend"] = st.number_input(
                "Annual Spend ($000s USD)", min_value=0.0,
                value=st.session_state["s3_cat1_spend"], step=1000.0)
        with c1b:
            st.session_state["s3_cat1_ef"] = st.number_input(
                "EEIO Factor (kgCO₂e per $)", min_value=0.0,
                value=st.session_state["s3_cat1_ef"], step=0.01,
                help="US EPA USEEIO v2.0. Typical range: 0.12–0.95 depending on spend category")
        with c1c:
            st.metric("Result", f"{s3['cat1']:,.1f} tCO₂e")

    # Cat 3
    with st.expander(f"**Cat 3 — Fuel & Energy-Related (T&D Losses)** — {s3['cat3']:,.1f} tCO₂e"):
        st.session_state["s3_cat3_elec_mwh"] = st.number_input(
            "Electricity consumed (MWh) — same as Scope 2 usually",
            min_value=0.0, value=st.session_state["s3_cat3_elec_mwh"], step=100.0,
            help=f"5% T&D loss factor applied × your grid EF ({st.session_state['s2_grid_ef']} kgCO₂e/MWh)")
        st.metric("Result", f"{s3['cat3']:,.1f} tCO₂e")

    # Cat 6
    with st.expander(f"**Cat 6 — Business Travel** — {s3['cat6']:,.1f} tCO₂e"):
        b1, b2 = st.columns(2)
        with b1:
            st.session_state["s3_cat6_air_km"] = st.number_input(
                "Total Air Travel (km)", min_value=0.0,
                value=st.session_state["s3_cat6_air_km"], step=1000.0,
                help=f"EF: {EF['s3_cat6_air']} kgCO₂e/km (economy, DEFRA 2023)")
        with b2:
            st.session_state["s3_cat6_rail_km"] = st.number_input(
                "Total Rail Travel (km)", min_value=0.0,
                value=st.session_state["s3_cat6_rail_km"], step=1000.0,
                help=f"EF: {EF['s3_cat6_rail']} kgCO₂e/km")
        st.metric("Result", f"{s3['cat6']:,.1f} tCO₂e")

    # Cat 7
    with st.expander(f"**Cat 7 — Employee Commuting** — {s3['cat7']:,.1f} tCO₂e"):
        st.session_state["s3_cat7_km_per_emp"] = st.number_input(
            "Average commute distance per employee per year (km)", min_value=0.0,
            value=st.session_state["s3_cat7_km_per_emp"], step=100.0,
            help=f"Applied to {st.session_state['employees']:,} employees × {EF['s3_cat7_car']} kgCO₂e/km")
        st.metric("Result", f"{s3['cat7']:,.1f} tCO₂e")

    # Cat 11
    with st.expander(f"**Cat 11 — Use of Sold Products** — {s3['cat11']:,.1f} tCO₂e"):
        u1, u2 = st.columns(2)
        with u1:
            st.session_state["s3_cat11_units"] = st.number_input(
                "Units / product-years in use", min_value=0.0,
                value=st.session_state["s3_cat11_units"], step=1000.0)
        with u2:
            st.session_state["s3_cat11_ef"] = st.number_input(
                "Lifecycle EF (kgCO₂e per unit)", min_value=0.0,
                value=st.session_state["s3_cat11_ef"], step=0.1)
        st.metric("Result", f"{s3['cat11']:,.1f} tCO₂e")


# ─── PAGE: DASHBOARD ─────────────────────────────────────────────────────────
elif page == "📊 Dashboard":
    st.markdown('<div class="section-tag">Executive Summary</div>', unsafe_allow_html=True)
    company = st.session_state["company_name"]
    year = st.session_state["reporting_year"]
    st.title(f"{company} — Carbon Footprint {year}")

    _, s1_total = calc_scope1()
    s2 = calc_scope2()
    s3 = calc_scope3()
    grand_mb = s1_total + s2["market_based"] + s3["total"]

    # Top KPIs
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">🔥 Scope 1</div>
            <div class="kpi-value">{s1_total:,.0f}</div>
            <div class="kpi-unit">tCO₂e — Direct</div></div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">⚡ Scope 2 (MB)</div>
            <div class="kpi-value">{s2['market_based']:,.0f}</div>
            <div class="kpi-unit">tCO₂e — Market-Based</div></div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">🔗 Scope 3</div>
            <div class="kpi-value">{s3['total']:,.0f}</div>
            <div class="kpi-unit">tCO₂e — Value Chain</div></div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">📊 Total (S1+S2+S3)</div>
            <div class="kpi-value">{grand_mb:,.0f}</div>
            <div class="kpi-unit">tCO₂e</div></div>""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    # Intensity ratios
    st.markdown("#### Carbon Intensity Ratios")
    rev = st.session_state["revenue_musd"]
    emp = st.session_state["employees"]

    prior_grand = st.session_state["prior_s1"] + st.session_state["prior_s2mb"] + st.session_state["prior_s3"]

    intensity_data = []
    if rev > 0:
        curr_ri = grand_mb / rev
        prior_ri = prior_grand / rev if prior_grand > 0 else None
        change_ri = (curr_ri - prior_ri) / prior_ri * 100 if prior_ri else None
        intensity_data.append(("Revenue Intensity", f"{curr_ri:.2f}", "tCO₂e / $M revenue",
                                f"{change_ri:+.1f}%" if change_ri else "—"))
    if emp > 0:
        curr_ei = grand_mb / emp
        prior_ei = prior_grand / emp if prior_grand > 0 else None
        change_ei = (curr_ei - prior_ei) / prior_ei * 100 if prior_ei else None
        intensity_data.append(("Employee Intensity", f"{curr_ei:.2f}", "tCO₂e / employee",
                                f"{change_ei:+.1f}%" if change_ei else "—"))

    if intensity_data:
        for metric, value, unit, change in intensity_data:
            ic1, ic2, ic3, ic4 = st.columns([3, 2, 2, 2])
            with ic1: st.markdown(f"**{metric}**")
            with ic2: st.markdown(f"`{value} {unit}`")
            with ic3: st.markdown(f"YoY: **{change}**")
    else:
        st.info("Enter Revenue and Employees in Assumptions to see intensity ratios.")

    st.divider()

    # Scope breakdown table
    st.markdown("#### Scope Breakdown")
    scope_df = pd.DataFrame({
        "Scope": ["Scope 1 — Direct", "Scope 2 — Market-Based", "Scope 2 — Location-Based (suppl.)", "Scope 3 — Value Chain", "TOTAL (S1+S2MB+S3)"],
        "tCO₂e": [s1_total, s2["market_based"], s2["location_based"], s3["total"], grand_mb],
        "% of Total": [
            f"{s1_total/grand_mb*100:.1f}%" if grand_mb > 0 else "—",
            f"{s2['market_based']/grand_mb*100:.1f}%" if grand_mb > 0 else "—",
            "Supplemental",
            f"{s3['total']/grand_mb*100:.1f}%" if grand_mb > 0 else "—",
            "100%"
        ]
    })
    st.dataframe(scope_df, use_container_width=True, hide_index=True)

    # Target progress
    if st.session_state["target_baseline"] > 0:
        st.divider()
        st.markdown("#### Reduction Target Progress")
        target_val = st.session_state["target_baseline"] * (1 - st.session_state["target_reduction_pct"] / 100)
        progress = max(0, min(1, (st.session_state["target_baseline"] - grand_mb) /
                              max(1, st.session_state["target_baseline"] - target_val)))
        st.progress(progress, text=f"{progress*100:.0f}% of way to {st.session_state['target_reduction_pct']}% reduction target by {st.session_state['target_year']}")
        st.caption(f"Current: {grand_mb:,.0f} tCO₂e | Target: {target_val:,.0f} tCO₂e | Baseline: {st.session_state['target_baseline']:,.0f} tCO₂e")


# ─── PAGE: REPORT ─────────────────────────────────────────────────────────────
elif page == "📄 Report":
    st.markdown('<div class="section-tag">Export</div>', unsafe_allow_html=True)
    st.title("Generate Report")
    st.caption("Download a structured GHG inventory summary.")

    _, s1_total = calc_scope1()
    s2 = calc_scope2()
    s3 = calc_scope3()
    grand_mb = s1_total + s2["market_based"] + s3["total"]
    s = st.session_state

    report_text = f"""
GHG CARBON FOOTPRINT REPORT
{'='*60}
Company:          {s['company_name']}
Industry:         {s['industry']}
Country:          {s['country']}
Reporting Year:   {s['reporting_year']}
Generated:        {datetime.now().strftime('%Y-%m-%d %H:%M')}
Framework:        GHG Protocol Corporate Standard

{'='*60}
SECTION 1 — SCOPE TOTALS
{'='*60}
Scope 1  (Direct):                {s1_total:>15,.2f} tCO₂e
Scope 2  (Market-Based):          {s2['market_based']:>15,.2f} tCO₂e
Scope 2  (Location-Based, suppl): {s2['location_based']:>15,.2f} tCO₂e
Scope 3  (Value Chain):           {s3['total']:>15,.2f} tCO₂e
{'─'*50}
TOTAL    (S1 + S2MB + S3):        {grand_mb:>15,.2f} tCO₂e

{'='*60}
SECTION 2 — SCOPE 3 BREAKDOWN
{'='*60}
Cat 1 — Purchased Goods & Services:  {s3['cat1']:>12,.2f} tCO₂e
Cat 3 — Fuel & Energy (T&D losses):  {s3['cat3']:>12,.2f} tCO₂e
Cat 6 — Business Travel:             {s3['cat6']:>12,.2f} tCO₂e
Cat 7 — Employee Commuting:          {s3['cat7']:>12,.2f} tCO₂e
Cat 11 — Use of Sold Products:       {s3['cat11']:>12,.2f} tCO₂e

{'='*60}
SECTION 3 — CARBON INTENSITY
{'='*60}"""

    rev = s["revenue_musd"]
    emp = s["employees"]
    if rev > 0:
        report_text += f"\nRevenue Intensity:  {grand_mb/rev:.2f} tCO₂e / $M revenue"
    if emp > 0:
        report_text += f"\nEmployee Intensity: {grand_mb/emp:.2f} tCO₂e / FTE"

    report_text += f"""

{'='*60}
SECTION 4 — ASSUMPTIONS
{'='*60}
Revenue:              ${rev:,.0f}M USD
Employees:            {emp:,} FTE
Grid EF (location):   {s['s2_grid_ef']} kgCO₂e/MWh
Market EF:            {s['s2_market_ef']} kgCO₂e/MWh
GWP — CH₄ (fossil):   {s['gwp_ch4_fossil']}  (IPCC AR6)
GWP — N₂O:            {s['gwp_n2o']}  (IPCC AR6)
GWP — HFC-134a:       {s['gwp_hfc134a']}  (IPCC AR6)
GWP — SF₆:            {s['gwp_sf6']}  (IPCC AR6)

{'='*60}
SECTION 5 — REDUCTION TARGET
{'='*60}
Baseline:             {s['target_baseline']:,.0f} tCO₂e
Target Year:          {s['target_year']}
Reduction Required:   {s['target_reduction_pct']}%
Target Value:         {s['target_baseline'] * (1-s['target_reduction_pct']/100):,.0f} tCO₂e

{'='*60}
METHODOLOGY NOTES
{'='*60}
- Emission factors: EPA Center for Corporate Climate Leadership 2023,
  DEFRA 2023, IEA 2023, US EPA USEEIO v2.0
- GWP values: IPCC Sixth Assessment Report (AR6), 2021
- Scope 2 primary method: Market-Based
- Scope 3 method: Spend-based (Cat 1), Activity-based (Cat 3, 6, 7, 11)
"""

    st.text_area("Report Preview", report_text, height=400)

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="⬇️ Download Report (.txt)",
            data=report_text,
            file_name=f"GHG_Report_{s['company_name'].replace(' ','_')}_{s['reporting_year']}.txt",
            mime="text/plain",
        )
    with col2:
        # CSV export
        csv_rows = [
            ["Metric", "Value", "Unit"],
            ["Company", s["company_name"], ""],
            ["Reporting Year", s["reporting_year"], ""],
            ["Scope 1", f"{s1_total:.2f}", "tCO₂e"],
            ["Scope 2 Market-Based", f"{s2['market_based']:.2f}", "tCO₂e"],
            ["Scope 2 Location-Based", f"{s2['location_based']:.2f}", "tCO₂e"],
            ["Scope 3 Total", f"{s3['total']:.2f}", "tCO₂e"],
            ["Total (S1+S2MB+S3)", f"{grand_mb:.2f}", "tCO₂e"],
        ]
        if rev > 0:
            csv_rows.append(["Revenue Intensity", f"{grand_mb/rev:.4f}", "tCO₂e/$M"])
        if emp > 0:
            csv_rows.append(["Employee Intensity", f"{grand_mb/emp:.4f}", "tCO₂e/FTE"])

        csv_str = "\n".join(",".join(str(c) for c in row) for row in csv_rows)
        st.download_button(
            label="⬇️ Download Summary (.csv)",
            data=csv_str,
            file_name=f"GHG_Summary_{s['company_name'].replace(' ','_')}_{s['reporting_year']}.csv",
            mime="text/csv",
        )

    st.divider()

    # JSON export for saving state
    st.markdown("#### 💾 Save / Restore Your Data")
    st.caption("Export all your inputs as JSON to reload them later.")

    save_keys = [k for k in st.session_state if not k.startswith("inp_")]
    save_data = {k: st.session_state[k] for k in save_keys}
    st.download_button(
        label="💾 Save All Inputs (.json)",
        data=json.dumps(save_data, indent=2),
        file_name=f"GHG_Inputs_{s['company_name'].replace(' ','_')}.json",
        mime="application/json",
    )

    uploaded = st.file_uploader("📂 Restore inputs from JSON", type="json")
    if uploaded:
        loaded = json.load(uploaded)
        for k, v in loaded.items():
            st.session_state[k] = v
        st.success("✅ Inputs restored! Navigate to any page to see your data.")
