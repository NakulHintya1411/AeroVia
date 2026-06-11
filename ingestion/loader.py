"""DGCA loader — reads uploaded CSV/Excel and normalises columns."""
import io
import pandas as pd
import numpy as np
from typing import Optional

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

    # Derive load_factor if missing
    if "load_factor" not in df.columns and "passengers" in df.columns and "seats" in df.columns:
        df["load_factor"] = df["passengers"] / df["seats"].replace(0, np.nan)
        warnings.append("load_factor derived from passengers/seats")

    # Clamp load factor
    if "load_factor" in df.columns:
        df["load_factor"] = df["load_factor"].clip(0, 1)

    missing = [c for c in ["origin", "destination", "airline_code"] if c not in df.columns]
    if missing:
        warnings.append(f"Missing expected columns: {missing}. Check column mapping below.")

    return df, warnings


def generate_demo_data(n_months: int = 12) -> pd.DataFrame:
    """Synthetic DGCA-style data for demo/testing."""
    import random, math
    rows = []
    routes = [
        ("DEL", "BOM"), ("DEL", "BLR"), ("BOM", "BLR"), ("DEL", "HYD"),
        ("BOM", "COK"), ("DEL", "CCU"), ("BLR", "HYD"), ("DEL", "MAA"),
    ]
    airlines = ["6E", "AI", "SG", "UK"]
    for month in range(1, n_months + 1):
        season = 1.15 if month in [11, 12, 1, 2] else 0.90 if month in [5, 6, 7] else 1.0
        for orig, dest in routes:
            for airline in airlines[:3]:
                base_pax = random.randint(8000, 18000)
                seats = int(base_pax / random.uniform(0.72, 0.88))
                rows.append({
                    "year": 2024,
                    "month": month,
                    "airline_code": airline,
                    "origin": orig,
                    "destination": dest,
                    "flights": random.randint(60, 150),
                    "seats": int(seats * season),
                    "passengers": int(base_pax * season),
                    "load_factor": round(base_pax / seats, 3),
                })
    return pd.DataFrame(rows)
