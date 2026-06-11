<div align="center">

# ✈ AeroVia

**Route Profitability Simulator for Indian Aviation**

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Anthropic](https://img.shields.io/badge/Powered%20by-Claude%20API-191919?style=flat-square)](https://anthropic.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

*Model airline economics, run what-if scenarios, forecast ATF prices, and get AI-powered route analysis — all in one tool built for Indian domestic aviation.*

</div>

---

## What is AeroVia?

AeroVia is a full-stack route profitability simulator designed specifically for Indian domestic airline economics. It lets you model any route between 24 Indian airports, compute RASK/CASK/BELF metrics with customizable cost assumptions, run sensitivity analyses, and chat with an AI analyst powered by Claude.

Built using real aviation economics frameworks, DGCA traffic data structures, and Indian-specific inputs (ATF pricing, airport charges, domestic yield benchmarks).

---

## Features

| Module | What it does |
|--------|-------------|
| **Route Builder** | Pick any origin → destination, aircraft type, frequency, load factor, and customize every cost assumption |
| **Scenario Lab** | Live what-if sliders with instant delta vs base case; sensitivity heatmap across LF × ATF price |
| **Save & Compare** | Store up to 6 named scenarios, compare side-by-side, export to CSV |
| **Portfolio Map** | Plotly geo map of your full route network, arcs colour-coded by profitability |
| **DGCA Upload** | Drag-and-drop CSV/Excel with automatic column mapping UI |
| **ML Forecasts** | ATF price forecasting, demand prediction with confidence bands, anomaly detection |
| **AI Analyst** | Claude-powered NLP chat with live route context — ask anything about route economics |

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/aerovia.git
cd aerovia
```

### 2. Create a virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS / Linux
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Open `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

> Get your API key at [console.anthropic.com](https://console.anthropic.com). The AI Analyst page will work without it — you'll just see a prompt to add the key in the sidebar.

### 5. Launch

```bash
streamlit run dashboard/app.py
```

Open **http://localhost:8501** in your browser. Click **Load demo data** on the Portfolio page to explore without a real DGCA file.

---

## Project Structure

```
aerovia/
├── dashboard/
│   ├── app.py                  ← Streamlit entry point & navigation
│   └── pages/
│       ├── portfolio.py        ← Route network map + DGCA file upload
│       ├── route_builder.py    ← Interactive route economics builder
│       ├── scenario_lab.py     ← What-if sliders, comparisons, heatmap
│       ├── ml_forecast.py      ← ATF + demand forecasts + anomaly detection
│       └── ai_analyst.py       ← Claude-powered NLP analyst
├── economics/
│   ├── engine.py               ← RASK / CASK / BELF core engine
│   └── scenario_store.py       ← Session-based scenario persistence
├── ingestion/
│   └── loader.py               ← DGCA CSV/Excel parser + demo data generator
├── config/
│   └── constants.py            ← Airport coords, airlines, aircraft, cost defaults
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Economics Model

AeroVia computes the following for every route:

| Metric | Formula |
|--------|---------|
| **ASK** | Seats × Distance × Frequency |
| **RPK** | ASK × Load Factor |
| **RASK** | (RPK × Yield) / ASK |
| **CASK** | Total Cost / ASK |
| **BELF** | Total Cost / (ASK × Yield) |
| **Margin** | (Revenue − Cost) / Revenue |
| **LF Cushion** | Load Factor − BELF |

Cost components: ATF fuel, crew (% of revenue), maintenance (per flight hour), airport charges (per sector), overhead (% of revenue).

All inputs are fully editable per route. Defaults are calibrated to Indian domestic aviation benchmarks (2024).

---

## Supported Airports

24 Indian airports including DEL, BOM, BLR, MAA, HYD, CCU, PNQ, GOI, AMD, COK, JAI, LKO, SXR, and more.

---

## Data

AeroVia works with **DGCA traffic statistics** (available at [dgca.gov.in](https://www.dgca.gov.in)). Upload any DGCA monthly/annual CSV or Excel — the column mapper handles common naming variations automatically.

No data is included in this repository. Use the built-in demo data generator to explore without a real file.

---

## Tech Stack

- **UI** — [Streamlit](https://streamlit.io)
- **Charts** — [Plotly](https://plotly.com/python/)
- **Maps** — Plotly Geo (Scattergeo)
- **Data** — pandas, numpy
- **AI** — [Anthropic Claude API](https://anthropic.com)
- **ML** — scikit-learn (anomaly detection), custom forecasting

---

## Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

---

## License

[MIT](LICENSE)

---

<div align="center">
Built for Indian aviation · Powered by Claude
</div>
