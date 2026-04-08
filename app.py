import streamlit as st
import pandas as pd
import json
from datetime import datetime

# ─── PAGE CONFIG ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="GHG Carbon Inventory",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── McKINSEY STYLE CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Source+Sans+3:wght@300;400;500;600&family=Source+Code+Pro:wght@400;500&display=swap');

:root {
    --white:     #FFFFFF;
    --off-white: #F7F7F5;
    --rule:      #E0DDD8;
    --light-grey:#F0EEE9;
    --mid-grey:  #9A9591;
    --body:      #1A1A1A;
    --navy:      #002B5B;
    --accent:    #005EB8;
    --accent-lt: #E8F0FA;
    --teal:      #00857C;
    --amber:     #C9600A;
    --rule-h:    2px solid #002B5B;
}

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: var(--white) !important;
    color: var(--body);
    font-family: 'Source Sans 3', sans-serif;
    font-size: 15px;
}

[data-testid="stSidebar"] {
    background: var(--navy) !important;
    border-right: none;
}
[data-testid="stSidebar"] * { color: #C8D8EE !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }
[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-family: 'Source Code Pro', monospace !important;
    font-size: 1.05rem !important;
}
[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    color: #7DA3CC !important;
    font-size: 11px !important;
}

h1 {
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: 2rem;
    color: var(--navy);
    border-bottom: var(--rule-h);
    padding-bottom: 12px;
    margin-bottom: 4px;
    letter-spacing: -0.02em;
}
h2 {
    font-family: 'Playfair Display', serif;
    font-weight: 600;
    font-size: 1.2rem;
    color: var(--navy);
    margin-top: 28px;
    margin-bottom: 4px;
    border-bottom: 1px solid var(--rule);
    padding-bottom: 6px;
}

.eyebrow {
    font-family: 'Source Sans 3', sans-serif;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--accent);
    margin-bottom: 4px;
    display: block;
}
.page-caption {
    font-size: 13px;
    color: var(--mid-grey);
    margin-top: 2px;
    margin-bottom: 20px;
}

.mck-kpi {
    border-top: 3px solid var(--navy);
    padding: 16px 0 12px 0;
}
.mck-kpi-label {
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: var(--mid-grey);
    margin-bottom: 6px;
}
.mck-kpi-value {
    font-family: 'Playfair Display', serif;
    font-size: 2.3rem;
    font-weight: 700;
    color: var(--navy);
    line-height: 1;
    margin-bottom: 4px;
}
.mck-kpi-unit { font-size: 12px; color: var(--mid-grey); }
.mck-kpi-delta { font-size: 12px; font-weight: 600; margin-top: 4px; }
.delta-neg { color: var(--teal); }
.delta-pos { color: var(--amber); }

.insight-box {
    background: var(--accent-lt);
    border-left: 4px solid var(--accent);
    padding: 12px 16px;
    margin: 12px 0;
    font-size: 13px;
    line-height: 1.5;
}
.insight-box strong { color: var(--navy); }

.mck-table { width:100%; border-collapse:collapse; font-size:13px; margin-top:8px; }
.mck-table thead tr { border-top:2px solid var(--navy); border-bottom:1px solid var(--navy); }
.mck-table thead th {
    padding:8px 12px; text-align:left;
    font-size:11px; font-weight:600; text-transform:uppercase;
    letter-spacing:0.08em; color:var(--navy);
}
.mck-table thead th.num { text-align:right; }
.mck-table tbody tr { border-bottom:1px solid var(--rule); }
.mck-table tbody tr:last-child { border-bottom:2px solid var(--navy); }
.mck-table tbody td { padding:8px 12px; }
.mck-table tbody td.num {
    text-align:right;
    font-family:'Source Code Pro', monospace;
    font-size:12px;
}
.mck-table tr.total-row { background:var(--light-grey); }
.mck-table tr.total-row td { color:var(--navy); font-weight:600; }

.ef-chip {
    display:inline-block;
    font-family:'Source Code Pro', monospace;
    font-size:11px;
    color:var(--accent);
    background:var(--accent-lt);
    padding:2px 7px;
    border-radius:2px;
    border:1px solid #C0D4EF;
}

.mck-progress-label {
    display:flex; justify-content:space-between;
    font-size:12px; color:var(--mid-grey); margin-bottom:4px;
}
.mck-progress-track { background:var(--light-grey); height:6px; width:100%; }
.mck-progress-fill  { background:var(--accent); height:6px; }

