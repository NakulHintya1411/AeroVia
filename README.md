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
| **Save & Compare** | Named scenarios saved to your organisation, compared side-by-side, exported to CSV |
| **Portfolio Map** | Plotly geo map of your full route network, arcs colour-coded by profitability |
| **DGCA Upload** | Drag-and-drop CSV/Excel with automatic column mapping UI |
| **ML Forecasts** | ATF price forecasting, demand prediction with confidence bands, anomaly detection |
| **AI Analyst** | Claude-powered NLP chat with live route context — ask anything about route economics |

---

## Quick Start (local development)

```bash
git clone https://github.com/NakulHintya1411/AeroVia.git
cd AeroVia

python -m venv .venv
# Windows:  .venv\Scriptsctivate
# macOS / Linux:  source .venv/bin/activate

pip install -r requirements-dev.txt
cp .env.example .env          # then fill in ANTHROPIC_API_KEY if you want the AI Analyst
streamlit run dashboard/app.py
```

Open **http://localhost:8501**. On first launch there are no accounts: the sign-up form
creates the first user and their organisation. Locally the database is a SQLite file at
`instance/aerovia.db`, created and migrated automatically.

---

## Configuration

All settings are environment variables (or `.env` locally). See `.env.example`.

| Variable | Purpose | Default |
|---|---|---|
| `DATABASE_URL` | Postgres URL in production | SQLite at `instance/aerovia.db` |
| `ANTHROPIC_API_KEY` | Server-side key for the AI Analyst. Users never see it. Empty = AI off | empty |
| `CLAUDE_MODEL` | Model for the AI Analyst | `claude-opus-5-5` |
| `CLAUDE_EFFORT` | Effort level: `low` / `medium` / `high` | `medium` |
| `AEROVIA_ALLOW_SIGNUP` | Let anyone create an account. The first account is always allowed | `true` |
| `AEROVIA_ENV` | `development` / `staging` / `production` | `development` |
| `AEROVIA_TRIAL_DAYS` | Days of free Pro trial for new organisations (0 = none) | `14` |
| `RAZORPAY_KEY_ID`, `RAZORPAY_KEY_SECRET` | Razorpay API keys (test mode outside production). Empty = billing off | empty |
| `RAZORPAY_PLAN_PRO`, `RAZORPAY_PLAN_TEAM` | Razorpay plan IDs for the paid plans | empty |
| `RAZORPAY_WEBHOOK_SECRET` | Secret for verifying Razorpay webhooks (API service) | empty |
| `AEROVIA_SERVICE` | Docker only: `web` (Streamlit) or `api` (webhooks) | `web` |

## Accounts, organisations and plans

- Users sign up with email and password (bcrypt-hashed). Five wrong passwords lock the account for 15 minutes.
- Each sign-up creates an **organisation**; the user is its owner. Saved scenarios and AI usage belong to the organisation.
- Plans live in `config/plans.py` (Free / Pro / Team). They set the scenario limit and monthly AI Analyst messages.
- New organisations get a free Pro trial (`AEROVIA_TRIAL_DAYS`, default 14 days, no card needed), then drop to Free unless they subscribe.

## Billing (Razorpay)

Owners and admins subscribe on the **Billing** page. AeroVia creates a Razorpay subscription and sends them to
Razorpay's hosted payment page; card/UPI details never touch AeroVia. An organisation's plan is the best of its
base plan, an active trial, and any subscription in `authenticated`, `active` or `pending` (renewal retrying).
Cancelling takes effect at the end of the paid period.

Subscription state always comes from Razorpay's API: the Billing page refreshes it on load, and webhooks (sent to the
separate API service, because Streamlit can't receive them) trigger the same refresh. Webhooks are verified with
HMAC-SHA256 and de-duplicated by event ID.

**Setup (test mode first):**

1. In the Razorpay Dashboard switch to **Test Mode**, then create two monthly plans under
   **Subscriptions → Plans** (Pro and Team, at your prices). Copy their `plan_...` IDs into
   `RAZORPAY_PLAN_PRO` / `RAZORPAY_PLAN_TEAM`.
2. **Account & Settings → API Keys**: generate a test key pair → `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET`.
3. **Account & Settings → Webhooks**: add `https://<your API host>/webhooks/razorpay`, choose a secret
   (→ `RAZORPAY_WEBHOOK_SECRET`) and tick all `subscription.*` events.
4. Restart the app. Prices on the Billing page are read from the Razorpay plans.

Locally, the Billing page works without webhooks (it re-syncs from Razorpay when opened). To test webhooks
locally, run the API (`uvicorn api.main:app --port 8000`) and expose it with a tunnel such as ngrok.

## Database migrations

The schema is managed with Alembic. The app applies pending migrations on start-up; the Docker image runs
`alembic upgrade head` before launching. After changing `db/models.py`:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

`tests/test_migrations.py` fails if models and migrations drift apart.

## Tests

```bash
pytest -q                                              # SQLite
TEST_DATABASE_URL=postgresql://user:pass@localhost/aerovia_test pytest -q   # Postgres (wiped per test)
```

GitHub Actions runs the suite against both SQLite and Postgres on every push and pull request.

## Deploying

One Docker image runs both services: `AEROVIA_SERVICE=web` (the Streamlit app, default) and
`AEROVIA_SERVICE=api` (the webhook API, health check `/healthz`). Each container applies migrations on start;
a Postgres advisory lock keeps two services from migrating at the same time.

The Render Blueprint (`render.yaml`) sets up staging: both services plus managed Postgres in Singapore. In Render
choose **New → Blueprint**, select this repository, and fill in the keys it asks for. Staging has sign-up closed,
so the first account you create becomes the owner. Then add the Razorpay webhook (Billing step 3) using the API
service's URL. The image works on any container host that sets `PORT` and `DATABASE_URL`.

---

## Project Structure

```
AeroVia/
├── dashboard/
│   ├── app.py                ← Streamlit entry point (auth gate → Portfolio Overview)
│   ├── pages/                ← Portfolio, Route Builder, Scenario Lab, ML Forecasts,
│   │                           AI Analyst, Route Comparison, P&L Dashboard, Settings, Billing
│   ├── utils/auth.py         ← Sign-in / sign-up screens and the per-page auth gate
│   └── data/                 ← Bundled sample DGCA traffic file
├── services/                 ← Business logic (no Streamlit): accounts, billing, scenarios, usage, AI analyst
├── api/                      ← FastAPI service: Razorpay webhooks, /healthz
├── db/                       ← SQLAlchemy models and session management
├── migrations/               ← Alembic migrations
├── economics/                ← RASK / CASK / BELF engine; scenario_store wrapper for pages
├── ingestion/                ← DGCA CSV/Excel parser + demo data generator
├── config/                   ← constants, settings (env vars), plans
├── tests/                    ← pytest suite
├── scripts/                  ← Container start-up and health check
├── Dockerfile, render.yaml   ← Deployment
└── .github/workflows/ci.yml  ← CI
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
- **Forecasting** — numpy trend models and z-score anomaly detection
- **Database** — SQLAlchemy + Alembic (Postgres in production, SQLite locally)
- **Auth** — email + password with bcrypt, organisation-scoped data

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
