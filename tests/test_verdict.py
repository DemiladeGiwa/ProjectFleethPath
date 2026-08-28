import pytest

from api.main import _upfront_capital, build_advanced_dashboard, calculate_verdict
from engine.models import FleetInputPayload, OverridesConfig, PathwayOutputMetrics
from engine.tco_calculator import calculate_all_pathways


PATHWAYS = ("diesel", "bev", "hydrogen", "cng", "biodiesel")


def _metric(
    fuel_type,
    tco_total,
    lifecycle_co2e_tons,
    vehicle_capex=1000.0,
    infra_capex=0.0,
    fuel_opex=50.0,
    maintenance_opex=50.0,
    incentives=0.0,
    currency="USD",
):
    # DISCLOSED CHANGE (pricing-bug remediation, phase 1): currency is now a
    # required field on PathwayOutputMetrics with no default. These fixtures
    # use arbitrary synthetic numbers, not real regional data, so "USD" is a
    # safe default -- every call in this file uses the same currency, which
    # satisfies calculate_verdict's mixed-currency guard (see
    # api/main.py::_assert_single_currency). Pass currency="CAD" explicitly
    # if a future test needs to exercise that guard directly.
    return PathwayOutputMetrics(
        fuel_type=fuel_type,
        currency=currency,
        tco_total=tco_total,
        capex_vehicle_amortized=vehicle_capex,
        capex_infra_amortized=infra_capex,
        opex_fuel=fuel_opex,
        opex_maintenance=maintenance_opex,
        incentives_applied=incentives,
        lifecycle_co2e_tons=lifecycle_co2e_tons,
        cold_climate_adjustment_applied=False,
    )


def test_diesel_wins_when_it_dominates_cost_and_carbon():
    pathways = {
        "diesel": _metric("diesel", 100.0, 10.0),
        "bev": _metric("bev", 200.0, 20.0),
        "hydrogen": _metric("hydrogen", 300.0, 30.0),
        "cng": _metric("cng", 250.0, 25.0),
        "biodiesel": _metric("biodiesel", 150.0, 15.0),
    }
    verdict = calculate_verdict(pathways, fleet_lifecycle_years=12)
    assert verdict.winner_pathway == "diesel"
    assert verdict.payback_years == 0.0


def test_equal_normalized_scores_use_canonical_pathway_order():
    pathways = {
        fuel_type: _metric(fuel_type, 100.0, 10.0)
        for fuel_type in reversed(PATHWAYS)
    }
    verdict = calculate_verdict(pathways, fleet_lifecycle_years=12)
    assert verdict.winner_pathway == "diesel"


def test_alt_pathway_without_lifecycle_recovery_has_no_payback():
    pathways = {
        "diesel": _metric("diesel", 100.0, 100.0, vehicle_capex=1000.0, fuel_opex=100.0),
        "bev": _metric(
            "bev",
            90.0,
            0.0,
            vehicle_capex=2000.0,
            fuel_opex=150.0,
        ),
        "hydrogen": _metric("hydrogen", 300.0, 300.0),
        "cng": _metric("cng", 250.0, 250.0),
        "biodiesel": _metric("biodiesel", 200.0, 200.0),
    }
    verdict = calculate_verdict(pathways, fleet_lifecycle_years=12)
    assert verdict.winner_pathway == "bev"
    assert verdict.payback_years is None


def test_winner_with_no_capital_premium_has_zero_payback():
    pathways = {
        "diesel": _metric("diesel", 100.0, 100.0, vehicle_capex=1000.0),
        "bev": _metric("bev", 90.0, 0.0, vehicle_capex=1000.0, fuel_opex=25.0),
        "hydrogen": _metric("hydrogen", 300.0, 300.0),
        "cng": _metric("cng", 250.0, 250.0),
        "biodiesel": _metric("biodiesel", 200.0, 200.0),
    }
    verdict = calculate_verdict(pathways, fleet_lifecycle_years=12)
    assert verdict.winner_pathway == "bev"
    assert verdict.payback_years == 0.0


def test_winner_with_payback_beyond_fleet_lifecycle_reports_none_and_discloses_premium():
    # DISCLOSED CHANGE (verdict-honesty fix): locks in the regression caught
    # against the live NB/CNG scenario -- a pathway can win on blended
    # cost/carbon utility (carbon-weighted) while (a) its computed
    # incremental-capex payback exceeds the fleet's own holding horizon, and
    # (b) its lifetime tco_total is HIGHER than diesel's. Before this fix,
    # payback_years reported a number that implied recovery within the
    # asset's life even though the payback period (60 yrs here) blew past
    # fleet_lifecycle_years (12), and summary_text never disclosed that the
    # "winning" pathway cost more than diesel over its lifecycle.
    pathways = {
        "diesel": _metric(
            "diesel", 100.0, 100.0, vehicle_capex=1000.0, fuel_opex=100.0, maintenance_opex=100.0
        ),
        "cng": _metric(
            "cng", 110.0, 5.0, vehicle_capex=1500.0, fuel_opex=50.0, maintenance_opex=50.0
        ),
        "bev": _metric("bev", 300.0, 300.0),
        "hydrogen": _metric("hydrogen", 300.0, 300.0),
        "biodiesel": _metric("biodiesel", 250.0, 250.0),
    }
    verdict = calculate_verdict(pathways, fleet_lifecycle_years=12)

    assert verdict.winner_pathway == "cng"

    # incremental_capex=6000, annual_opex_savings=100 -> computed payback is
    # 60 years, which exceeds the 12-year fleet_lifecycle_years horizon, so
    # this must report None (not 60.0) -- a payback that doesn't fit inside
    # the asset's own service life is not a real payback.
    assert verdict.payback_years is None
    assert "no capital payback within fleet lifecycle" in verdict.summary_text

    # cng's tco_total (110.0) exceeds diesel's (100.0) by 10.0 -- the winner
    # costs more over the fleet lifecycle despite winning on blended
    # utility, and summary_text must disclose that explicitly rather than
    # let "wins" read as "cheaper."
    assert "$10 USD" in verdict.summary_text
    assert "higher than diesel" in verdict.summary_text
    assert "blended cost/carbon utility" in verdict.summary_text


def test_advanced_dashboard_cumulative_cost_axis_and_year_zero():
    lifecycle_years = 12
    inputs = FleetInputPayload(overrides=OverridesConfig(incentive_credits_usd=50000.0))
    pathways = calculate_all_pathways(inputs)
    dashboard = build_advanced_dashboard(pathways, lifecycle_years)
    bev_vector = next(item for item in dashboard.payback_vector if item.fuel_type == "bev")
    bev = pathways["bev"]
    expected_year_zero = _upfront_capital(bev, lifecycle_years) - bev.incentives_applied
    assert len(bev_vector.cumulative_cost_by_year) == lifecycle_years + 1
    assert bev_vector.cumulative_cost_by_year[0] == pytest.approx(expected_year_zero, abs=0.01)