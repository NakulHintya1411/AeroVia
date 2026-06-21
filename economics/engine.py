"""AeroVia Economics Engine — RASK, CASK, BELF, scenarios."""
import math
from dataclasses import dataclass, field, asdict
from typing import Dict, Optional
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config.constants import INDIAN_AIRPORTS, INTERNATIONAL_AIRPORTS, AIRCRAFT_TYPES, DEFAULT_COST_ASSUMPTIONS

ALL_AIRPORTS = {**INDIAN_AIRPORTS, **INTERNATIONAL_AIRPORTS}


def haversine_km(iata1: str, iata2: str) -> float:
    a = ALL_AIRPORTS.get(iata1)
    b = ALL_AIRPORTS.get(iata2)
    if not a or not b:
        return 1000.0
    R = 6371
    lat1, lon1 = math.radians(a["lat"]), math.radians(a["lon"])
    lat2, lon2 = math.radians(b["lat"]), math.radians(b["lon"])
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(h))


@dataclass
class RouteInputs:
    origin: str
    destination: str
    airline_code: str
    aircraft_type: str
    daily_frequency: int = 1
    load_factor: float = 0.82
    # cost overrides (None = use defaults)
    atf_price_inr_per_litre: Optional[float] = None
    crew_cost_pct: Optional[float] = None
    maintenance_cost_per_fh: Optional[float] = None
    airport_charges_per_sector: Optional[float] = None
    overhead_pct: Optional[float] = None
    yield_inr_per_km: Optional[float] = None
    usd_inr_rate: Optional[float] = None


@dataclass
class RouteEconomics:
    origin: str
    destination: str
    airline_code: str
    aircraft_type: str
    distance_km: float
    seats: int
    load_factor: float
    daily_frequency: int

    # Revenue
    rask: float = 0.0            # Revenue per ASK (paise)
    total_revenue_inr: float = 0.0

    # Costs
    cask: float = 0.0            # Cost per ASK (paise)
    fuel_cost_inr: float = 0.0
    crew_cost_inr: float = 0.0
    maintenance_cost_inr: float = 0.0
    airport_cost_inr: float = 0.0
    overhead_cost_inr: float = 0.0
    total_cost_inr: float = 0.0

    # Profitability
    margin_pct: float = 0.0
    profit_inr: float = 0.0
    belf: float = 0.0            # Break-Even Load Factor
    lf_cushion: float = 0.0      # LF - BELF

    # Per-flight
    flight_time_hr: float = 0.0
    ask: float = 0.0
    rpk: float = 0.0

    def to_dict(self):
        return asdict(self)


def compute_route_economics(inputs: RouteInputs, defaults: dict = None) -> RouteEconomics:
    d = {**DEFAULT_COST_ASSUMPTIONS, **(defaults or {})}
    ac = AIRCRAFT_TYPES[inputs.aircraft_type]

    distance_km = haversine_km(inputs.origin, inputs.destination)
    flight_time_hr = distance_km / ac["speed_kmh"]
    seats = ac["seats"]
    freq = inputs.daily_frequency

    # ASK / RPK (per day)
    ask = seats * distance_km * freq
    rpk = ask * inputs.load_factor

    # ── Revenue ──────────────────────────────────────────────────────────────
    yield_inr_km = inputs.yield_inr_per_km or d["avg_yield_inr_per_km"]
    total_revenue = rpk * yield_inr_km
    rask = (total_revenue / ask) * 100  # paise per ASK

    # ── Costs ────────────────────────────────────────────────────────────────
    atf = inputs.atf_price_inr_per_litre or d["atf_price_inr_per_litre"]
    fuel_litres = ac["fuel_burn_kg_hr"] * flight_time_hr * freq * 0.8  # kg→litre ~0.8
    fuel_cost = fuel_litres * atf

    crew_pct = inputs.crew_cost_pct or d["crew_cost_pct_of_revenue"]
    crew_cost = total_revenue * crew_pct

    maint_per_fh = inputs.maintenance_cost_per_fh or d["maintenance_cost_per_flight_hour"]
    maintenance_cost = maint_per_fh * flight_time_hr * freq

    airport_per_sector = inputs.airport_charges_per_sector or d["airport_charges_per_sector"]
    airport_cost = airport_per_sector * freq

    overhead_pct = inputs.overhead_pct or d["overhead_pct_of_revenue"]
    overhead_cost = total_revenue * overhead_pct

    total_cost = fuel_cost + crew_cost + maintenance_cost + airport_cost + overhead_cost
    cask = (total_cost / ask) * 100  # paise per ASK

    profit = total_revenue - total_cost
    margin_pct = (profit / total_revenue * 100) if total_revenue > 0 else 0.0
    belf = total_cost / (ask * yield_inr_km) if (ask * yield_inr_km) > 0 else 0.0
    lf_cushion = inputs.load_factor - belf

    return RouteEconomics(
        origin=inputs.origin,
        destination=inputs.destination,
        airline_code=inputs.airline_code,
        aircraft_type=inputs.aircraft_type,
        distance_km=round(distance_km, 1),
        seats=seats,
        load_factor=inputs.load_factor,
        daily_frequency=freq,
        rask=round(rask, 2),
        total_revenue_inr=round(total_revenue, 0),
        cask=round(cask, 2),
        fuel_cost_inr=round(fuel_cost, 0),
        crew_cost_inr=round(crew_cost, 0),
        maintenance_cost_inr=round(maintenance_cost, 0),
        airport_cost_inr=round(airport_cost, 0),
        overhead_cost_inr=round(overhead_cost, 0),
        total_cost_inr=round(total_cost, 0),
        margin_pct=round(margin_pct, 2),
        profit_inr=round(profit, 0),
        belf=round(belf, 4),
        lf_cushion=round(lf_cushion, 4),
        flight_time_hr=round(flight_time_hr, 2),
        ask=round(ask, 0),
        rpk=round(rpk, 0),
    )


def run_scenario(base: RouteInputs, overrides: dict) -> RouteEconomics:
    """Apply delta overrides to a base RouteInputs and recompute."""
    import copy
    inp = copy.deepcopy(base)
    for k, v in overrides.items():
        if hasattr(inp, k):
            setattr(inp, k, v)
    return compute_route_economics(inp)


def sensitivity_grid(base: RouteInputs, param: str, values: list) -> list:
    """Return list of (value, RouteEconomics) for a single param sweep."""
    results = []
    for v in values:
        econ = run_scenario(base, {param: v})
        results.append((v, econ))
    return results
