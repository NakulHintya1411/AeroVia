import math

import pytest

from config.constants import AIRCRAFT_TYPES, DEFAULT_COST_ASSUMPTIONS
from economics.engine import (
    RouteInputs,
    compute_route_economics,
    haversine_km,
    run_scenario,
    sensitivity_grid,
)

AIRCRAFT = next(iter(AIRCRAFT_TYPES))


def base_inputs(**overrides) -> RouteInputs:
    kwargs = dict(origin="DEL", destination="BOM", airline_code="6E", aircraft_type=AIRCRAFT,
                  daily_frequency=3, load_factor=0.82)
    kwargs.update(overrides)
    return RouteInputs(**kwargs)


def test_haversine_del_bom_is_about_1140_km():
    assert 1100 < haversine_km("DEL", "BOM") < 1180


def test_haversine_is_symmetric_and_zero_for_same_airport():
    assert haversine_km("DEL", "BLR") == pytest.approx(haversine_km("BLR", "DEL"))
    assert haversine_km("DEL", "DEL") == pytest.approx(0.0)


def test_core_metrics_follow_their_definitions():
    e = compute_route_economics(base_inputs())
    seats = AIRCRAFT_TYPES[AIRCRAFT]["seats"]
    assert e.seats == seats
    assert e.ask == pytest.approx(seats * e.distance_km * 3, rel=1e-3)
    assert e.rpk == pytest.approx(e.ask * 0.82, rel=1e-3)
    assert e.profit_inr == pytest.approx(e.total_revenue_inr - e.total_cost_inr, abs=2)
    assert e.lf_cushion == pytest.approx(e.load_factor - e.belf, abs=1e-3)
    assert math.copysign(1, e.margin_pct) == math.copysign(1, e.profit_inr)


def test_cost_components_add_up():
    e = compute_route_economics(base_inputs())
    parts = (e.fuel_cost_inr + e.crew_cost_inr + e.maintenance_cost_inr
             + e.airport_cost_inr + e.overhead_cost_inr)
    assert parts == pytest.approx(e.total_cost_inr, abs=5)


def test_explicit_zero_override_is_respected():
    """Regression: `x or default` used to replace an explicit 0 with the default."""
    with_default = compute_route_economics(base_inputs())
    zero_overhead = compute_route_economics(base_inputs(overhead_pct=0.0))
    assert DEFAULT_COST_ASSUMPTIONS["overhead_pct_of_revenue"] > 0
    assert zero_overhead.overhead_cost_inr == 0
    assert zero_overhead.profit_inr > with_default.profit_inr


def test_none_override_uses_default():
    explicit = compute_route_economics(base_inputs(
        atf_price_inr_per_litre=DEFAULT_COST_ASSUMPTIONS["atf_price_inr_per_litre"]))
    implicit = compute_route_economics(base_inputs(atf_price_inr_per_litre=None))
    assert explicit.fuel_cost_inr == implicit.fuel_cost_inr


def test_zero_yield_does_not_divide_by_zero():
    e = compute_route_economics(base_inputs(yield_inr_per_km=0.0))
    assert e.total_revenue_inr == 0
    assert e.margin_pct == 0.0
    assert e.belf == 0.0


def test_higher_fuel_price_lowers_profit():
    results = sensitivity_grid(base_inputs(), "atf_price_inr_per_litre", [60.0, 90.0, 120.0])
    profits = [econ.profit_inr for _, econ in results]
    assert profits == sorted(profits, reverse=True)


def test_run_scenario_does_not_mutate_base():
    base = base_inputs()
    run_scenario(base, {"load_factor": 0.5})
    assert base.load_factor == 0.82
