# 🌍 GHG Carbon Footprint Calculator

A web-based GHG inventory tool built on the **GHG Protocol Corporate Standard**.
Mirrors the structure of your Excel dashboard — with live calculations, caseable factors, and instant report export.

## Structure

| Page | Purpose |
|------|---------|
| 🏠 Assumptions | Company info, GWP factors, reduction targets |
| 🔥 Scope 1 | Stationary combustion, fleet, fugitive emissions |
| ⚡ Scope 2 | Purchased electricity (location- & market-based) |
| 🔗 Scope 3 | Value chain (Cat 1, 3, 6, 7, 11) |
| 📊 Dashboard | Executive KPIs, intensity ratios, target progress |
| 📄 Report | Download .txt / .csv report + save/restore JSON |

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy to Streamlit Cloud

1. Push this folder to a GitHub repo
2. Go to share.streamlit.io → New app → select your repo
3. Set `app.py` as the main file
4. Done ✅

## Key features

- **Pre-loaded emission factors** — EPA CCCL 2023, DEFRA 2023, IEA 2023
- **Caseable / editable factors** — GWP values and all EFs can be overridden
- **Dual Scope 2 reporting** — location-based and market-based
- **Live sidebar totals** — see all scope totals update as you type
- **Save & restore** — export all inputs as JSON, reload anytime
- **Instant reports** — .txt narrative + .csv summary download