[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    background: var(--off-white) !important;
    border: 1px solid var(--rule) !important;
    border-radius: 2px !important;
    color: var(--body) !important;
    font-family: 'Source Code Pro', monospace !important;
    font-size: 13px !important;
}
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus { border-color: var(--accent) !important; box-shadow:none !important; }
[data-testid="stSelectbox"] > div > div {
    background: var(--off-white) !important;
    border: 1px solid var(--rule) !important;
    border-radius: 2px !important;
}
label { font-size:13px !important; color:#444 !important; font-weight:500 !important; }

.stButton > button {
    background: var(--navy) !important;
    color: var(--white) !important;
    border: none !important;
    border-radius: 2px !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size:13px !important; font-weight:600 !important;
    text-transform:uppercase !important; letter-spacing:0.06em !important;
    padding:8px 20px !important;
}
.stButton > button:hover { background: var(--accent) !important; }

[data-testid="stExpander"] {
    border: 1px solid var(--rule) !important;
    border-radius: 2px !important;
    background: var(--off-white) !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    font-size: 13px !important;
    color: var(--navy) !important;
}

[data-testid="stDownloadButton"] button {
    background: transparent !important;
    border: 1.5px solid var(--navy) !important;
    color: var(--navy) !important;
    border-radius: 2px !important;
    font-size:12px !important; font-weight:600 !important;
    text-transform:uppercase !important; letter-spacing:0.06em !important;
}
[data-testid="stDownloadButton"] button:hover {
    background: var(--navy) !important;
    color: var(--white) !important;
}

hr { border:none; border-top:1px solid var(--rule) !important; margin:20px 0 !important; }
footer { display:none; }
#MainMenu { display:none; }
</style>
""", unsafe_allow_html=True)


# ─── STATE INIT ───────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "company_name": "Your Company",
        "industry": "Technology",
        "country": "United States",
        "reporting_year": 2025,
        "revenue_musd": 0.0,
        "employees": 0,
        "gwp_ch4_fossil": 29.8,
        "gwp_n2o": 273.0,
        "gwp_hfc134a": 1526.0,
        "gwp_sf6": 25200.0,
        "s1_natgas_mmbtu": 0.0,
        "s1_diesel_litres": 0.0,
        "s1_lpg_litres": 0.0,
        "s1_coal_shorttons": 0.0,
        "s1_gasoline_litres": 0.0,
        "s1_diesel_fleet_litres": 0.0,
        "s1_jet_litres": 0.0,
        "s1_hfc134a_kg": 0.0,
        "s1_hfc410a_kg": 0.0,
        "s1_sf6_kg": 0.0,
        "s2_elec_mwh": 0.0,
        "s2_grid_ef": 386.0,
        "s2_market_ef": 0.0,
        "s2_recs_mwh": 0.0,
        "s2_steam_gj": 0.0,
        "s3_cat1_spend": 0.0,
        "s3_cat1_ef": 0.35,
        "s3_cat3_elec_mwh": 0.0,
        "s3_cat6_air_km": 0.0,
        "s3_cat6_rail_km": 0.0,
        "s3_cat7_km_per_emp": 0.0,
        "s3_cat11_units": 0.0,
        "s3_cat11_ef": 0.0,
        "prior_s1": 0.0,
        "prior_s2mb": 0.0,
        "prior_s3": 0.0,
        "target_year": 2030,
        "target_reduction_pct": 50.0,
        "target_baseline": 0.0,
        "benchmark_revenue_intensity": 0.0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

EF = {
    "natgas_co2": 53.06, "natgas_ch4": 1.0,   "natgas_n2o": 0.1,
    "diesel_co2": 2.663, "diesel_ch4": 0.139,  "diesel_n2o": 0.014,
    "lpg_co2":    1.555, "lpg_ch4":    0.0617, "lpg_n2o":    0.0062,
    "coal_co2": 2325.0,  "coal_ch4": 274.0,    "coal_n2o": 40.0,
    "gasoline_co2": 2.312, "gasoline_ch4": 0.339, "gasoline_n2o": 0.033,
    "jet_co2": 2.553,
    "hfc410a_gwp": 2088,
    "s3_cat3_td_loss": 0.05,
    "s3_cat6_air": 0.255, "s3_cat6_rail": 0.041,
    "s3_cat7_car": 0.170,
    "s2_steam_ef": 66.4,
}

COUNTRY_EF = {
    "United States": 386, "United Kingdom": 207, "Germany": 380,
    "France": 85, "China": 581, "India": 713, "Japan": 471,
    "Australia": 680, "Brazil": 119, "Canada": 130, "Other": 386,
}

def calc_scope1():
    s = st.session_state
    gwp_ch4, gwp_n2o = s["gwp_ch4_fossil"], s["gwp_n2o"]
    def tco2e(co2, ch4, n2o, qty):
        return (co2*qty/1000, ch4*qty/1e6*gwp_ch4, n2o*qty/1e6*gwp_n2o)
    r = {}
    r["natgas"]       = tco2e(EF["natgas_co2"],  EF["natgas_ch4"],  EF["natgas_n2o"],  s["s1_natgas_mmbtu"])
    r["diesel"]       = tco2e(EF["diesel_co2"],  EF["diesel_ch4"],  EF["diesel_n2o"],  s["s1_diesel_litres"])
    r["lpg"]          = tco2e(EF["lpg_co2"],     EF["lpg_ch4"],     EF["lpg_n2o"],     s["s1_lpg_litres"])
    r["coal"]         = tco2e(EF["coal_co2"],    EF["coal_ch4"],    EF["coal_n2o"],    s["s1_coal_shorttons"])
    r["gasoline"]     = tco2e(EF["gasoline_co2"],EF["gasoline_ch4"],EF["gasoline_n2o"],s["s1_gasoline_litres"])
    r["diesel_fleet"] = tco2e(EF["diesel_co2"],  EF["diesel_ch4"],  EF["diesel_n2o"],  s["s1_diesel_fleet_litres"])
    r["jet"]          = (EF["jet_co2"]*s["s1_jet_litres"]/1000, 0, 0)
    fug = (s["s1_hfc134a_kg"]*s["gwp_hfc134a"]/1000
         + s["s1_hfc410a_kg"]*EF["hfc410a_gwp"]/1000
         + s["s1_sf6_kg"]*s["gwp_sf6"]/1000)
    r["fugitive"] = (fug, 0, 0)
    return r, sum(sum(v) for v in r.values())

def calc_scope2():
    s = st.session_state
    net = max(0, s["s2_elec_mwh"] - s["s2_recs_mwh"])
    steam = s["s2_steam_gj"] * EF["s2_steam_ef"] / 1000
    lb = s["s2_elec_mwh"] * s["s2_grid_ef"] / 1000 + steam
    mb = net * s["s2_market_ef"] / 1000 + steam
    recs_pct = s["s2_recs_mwh"] / max(1, s["s2_elec_mwh"]) * 100
    return {"lb": lb, "mb": mb, "net": net, "recs_pct": recs_pct}

def calc_scope3():
    s = st.session_state
    cat1  = s["s3_cat1_spend"] * s["s3_cat1_ef"] / 1000
    cat3  = s["s3_cat3_elec_mwh"] * s["s2_grid_ef"] * EF["s3_cat3_td_loss"] / 1000
    cat6  = (s["s3_cat6_air_km"]*EF["s3_cat6_air"] + s["s3_cat6_rail_km"]*EF["s3_cat6_rail"]) / 1000
    cat7  = s["s3_cat7_km_per_emp"] * s["employees"] * EF["s3_cat7_car"] / 1000
    cat11 = s["s3_cat11_units"] * s["s3_cat11_ef"] / 1000
    return {"cat1":cat1,"cat3":cat3,"cat6":cat6,"cat7":cat7,"cat11":cat11,"total":cat1+cat3+cat6+cat7+cat11}

def fi(v): return f"{v:,.0f}"
def ff(v): return f"{v:,.1f}"
def dpct(c, p): return (c-p)/p*100 if p > 0 else None

def kpi_html(label, value, unit, delta=None):
    d = ""
    if delta is not None:
        cls = "delta-neg" if delta < 0 else "delta-pos"
        arr = "↓" if delta < 0 else "↑"
        d = f'<div class="mck-kpi-delta {cls}">{arr} {abs(delta):.1f}% vs prior year</div>'
    return f"""<div class="mck-kpi">
      <div class="mck-kpi-label">{label}</div>
      <div class="mck-kpi-value">{value}</div>
      <div class="mck-kpi-unit">{unit}</div>{d}
    </div>"""

def section_head(eyebrow, title, caption=""):
    st.markdown(f'<span class="eyebrow">{eyebrow}</span>', unsafe_allow_html=True)
    st.markdown(f"# {title}")
    if caption:
        st.markdown(f'<p class="page-caption">{caption}</p>', unsafe_allow_html=True)


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:24px 0 8px 0;">
      <div style="font-family:'Playfair Display',serif;font-size:1.1rem;
                  font-weight:700;color:#FFFFFF;letter-spacing:-0.01em;">GHG Inventory</div>
      <div style="font-size:11px;color:#7DA3CC;text-transform:uppercase;
                  letter-spacing:0.12em;margin-top:2px;">GHG Protocol Framework</div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    page = st.radio("Nav", [
        "Assumptions",
        "Scope 1 — Direct",
        "Scope 2 — Purchased Energy",
        "Scope 3 — Value Chain",
        "Dashboard",
        "Export Report",
    ], label_visibility="collapsed")
    st.divider()

    _, s1t = calc_scope1()
    s2 = calc_scope2()
    s3 = calc_scope3()
    grand = s1t + s2["mb"] + s3["total"]

    st.markdown("<div style='font-size:10px;text-transform:uppercase;letter-spacing:0.12em;color:#7DA3CC;margin-bottom:8px;'>Live Totals</div>", unsafe_allow_html=True)
    st.metric("Scope 1", f"{fi(s1t)} tCO₂e")
    st.metric("Scope 2 (MB)", f"{fi(s2['mb'])} tCO₂e")
    st.metric("Scope 3", f"{fi(s3['total'])} tCO₂e")
    st.metric("Total", f"{fi(grand)} tCO₂e")
    st.markdown(f"""<div style="margin-top:20px;padding-top:16px;border-top:1px solid rgba(255,255,255,0.12);
                font-size:11px;color:#7DA3CC;">{st.session_state['company_name']}<br>FY {st.session_state['reporting_year']}</div>""",
                unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
if page == "Assumptions":
    section_head("Step 01", "Central Assumptions",
                 "All calculation sheets reference these inputs. Complete this section before proceeding.")

    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown("## Company Profile")
        st.session_state["company_name"] = st.text_input("Legal Entity / Company Name", st.session_state["company_name"])
        st.session_state["industry"] = st.selectbox("Industry Sector", [
            "Technology","Manufacturing","Retail & Consumer","Financial Services",
            "Healthcare & Pharma","Energy & Utilities","Real Estate",
            "Transportation & Logistics","Food & Beverage","Other"])
        st.session_state["country"] = st.selectbox("Primary Country of Operations", list(COUNTRY_EF.keys()))
        st.session_state["reporting_year"] = st.number_input("Reporting Year", 2000, 2030, st.session_state["reporting_year"])

    with col2:
        st.markdown("## Financial Metrics")
        st.caption("Used to calculate carbon intensity ratios.")
        st.session_state["revenue_musd"] = st.number_input("Annual Revenue (USD Millions)", 0.0, value=st.session_state["revenue_musd"], step=100.0)
        st.session_state["employees"] = st.number_input("Full-Time Equivalent Employees (FTE)", 0, value=st.session_state["employees"], step=100)
        st.markdown("## Prior Year Actuals")
        st.caption("Used for year-on-year comparison.")
        pa, pb, pc = st.columns(3)
        with pa: st.session_state["prior_s1"]   = st.number_input("Scope 1", 0.0, value=st.session_state["prior_s1"])
        with pb: st.session_state["prior_s2mb"] = st.number_input("Scope 2 MB", 0.0, value=st.session_state["prior_s2mb"])
        with pc: st.session_state["prior_s3"]   = st.number_input("Scope 3", 0.0, value=st.session_state["prior_s3"])

    st.divider()
    st.markdown("## GWP Factors — IPCC AR6 (2021)")
    st.caption("Adjust only if your regulatory regime requires AR5 or AR4.")
    gc1, gc2, gc3, gc4 = st.columns(4)
    with gc1:
        st.session_state["gwp_ch4_fossil"] = st.number_input("CH₄ fossil GWP", value=st.session_state["gwp_ch4_fossil"])
        st.markdown('<span class="ef-chip">AR5: 25 | AR6: 29.8</span>', unsafe_allow_html=True)
    with gc2:
        st.session_state["gwp_n2o"] = st.number_input("N₂O GWP", value=st.session_state["gwp_n2o"])
        st.markdown('<span class="ef-chip">AR5: 298 | AR6: 273</span>', unsafe_allow_html=True)
    with gc3:
        st.session_state["gwp_hfc134a"] = st.number_input("HFC-134a GWP", value=st.session_state["gwp_hfc134a"])
        st.markdown('<span class="ef-chip">AR5: 1430 | AR6: 1526</span>', unsafe_allow_html=True)
    with gc4:
        st.session_state["gwp_sf6"] = st.number_input("SF₆ GWP", value=st.session_state["gwp_sf6"])
        st.markdown('<span class="ef-chip">AR5: 22800 | AR6: 25200</span>', unsafe_allow_html=True)

    st.divider()
    st.markdown("## Reduction Target")
    ta, tb, tc = st.columns(3)
    with ta: st.session_state["target_year"] = st.number_input("Target Year", 2025, 2060, st.session_state["target_year"])
    with tb: st.session_state["target_reduction_pct"] = st.slider("Reduction vs Baseline (%)", 0, 100, int(st.session_state["target_reduction_pct"]))
    with tc: st.session_state["target_baseline"] = st.number_input("Baseline Emissions (tCO₂e)", 0.0, value=st.session_state["target_baseline"])

    if st.session_state["target_baseline"] > 0:
        target_val = st.session_state["target_baseline"] * (1 - st.session_state["target_reduction_pct"]/100)
        yrs = max(1, st.session_state["target_year"] - st.session_state["reporting_year"])
        annual = (st.session_state["target_baseline"] - target_val) / yrs
        st.markdown(f"""<div class="insight-box"><strong>Target trajectory:</strong>
            Reduce to <strong>{fi(target_val)} tCO₂e</strong> by {st.session_state['target_year']},
            requiring <strong>{fi(annual)} tCO₂e/year</strong> reduction over {yrs} years.</div>""",
            unsafe_allow_html=True)

    st.session_state["benchmark_revenue_intensity"] = st.number_input(
        "Industry Benchmark — Revenue Intensity (tCO₂e / $M revenue)", 0.0,
        value=st.session_state["benchmark_revenue_intensity"])


# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Scope 1 — Direct":
    results, s1t = calc_scope1()
    stationary = sum(sum(results[k]) for k in ["natgas","diesel","lpg","coal"])
    mobile     = sum(sum(results[k]) for k in ["gasoline","diesel_fleet","jet"])
    fugitive   = sum(results["fugitive"])

    section_head("Step 02", "Scope 1 — Direct GHG Emissions",
                 "Sources directly owned or controlled: stationary combustion, mobile combustion, and fugitive releases.")

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(kpi_html("Total Scope 1", fi(s1t), "tCO₂e"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_html("Stationary Combustion", fi(stationary), "tCO₂e"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_html("Mobile Combustion", fi(mobile), "tCO₂e"), unsafe_allow_html=True)
    with c4: st.markdown(kpi_html("Fugitive Emissions", fi(fugitive), "tCO₂e"), unsafe_allow_html=True)

    st.divider()
    st.markdown("## Part A — Stationary Combustion")
    st.caption("Boilers, furnaces, generators, turbines. Source: EPA CCCL 2023.")

    for label, key, unit, ef_val, rkey in [
        ("Natural Gas",            "s1_natgas_mmbtu",   "MMBtu",      EF["natgas_co2"],    "natgas"),
        ("Diesel / Fuel Oil No.2", "s1_diesel_litres",  "Litres",     EF["diesel_co2"],    "diesel"),
        ("Liquefied Petroleum Gas","s1_lpg_litres",     "Litres",     EF["lpg_co2"],       "lpg"),
        ("Coal (Bituminous)",      "s1_coal_shorttons", "Short Tons", EF["coal_co2"]/1000, "coal"),
    ]:
        row_total = sum(results[rkey])
        with st.expander(f"{label}   —   {ff(row_total)} tCO₂e"):
            ea, eb, ec_ = st.columns([3,2,2])
            with ea:
                st.session_state[key] = st.number_input(
                    f"Activity Quantity ({unit})", 0.0, value=st.session_state[key],
                    key=f"si_{key}", step=1.0 if "ton" in unit.lower() else 100.0)
            with eb:
                st.markdown(f"<br><span class='ef-chip'>CO₂ EF: {ef_val:.4f} kgCO₂/{unit}</span>", unsafe_allow_html=True)
            with ec_:
                st.metric("Result", f"{ff(row_total)} tCO₂e")

    st.divider()
    st.markdown("## Part B — Mobile Combustion")
    st.caption("Company-owned or leased vehicles and aircraft. Source: DEFRA 2023 / EPA 2023.")
    mb1, mb2, mb3 = st.columns(3)
    with mb1:
        st.session_state["s1_gasoline_litres"] = st.number_input("Gasoline / Petrol (Litres)", 0.0, value=st.session_state["s1_gasoline_litres"], step=100.0)
        st.markdown(f"<span class='ef-chip'>{EF['gasoline_co2']} kgCO₂/L</span>", unsafe_allow_html=True)
    with mb2:
        st.session_state["s1_diesel_fleet_litres"] = st.number_input("Diesel Fleet (Litres)", 0.0, value=st.session_state["s1_diesel_fleet_litres"], step=100.0)
        st.markdown(f"<span class='ef-chip'>{EF['diesel_co2']} kgCO₂/L</span>", unsafe_allow_html=True)
    with mb3:
        st.session_state["s1_jet_litres"] = st.number_input("Aviation Fuel / Jet-A (Litres)", 0.0, value=st.session_state["s1_jet_litres"], step=100.0)
        st.markdown(f"<span class='ef-chip'>{EF['jet_co2']} kgCO₂/L</span>", unsafe_allow_html=True)

    st.divider()
    st.markdown("## Part C — Fugitive Emissions")
    st.caption("Refrigerant leaks and electrical equipment. GWP factors from IPCC AR6.")
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        st.session_state["s1_hfc134a_kg"] = st.number_input("HFC-134a leaked (kg)", 0.0, value=st.session_state["s1_hfc134a_kg"])
        st.markdown(f"<span class='ef-chip'>GWP: {st.session_state['gwp_hfc134a']}</span>", unsafe_allow_html=True)
    with fc2:
        st.session_state["s1_hfc410a_kg"] = st.number_input("HFC-410A leaked (kg)", 0.0, value=st.session_state["s1_hfc410a_kg"])
        st.markdown(f"<span class='ef-chip'>GWP: {EF['hfc410a_gwp']}</span>", unsafe_allow_html=True)
    with fc3:
        st.session_state["s1_sf6_kg"] = st.number_input("SF₆ leaked (kg)", 0.0, value=st.session_state["s1_sf6_kg"])
        st.markdown(f"<span class='ef-chip'>GWP: {st.session_state['gwp_sf6']}</span>", unsafe_allow_html=True)

    st.divider()
    st.markdown("## Scope 1 Summary")
    rows = [
        ("Natural Gas",       "Stationary", ff(sum(results["natgas"]))),
        ("Diesel / Fuel Oil", "Stationary", ff(sum(results["diesel"]))),
        ("LPG",               "Stationary", ff(sum(results["lpg"]))),
        ("Coal",              "Stationary", ff(sum(results["coal"]))),
        ("Gasoline Fleet",    "Mobile",     ff(sum(results["gasoline"]))),
        ("Diesel Fleet",      "Mobile",     ff(sum(results["diesel_fleet"]))),
        ("Aviation",          "Mobile",     ff(sum(results["jet"]))),
        ("Fugitive",          "Fugitive",   ff(sum(results["fugitive"]))),
    ]
    tbl = '<table class="mck-table"><thead><tr><th>Source</th><th>Category</th><th class="num">tCO₂e</th></tr></thead><tbody>'
    for n,c,v in rows: tbl += f"<tr><td>{n}</td><td>{c}</td><td class='num'>{v}</td></tr>"
    tbl += f'<tr class="total-row"><td><strong>Total Scope 1</strong></td><td></td><td class="num"><strong>{ff(s1t)}</strong></td></tr></tbody></table>'
    st.markdown(tbl, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Scope 2 — Purchased Energy":
    s2 = calc_scope2()
    section_head("Step 03", "Scope 2 — Purchased Energy",
                 "GHG Protocol requires dual reporting: Market-Based (primary) and Location-Based (supplemental).")

    c1,c2,c3 = st.columns(3)
    with c1: st.markdown(kpi_html("Market-Based (Primary)", fi(s2["mb"]), "tCO₂e"), unsafe_allow_html=True)
    with c2: st.markdown(kpi_html("Location-Based (Suppl.)", fi(s2["lb"]), "tCO₂e"), unsafe_allow_html=True)
    with c3: st.markdown(kpi_html("Renewable Coverage", f"{s2['recs_pct']:.1f}%", "of total electricity"), unsafe_allow_html=True)

    st.divider()
    st.markdown("## Part A — Purchased Electricity")
    ea, eb, ec = st.columns(3)
    with ea:
        st.session_state["s2_elec_mwh"] = st.number_input("Total Electricity Consumed (MWh)", 0.0, value=st.session_state["s2_elec_mwh"], step=100.0)
    with eb:
        suggested = COUNTRY_EF.get(st.session_state["country"], 386)
        st.session_state["s2_grid_ef"] = st.number_input("Location-Based Grid EF (kgCO₂e/MWh)", 0.0, value=float(suggested), step=1.0)
        st.markdown(f"<span class='ef-chip'>Suggested for {st.session_state['country']}: {suggested}</span>", unsafe_allow_html=True)
    with ec:
        st.session_state["s2_market_ef"] = st.number_input("Market-Based Supplier EF (kgCO₂e/MWh)", 0.0, value=st.session_state["s2_market_ef"], step=1.0)

    st.session_state["s2_recs_mwh"] = st.slider(
        "RECs / PPAs Covered (MWh)", 0.0, max(st.session_state["s2_elec_mwh"], 1.0),
        min(st.session_state["s2_recs_mwh"], max(st.session_state["s2_elec_mwh"], 0.0)), step=100.0)

    st.markdown(f"""<div class="insight-box"><strong>Net metered electricity:</strong>
        {fi(s2['net'])} MWh after {fi(st.session_state['s2_recs_mwh'])} MWh RECs/PPAs.
        Market-based emissions = net MWh × {st.session_state['s2_market_ef']} kgCO₂e/MWh.</div>""",
        unsafe_allow_html=True)

    st.divider()
    st.markdown("## Part B — Purchased Steam, Heat & Cooling")
    st.session_state["s2_steam_gj"] = st.number_input("Purchased Steam / Heat / Cooling (GJ)", 0.0, value=st.session_state["s2_steam_gj"])
    st.markdown(f"<span class='ef-chip'>EF: {EF['s2_steam_ef']} kgCO₂e/GJ</span>", unsafe_allow_html=True)

    st.divider()
    tbl = '<table class="mck-table"><thead><tr><th>Method</th><th>Basis</th><th class="num">tCO₂e</th></tr></thead><tbody>'
    tbl += f"<tr><td>Location-Based</td><td>Grid average × total MWh</td><td class='num'>{ff(s2['lb'])}</td></tr>"
    tbl += f"<tr><td>Market-Based</td><td>Supplier EF × net MWh after RECs</td><td class='num'>{ff(s2['mb'])}</td></tr>"
    tbl += f'<tr class="total-row"><td><strong>Primary (Market-Based)</strong></td><td>Used in total inventory</td><td class="num"><strong>{ff(s2["mb"])}</strong></td></tr></tbody></table>'
    st.markdown(tbl, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Scope 3 — Value Chain":
    s3 = calc_scope3()
    section_head("Step 04", "Scope 3 — Value Chain Emissions",
                 "Indirect emissions from upstream and downstream activities. Typically 70–90% of total inventory.")

    c1, _ = st.columns([1, 3])
    with c1: st.markdown(kpi_html("Scope 3 Total", fi(s3["total"]), "tCO₂e"), unsafe_allow_html=True)

    st.divider()

    configs = [
        ("Cat. 1", "Purchased Goods & Services",        "s3_cat1_spend", "s3_cat1_ef",
         "Annual Spend ($000s USD)", "EEIO Factor (kgCO₂e per $)",
         "Spend-based | US EPA USEEIO v2.0 | Typical: 0.12–0.95", "cat1", True),
        ("Cat. 3", "Fuel & Energy-Related (T&D Losses)", "s3_cat3_elec_mwh", None,
         "Electricity consumed (MWh)", None,
         f"5% T&D loss × grid EF ({st.session_state['s2_grid_ef']} kgCO₂e/MWh)", "cat3", False),
        ("Cat. 6", "Business Travel",                    "s3_cat6_air_km", None,
         "Total Air Travel (km)", None,
         f"Economy class | EF: {EF['s3_cat6_air']} kgCO₂e/km | DEFRA 2023", "cat6", False),
        ("Cat. 7", "Employee Commuting",                 "s3_cat7_km_per_emp", None,
         "Avg commute per employee/year (km)", None,
         f"Applied to {st.session_state['employees']:,} FTEs | EF: {EF['s3_cat7_car']} kgCO₂e/km", "cat7", False),
        ("Cat. 11","Use of Sold Products",               "s3_cat11_units", "s3_cat11_ef",
         "Units / product-years in use", "Lifecycle EF (kgCO₂e/unit)",
         "Activity-based | Provide product-specific lifecycle EF", "cat11", True),
    ]

    for cat_num, cat_name, k1, k2, lbl1, lbl2, note, rkey, has_two in configs:
        val = s3[rkey]
        with st.expander(f"**{cat_num} — {cat_name}**   —   {ff(val)} tCO₂e"):
            if has_two:
                ca, cb, cc = st.columns([3,2,2])
                with ca: st.session_state[k1] = st.number_input(lbl1, 0.0, value=st.session_state[k1], step=1000.0, key=f"s3a_{k1}")
                with cb: st.session_state[k2] = st.number_input(lbl2, 0.0, value=st.session_state[k2], step=0.01,   key=f"s3b_{k2}")
                with cc: st.metric("Result", f"{ff(val)} tCO₂e")
            else:
                ca, cb = st.columns([3,2])
                with ca: st.session_state[k1] = st.number_input(lbl1, 0.0, value=st.session_state[k1], step=1000.0, key=f"s3a_{k1}")
                with cb: st.metric("Result", f"{ff(val)} tCO₂e")
            st.caption(f"Methodology: {note}")

    st.divider()
    st.markdown("## Category Summary")
    cat_labels = [
        ("cat1",  "Cat 1 — Purchased Goods & Services", "Spend-based"),
        ("cat3",  "Cat 3 — Fuel & Energy (T&D)",        "Activity-based"),
        ("cat6",  "Cat 6 — Business Travel",             "Activity-based"),
        ("cat7",  "Cat 7 — Employee Commuting",          "Activity-based"),
        ("cat11", "Cat 11 — Use of Sold Products",       "Activity-based"),
    ]
    tbl = '<table class="mck-table"><thead><tr><th>Category</th><th>Method</th><th class="num">tCO₂e</th><th class="num">% of S3</th></tr></thead><tbody>'
    for k, label, method in cat_labels:
        pct = s3[k]/max(s3["total"],1)*100
        tbl += f"<tr><td>{label}</td><td>{method}</td><td class='num'>{ff(s3[k])}</td><td class='num'>{pct:.1f}%</td></tr>"
    tbl += f'<tr class="total-row"><td><strong>Total Scope 3</strong></td><td></td><td class="num"><strong>{ff(s3["total"])}</strong></td><td class="num"><strong>100%</strong></td></tr></tbody></table>'
    st.markdown(tbl, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Dashboard":
    _, s1t = calc_scope1()
    s2 = calc_scope2()
    s3 = calc_scope3()
    grand = s1t + s2["mb"] + s3["total"]
    prior_grand = st.session_state["prior_s1"] + st.session_state["prior_s2mb"] + st.session_state["prior_s3"]
    s = st.session_state

    section_head("Executive View",
                 f"{s['company_name']} — GHG Inventory {s['reporting_year']}",
                 "GHG Protocol Corporate Standard  ·  Market-Based Scope 2  ·  Figures in tCO₂e")

    c1,c2,c3,c4 = st.columns(4)
    with c1: st.markdown(kpi_html("Scope 1 — Direct",         fi(s1t),          "tCO₂e", dpct(s1t, s["prior_s1"])),   unsafe_allow_html=True)
    with c2: st.markdown(kpi_html("Scope 2 — Market-Based",   fi(s2["mb"]),      "tCO₂e", dpct(s2["mb"], s["prior_s2mb"])), unsafe_allow_html=True)
    with c3: st.markdown(kpi_html("Scope 3 — Value Chain",    fi(s3["total"]),   "tCO₂e", dpct(s3["total"], s["prior_s3"])), unsafe_allow_html=True)
    with c4: st.markdown(kpi_html("Total (S1 + S2 + S3)",     fi(grand),         "tCO₂e", dpct(grand, prior_grand)),   unsafe_allow_html=True)

    st.divider()
    col_l, col_r = st.columns([3,2], gap="large")

    with col_l:
        st.markdown("## Scope Breakdown")
        scope_rows = [
            ("Scope 1",           "Direct — combustion, fleet, fugitive",   s1t,          s["prior_s1"]),
            ("Scope 2 (MB)",      "Purchased energy — market-based",        s2["mb"],     s["prior_s2mb"]),
            ("Scope 3",           "Value chain — upstream & downstream",    s3["total"],  s["prior_s3"]),
            ("Total",             "S1 + S2(MB) + S3",                       grand,        prior_grand),
        ]
        tbl = '<table class="mck-table"><thead><tr><th>Scope</th><th>Description</th><th class="num">tCO₂e</th><th class="num">% Share</th><th class="num">YoY</th></tr></thead><tbody>'
        for sc, desc, val, prior in scope_rows:
            pct = f"{val/max(grand,1)*100:.1f}%" if sc != "Total" else "100%"
            yoy = f"{dpct(val,prior):+.1f}%" if prior > 0 else "—"
            cls = ' class="total-row"' if sc == "Total" else ""
            b = "<strong>" if sc == "Total" else ""
            be = "</strong>" if sc == "Total" else ""
            tbl += f"<tr{cls}><td>{b}{sc}{be}</td><td>{desc}</td><td class='num'>{b}{fi(val)}{be}</td><td class='num'>{pct}</td><td class='num'>{yoy}</td></tr>"
        tbl += "</tbody></table>"
        st.markdown(tbl, unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:11px;color:var(--mid-grey);margin-top:6px;'>◦ Scope 2 Location-Based (supplemental): {fi(s2['lb'])} tCO₂e</div>", unsafe_allow_html=True)

    with col_r:
        st.markdown("## Carbon Intensity")
        rev, emp = s["revenue_musd"], s["employees"]
        bench = s["benchmark_revenue_intensity"]
        tbl2 = '<table class="mck-table"><thead><tr><th>Metric</th><th class="num">Value</th><th class="num">Unit</th><th class="num">YoY</th></tr></thead><tbody>'
        if rev > 0:
            ri = grand/rev
            pri_ri = prior_grand/rev if prior_grand > 0 else None
            tbl2 += f"<tr><td>Revenue intensity</td><td class='num'>{ri:.2f}</td><td class='num'>tCO₂e/$M</td><td class='num'>{f'{dpct(ri,pri_ri):+.1f}%' if pri_ri else '—'}</td></tr>"
            if bench > 0:
                vs = (ri-bench)/bench*100
                tbl2 += f"<tr><td>vs Benchmark</td><td class='num'>{vs:+.1f}%</td><td class='num'>Bench: {bench:.1f}</td><td class='num'>—</td></tr>"
        if emp > 0:
            ei = grand/emp
            pri_ei = prior_grand/emp if prior_grand > 0 else None
            tbl2 += f"<tr><td>Employee intensity</td><td class='num'>{ei:.2f}</td><td class='num'>tCO₂e/FTE</td><td class='num'>{f'{dpct(ei,pri_ei):+.1f}%' if pri_ei else '—'}</td></tr>"
        tbl2 += "</tbody></table>"
        if rev > 0 or emp > 0:
            st.markdown(tbl2, unsafe_allow_html=True)
        else:
            st.caption("Enter revenue and employees in Assumptions to view intensity ratios.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("## Renewable Energy")
        rp = s2["recs_pct"]
        st.markdown(f"""<div style="margin:12px 0;">
          <div class="mck-progress-label"><span>Renewable Coverage</span><span>{rp:.1f}%</span></div>
          <div class="mck-progress-track"><div class="mck-progress-fill" style="width:{min(rp,100):.1f}%"></div></div>
        </div>""", unsafe_allow_html=True)

    if s["target_baseline"] > 0:
        st.divider()
        st.markdown("## Reduction Target Progress")
        target_val = s["target_baseline"] * (1 - s["target_reduction_pct"]/100)
        progress = max(0, min(1, (s["target_baseline"]-grand)/max(1, s["target_baseline"]-target_val)))
        yrs = max(1, s["target_year"]-s["reporting_year"])
        annual_req = max(0, (grand-target_val)/yrs)

        ta,tb,tc,td = st.columns(4)
        with ta: st.markdown(kpi_html("Baseline",           fi(s["target_baseline"]), "tCO₂e"), unsafe_allow_html=True)
        with tb: st.markdown(kpi_html("Current",            fi(grand),                "tCO₂e"), unsafe_allow_html=True)
        with tc: st.markdown(kpi_html("Target",             fi(target_val),           f"tCO₂e by {s['target_year']}"), unsafe_allow_html=True)
        with td: st.markdown(kpi_html("Annual Reduction Req.", fi(annual_req),        "tCO₂e/year"), unsafe_allow_html=True)

        st.markdown(f"""<div style="margin-top:16px;">
          <div class="mck-progress-label">
            <span>Progress toward {s['target_reduction_pct']}% reduction by {s['target_year']}</span>
            <span>{progress*100:.0f}%</span>
          </div>
          <div class="mck-progress-track">
            <div class="mck-progress-fill" style="width:{min(progress*100,100):.1f}%"></div>
          </div>
        </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
elif page == "Export Report":
    _, s1t = calc_scope1()
    s2 = calc_scope2()
    s3 = calc_scope3()
    grand = s1t + s2["mb"] + s3["total"]
    s = st.session_state

    section_head("Step 05", "Export Report",
                 "Download formatted outputs or save and restore your complete input dataset.")

    report_text = f"""{'═'*65}
  GHG CARBON FOOTPRINT REPORT
  {s['company_name']}  |  FY {s['reporting_year']}
  Generated: {datetime.now().strftime('%B %d, %Y %H:%M')}
  Framework: GHG Protocol Corporate Standard
{'═'*65}

SECTION 1 — SCOPE TOTALS
{'─'*65}
  Scope 1   Direct Emissions                  {s1t:>13,.1f}  tCO₂e
  Scope 2   Market-Based (Primary)            {s2['mb']:>13,.1f}  tCO₂e
  Scope 2   Location-Based (Supplemental)     {s2['lb']:>13,.1f}  tCO₂e
  Scope 3   Value Chain Emissions             {s3['total']:>13,.1f}  tCO₂e
{'─'*65}
  TOTAL     S1 + S2(MB) + S3                  {grand:>13,.1f}  tCO₂e

SECTION 2 — SCOPE 3 DETAIL
{'─'*65}
  Cat  1   Purchased Goods & Services         {s3['cat1']:>13,.1f}  tCO₂e
  Cat  3   Fuel & Energy (T&D Losses)         {s3['cat3']:>13,.1f}  tCO₂e
  Cat  6   Business Travel                    {s3['cat6']:>13,.1f}  tCO₂e
  Cat  7   Employee Commuting                 {s3['cat7']:>13,.1f}  tCO₂e
  Cat 11   Use of Sold Products               {s3['cat11']:>13,.1f}  tCO₂e

SECTION 3 — CARBON INTENSITY
{'─'*65}"""
    rev, emp = s["revenue_musd"], s["employees"]
    if rev > 0: report_text += f"\n  Revenue Intensity          {grand/rev:>10.2f}  tCO₂e / $M revenue"
    if emp > 0: report_text += f"\n  Employee Intensity         {grand/emp:>10.2f}  tCO₂e / FTE"

    report_text += f"""

SECTION 4 — ASSUMPTIONS
{'─'*65}
  Revenue                    ${rev:>12,.0f}M USD
  Employees                  {emp:>12,} FTE
  Grid EF (location)         {s['s2_grid_ef']:>12} kgCO₂e/MWh
  Market EF                  {s['s2_market_ef']:>12} kgCO₂e/MWh
  GWP CH₄ (fossil)           {s['gwp_ch4_fossil']:>12}  [IPCC AR6]
  GWP N₂O                    {s['gwp_n2o']:>12}  [IPCC AR6]
  GWP HFC-134a               {s['gwp_hfc134a']:>12}  [IPCC AR6]
  GWP SF₆                    {s['gwp_sf6']:>12}  [IPCC AR6]

SECTION 5 — REDUCTION TARGET
{'─'*65}
  Baseline                   {s['target_baseline']:>12,.0f}  tCO₂e
  Target Year                {s['target_year']:>12}
  Reduction Required         {s['target_reduction_pct']:>11.0f}%
  Target Value               {s['target_baseline']*(1-s['target_reduction_pct']/100):>12,.0f}  tCO₂e

METHODOLOGY
{'─'*65}
  Emission Factors: EPA CCCL 2023, DEFRA 2023, IEA 2023,
    US EPA USEEIO v2.0
  GWP Reference: IPCC AR6, 2021
  Scope 2 Primary Method: Market-Based
  Scope 3 Methods: Spend-based (Cat 1), Activity-based (Cat 3, 6, 7, 11)
{'═'*65}
"""

    d1, d2, d3 = st.columns(3)
    with d1:
        st.download_button("⬇  Report (.txt)", data=report_text,
            file_name=f"GHG_Report_{s['company_name'].replace(' ','_')}_{s['reporting_year']}.txt",
            mime="text/plain", use_container_width=True)
    with d2:
        csv_rows = [["Metric","Value","Unit"],
                    ["Company", s["company_name"],""],
                    ["Year", s["reporting_year"],""],
                    ["Scope 1", f"{s1t:.2f}","tCO₂e"],
                    ["Scope 2 MB", f"{s2['mb']:.2f}","tCO₂e"],
                    ["Scope 2 LB", f"{s2['lb']:.2f}","tCO₂e"],
                    ["Scope 3", f"{s3['total']:.2f}","tCO₂e"],
                    ["Total", f"{grand:.2f}","tCO₂e"]]
        if rev > 0: csv_rows.append(["Revenue Intensity", f"{grand/rev:.4f}","tCO₂e/$M"])
        if emp > 0: csv_rows.append(["Employee Intensity", f"{grand/emp:.4f}","tCO₂e/FTE"])
        st.download_button("⬇  Summary (.csv)",
            data="\n".join(",".join(str(c) for c in r) for r in csv_rows),
            file_name=f"GHG_Summary_{s['company_name'].replace(' ','_')}_{s['reporting_year']}.csv",
            mime="text/csv", use_container_width=True)
    with d3:
        save_keys = [k for k in st.session_state if not k.startswith("si_") and not k.startswith("s3a_") and not k.startswith("s3b_")]
        st.download_button("💾  Save Inputs (.json)",
            data=json.dumps({k: st.session_state[k] for k in save_keys}, indent=2),
            file_name=f"GHG_Inputs_{s['company_name'].replace(' ','_')}.json",
            mime="application/json", use_container_width=True)

    st.divider()
    with st.expander("Report Preview"):
        st.text(report_text)

    st.divider()
    st.markdown("## Restore Saved Inputs")
    st.caption("Upload a previously saved .json file to reload all inputs.")
    uploaded = st.file_uploader("Upload JSON", type="json", label_visibility="collapsed")
    if uploaded:
        for k, v in json.load(uploaded).items():
            st.session_state[k] = v
        st.success("Inputs restored. Navigate to any section to review.")
