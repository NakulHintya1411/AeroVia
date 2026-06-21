"""DGCA loader — reads uploaded CSV/Excel and normalises columns."""
import io
import pandas as pd
import numpy as np

COLUMN_ALIASES = {
    "airline_code": ["airline_code", "carrier", "airline", "operator", "iata_code"],
    "origin": ["origin", "from", "dep", "departure", "origin_iata", "source"],
    "destination": ["destination", "to", "arr", "arrival", "dest", "destination_iata"],
    "passengers": ["passengers", "pax", "no_of_passengers", "traffic", "total_passengers"],
    "flights": ["flights", "departures", "no_of_flights", "frequency", "sectors"],
    "seats": ["seats", "capacity", "seat_capacity", "available_seats"],
    "load_factor": ["load_factor", "lf", "plf", "passenger_load_factor"],
    "year": ["year", "yr", "financial_year"],
    "month": ["month", "mon", "period", "month_no"],
}


def _normalise_col(df: pd.DataFrame) -> pd.DataFrame:
    rename = {}
    lower_cols = {c.lower().replace(" ", "_").replace("-", "_"): c for c in df.columns}
    for canonical, aliases in COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in lower_cols and canonical not in df.columns:
                rename[lower_cols[alias]] = canonical
                break
    return df.rename(columns=rename)


def load_dgca_file(uploaded_file) -> tuple[pd.DataFrame, list]:
    """Returns (dataframe, list_of_warnings)."""
    warnings = []
    name = uploaded_file.name.lower()
    try:
        if name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        return pd.DataFrame(), [f"Could not read file: {e}"]

    df = _normalise_col(df)

    if "load_factor" not in df.columns and "passengers" in df.columns and "seats" in df.columns:
        df["load_factor"] = df["passengers"] / df["seats"].replace(0, np.nan)
        warnings.append("load_factor derived from passengers/seats")

    if "load_factor" in df.columns:
        df["load_factor"] = df["load_factor"].clip(0, 1)

    missing = [c for c in ["origin", "destination", "airline_code"] if c not in df.columns]
    if missing:
        warnings.append(f"Missing expected columns: {missing}. Check column mapping below.")

    return df, warnings


# ── Realistic route profiles ──────────────────────────────────────────────────
# Based on real Indian aviation dynamics:
# - High-competition metro routes: yield compressed, margins thin
# - Thin tier-2 routes: low load factors, sometimes loss-making
# - Seasonal leisure routes: profitable in peak, bleed in lean
# - Gulf feeders: Air India Express cash cows
# - UDAN routes: subsidised but low yield

ROUTE_PROFILES = {
    # Metro trunk routes — high competition, yield compressed
    ("DEL", "BOM"): {"lf_range": (0.84, 0.91), "yield_factor": 0.88, "label": "High competition"},
    ("DEL", "BLR"): {"lf_range": (0.82, 0.89), "yield_factor": 0.87, "label": "High competition"},
    ("BOM", "BLR"): {"lf_range": (0.80, 0.88), "yield_factor": 0.85, "label": "High competition"},
    ("DEL", "HYD"): {"lf_range": (0.78, 0.86), "yield_factor": 0.86, "label": "High competition"},
    ("DEL", "MAA"): {"lf_range": (0.76, 0.84), "yield_factor": 0.85, "label": "Competitive"},
    ("BOM", "HYD"): {"lf_range": (0.75, 0.83), "yield_factor": 0.84, "label": "Competitive"},

    # Profitable leisure/business routes
    ("BOM", "COK"): {"lf_range": (0.82, 0.90), "yield_factor": 0.95, "label": "Strong leisure"},
    ("DEL", "SXR"): {"lf_range": (0.78, 0.88), "yield_factor": 1.05, "label": "Premium leisure"},
    ("BOM", "GOI"): {"lf_range": (0.80, 0.92), "yield_factor": 1.08, "label": "Leisure peak"},
    ("DEL", "IXL"): {"lf_range": (0.72, 0.85), "yield_factor": 1.15, "label": "Premium thin"},
    ("MAA", "COK"): {"lf_range": (0.76, 0.84), "yield_factor": 0.92, "label": "Regional"},

    # Thin tier-2 routes — often loss-making or breakeven
    ("DEL", "IXJ"): {"lf_range": (0.58, 0.72), "yield_factor": 0.78, "label": "Thin route"},
    ("BOM", "NAG"): {"lf_range": (0.55, 0.68), "yield_factor": 0.75, "label": "Loss-making"},
    ("DEL", "RPR"): {"lf_range": (0.52, 0.65), "yield_factor": 0.72, "label": "UDAN thin"},
    ("CCU", "GAU"): {"lf_range": (0.60, 0.74), "yield_factor": 0.80, "label": "Regional thin"},
    ("BOM", "IXZ"): {"lf_range": (0.62, 0.76), "yield_factor": 0.88, "label": "Seasonal"},

    # Northeast — chronically loss-making without UDAN subsidy
    ("CCU", "IMF"): {"lf_range": (0.48, 0.64), "yield_factor": 0.68, "label": "UDAN loss"},
    ("DEL", "DIB"): {"lf_range": (0.55, 0.70), "yield_factor": 0.74, "label": "Northeast thin"},
    ("GAU", "DMU"): {"lf_range": (0.42, 0.58), "yield_factor": 0.65, "label": "Very thin"},

    # Breakeven routes
    ("DEL", "CCU"): {"lf_range": (0.72, 0.82), "yield_factor": 0.82, "label": "Breakeven"},
    ("BLR", "MAA"): {"lf_range": (0.70, 0.80), "yield_factor": 0.80, "label": "Breakeven"},
    ("HYD", "COK"): {"lf_range": (0.68, 0.78), "yield_factor": 0.82, "label": "Borderline"},
}

