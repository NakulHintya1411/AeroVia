# AeroVia — GitHub Upload Guide

Follow these steps exactly to publish AeroVia on GitHub.

---

## Step 1 — Create the GitHub Repository

1. Go to [github.com/new](https://github.com/new)
2. Fill in:
   - **Repository name:** `aerovia`
   - **Description:** `Route profitability simulator for Indian domestic aviation — RASK/CASK/BELF modelling, ML forecasts, AI analyst`
   - **Visibility:** Public (or Private if you prefer)
   - ❌ Do NOT check "Add a README file" — we have our own
   - ❌ Do NOT add .gitignore — we have our own
   - ❌ Do NOT choose a license — we have our own
3. Click **Create repository**

---

## Step 2 — Extract the Zip

Unzip `aerovia_github.zip` on your machine. You should see:

```
aerovia/
├── dashboard/
├── economics/
├── ingestion/
├── config/
├── .env.example
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

---

## Step 3 — Initialize Git and Push

Open a terminal inside the `aerovia/` folder and run these commands one by one:

```bash
git init
git add .
git commit -m "Initial release: AeroVia v2.0"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/aerovia.git
git push -u origin main
```

> Replace `YOUR_USERNAME` with your actual GitHub username.

---

## Step 4 — Create a Release (v2.0.0)

1. On your GitHub repo page, click **Releases** (right sidebar)
2. Click **Create a new release**
3. Fill in:
   - **Tag:** `v2.0.0`
   - **Title:** `AeroVia v2.0 — Full Release`
   - **Description:**
     ```
     First public release of AeroVia.

     ## What's included
     - Route Builder with fully customizable cost inputs
     - Scenario Lab with live what-if sliders and sensitivity heatmap
     - Save & compare up to 6 named scenarios
     - Portfolio route map with DGCA file upload
     - ML forecasts: ATF price, demand, anomaly detection
     - AI Analyst powered by Claude API
     - 24 Indian airports, 7 airlines, 6 aircraft types
     ```
4. Click **Publish release**

---

## Step 5 — Add Repository Topics

On your repo page, click the ⚙ gear next to **About** (top right of repo) and add these topics:

```
aviation  airline  streamlit  python  india  dgca  rask  cask  route-profitability  anthropic  claude
```

This makes your repo discoverable.

---

## Step 6 — Update README with Your Username

In `README.md`, replace:
```
git clone https://github.com/YOUR_USERNAME/aerovia.git
```
with your actual GitHub username before or after pushing.

---

## What NOT to Do

- ❌ Never push your `.env` file — it contains your API key
- ❌ Never push real DGCA data files (`.csv`, `.xlsx`) — they may be large or licensed
- ❌ Never push `__pycache__/` folders — the `.gitignore` handles this
- ❌ Don't upload old v1 files — only this version belongs on GitHub

---

## Optional: Add a Screenshot

A screenshot in the README dramatically improves how your project looks. After launching the app locally:
1. Take a screenshot of the Route Builder or Portfolio page
2. Create a folder: `docs/` in the repo
3. Add the image there: `docs/screenshot.png`
4. Add this line to README.md under the title:

```markdown
![AeroVia Screenshot](docs/screenshot.png)
```

Then push again:
```bash
git add .
git commit -m "Add screenshot to README"
git push
```
