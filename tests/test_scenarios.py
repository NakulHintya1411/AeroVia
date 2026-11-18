import pytest

from config.plans import get_plan
from services import accounts, scenarios
from services.scenarios import ScenarioError, ScenarioLimitReached

INPUTS = {"origin": "DEL", "destination": "BOM", "load_factor": 0.82}
ECON = {"origin": "DEL", "destination": "BOM", "margin_pct": 4.2, "rask": 5.1, "cask": 4.9}


def test_save_list_get_delete(org_user):
    org = org_user.org_id
    scenarios.save(org, org_user.user_id, "Base case", INPUTS, ECON)
    scenarios.save(org, org_user.user_id, "High LF", {**INPUTS, "load_factor": 0.9}, ECON)
    assert scenarios.list_names(org) == ["Base case", "High LF"]
    assert scenarios.get(org, "High LF")["inputs"]["load_factor"] == 0.9
    assert scenarios.get(org, "missing") == {}

    scenarios.remove(org, "Base case")
    assert scenarios.list_names(org) == ["High LF"]
    scenarios.clear(org)
    assert scenarios.list_names(org) == []


def test_saving_same_name_overwrites(org_user):
    org = org_user.org_id
    scenarios.save(org, org_user.user_id, "Case", INPUTS, ECON)
    scenarios.save(org, org_user.user_id, "Case", INPUTS, {**ECON, "margin_pct": -1.0})
    assert scenarios.list_names(org) == ["Case"]
    assert scenarios.get(org, "Case")["economics"]["margin_pct"] == -1.0


def test_compare_keeps_requested_order_and_skips_unknown(org_user):
    org = org_user.org_id
    for n in ["A", "B", "C"]:
        scenarios.save(org, org_user.user_id, n, INPUTS, ECON)
    assert [s["name"] for s in scenarios.compare(org, ["C", "nope", "A"])] == ["C", "A"]


def test_plan_limit_enforced(org_user):
    org = org_user.org_id
    limit = get_plan("free").max_scenarios
    for i in range(limit):
        scenarios.save(org, org_user.user_id, f"S{i}", INPUTS, ECON)
    with pytest.raises(ScenarioLimitReached):
        scenarios.save(org, org_user.user_id, "One too many", INPUTS, ECON)
    # Updating an existing scenario is still allowed at the limit.
    scenarios.save(org, org_user.user_id, "S0", INPUTS, ECON)


def test_blank_name_rejected(org_user):
    with pytest.raises(ScenarioError, match="name"):
        scenarios.save(org_user.org_id, org_user.user_id, "   ", INPUTS, ECON)


def test_organisations_cannot_see_each_others_scenarios(org_user):
    other = accounts.register("rival@example.com", "Rival", "long-enough-pw", "Rival Org")
    scenarios.save(org_user.org_id, org_user.user_id, "Secret route", INPUTS, ECON)

    assert scenarios.list_names(other.org_id) == []
    assert scenarios.get(other.org_id, "Secret route") == {}
    assert scenarios.compare(other.org_id, ["Secret route"]) == []
    scenarios.remove(other.org_id, "Secret route")
    scenarios.clear(other.org_id)
    assert scenarios.list_names(org_user.org_id) == ["Secret route"]

    # Same name in a different org is a separate scenario.
    scenarios.save(other.org_id, other.user_id, "Secret route", INPUTS, {**ECON, "margin_pct": 9.9})
    assert scenarios.get(org_user.org_id, "Secret route")["economics"]["margin_pct"] == 4.2


def test_numpy_values_are_stored_as_plain_numbers(org_user):
    np = pytest.importorskip("numpy")
    scenarios.save(org_user.org_id, org_user.user_id, "np", {"lf": np.float64(0.8)}, {"x": np.float32(1.5)})
    got = scenarios.get(org_user.org_id, "np")
    assert got["inputs"]["lf"] == pytest.approx(0.8)
    assert got["economics"]["x"] == pytest.approx(1.5)