DEFAULT_PROFILE = {"lf_range": (0.65, 0.78), "yield_factor": 0.82, "label": "Standard"}


def generate_demo_data(n_months: int = 12) -> pd.DataFrame:
    """
    Realistic DGCA-style demo data.
    Routes are calibrated to reflect actual Indian aviation economics:
    - Metro trunk routes: high LF but yield compressed → thin margins
    - Tier-2 routes: low LF → often loss-making
    - Leisure routes: strong yield → profitable
    - Northeast/UDAN: structurally loss-making
    """
    np.random.seed(2024)
    rows = []

    routes = list(ROUTE_PROFILES.keys())
    airlines = ["6E", "IX", "AI", "QP", "SG"]

    # Airline-specific yield adjustments
    airline_yield = {"6E": 0.96, "IX": 0.90, "AI": 1.08, "QP": 0.94, "SG": 0.88}
    # Airline-specific LF adjustments
    airline_lf = {"6E": 0.04, "IX": 0.02, "AI": -0.03, "QP": 0.01, "SG": -0.05}

    for month in range(1, n_months + 1):
        # Seasonal multipliers
        if month in [11, 12, 1, 2]:
            season_lf = 0.06; season_yield = 1.12   # Peak — higher LF and yield
        elif month in [5, 6, 7]:
            season_lf = -0.08; season_yield = 0.88  # Lean — lower LF, discounting
        else:
            season_lf = 0.0; season_yield = 1.0     # Shoulder

        for orig, dest in routes:
            profile = ROUTE_PROFILES.get((orig, dest), DEFAULT_PROFILE)
            lf_lo, lf_hi = profile["lf_range"]

            # Pick 2-3 airlines per route realistically
            n_airlines = np.random.choice([2, 3], p=[0.4, 0.6])
            route_airlines = np.random.choice(airlines, size=n_airlines, replace=False)

            for airline in route_airlines:
                # Load factor with seasonal and airline adjustment
                base_lf = np.random.uniform(lf_lo, lf_hi)
                final_lf = np.clip(
                    base_lf + season_lf + airline_lf.get(airline, 0),
                    0.38, 0.96
                )
                base_seats = np.random.randint(5000, 18000)
                passengers = int(base_seats * final_lf)

                rows.append({
                    "year": 2024,
                    "month": month,
                    "airline_code": airline,
                    "origin": orig,
                    "destination": dest,
                    "flights": np.random.randint(28, 180),
                    "seats": base_seats,
                    "passengers": passengers,
                    "load_factor": round(final_lf, 3),
                    # Store yield factor for economics engine
                    "_yield_factor": round(
                        profile["yield_factor"] * airline_yield.get(airline, 1.0) * season_yield, 3
                    ),
                    "_route_label": profile["label"],
                })

    return pd.DataFrame(rows)
