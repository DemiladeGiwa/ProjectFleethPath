import pytest

from api.main import calculate_fleet_pathways
from engine.models import FleetInputPayload, OverridesConfig, RegionConfig
from engine.tco_calculator import calculate_pathway_tco


def test_zero_and_positive_price_overrides_are_used():
    baseline = FleetInputPayload()
    zero_price = FleetInputPayload(overrides=OverridesConfig(diesel_price_gal=0.0))
    high_price = FleetInputPayload(overrides=OverridesConfig(diesel_price_gal=20.0))

    baseline_result = calculate_pathway_tco("diesel", baseline)
    zero_result = calculate_pathway_tco("diesel", zero_price)
    high_result = calculate_pathway_tco("diesel", high_price)

    assert zero_result.opex_fuel == 0.0
    assert high_result.opex_fuel > baseline_result.opex_fuel


def test_electricity_override_changes_bev_cost_and_can_change_winner():
    # DISCLOSED CHANGE (grid-factor sourcing fix, side effect): the default
    # region (CA -> CAMX) previously won this scenario for bev due to
    # CAMX's uncorrected placeholder grid factor (400.0 lb/MWh, vs. the
    # real EPA eGRID2023 Rev 2 figure of 430.0). With CAMX corrected, cng
    # already wins the CA baseline, leaving no bev-winning state for the
    # override to flip away from. QC is used instead: its corrected grid
    # factor (2.8 lb/MWh, effectively zero-carbon hydro) plus its wired
    # PETS incentive reliably produce a bev-winning baseline, so the
    # override's winner-flip effect remains meaningfully testable.
    baseline = calculate_fleet_pathways(FleetInputPayload(region=RegionConfig(state_prov="QC")))
    adjusted = calculate_fleet_pathways(
        FleetInputPayload(
            region=RegionConfig(state_prov="QC"),
            overrides=OverridesConfig(electricity_rate_kwh=5.0)
        )
    )
    baseline_bev = next(path for path in baseline.pathways if path.fuel_type == "bev")
    adjusted_bev = next(path for path in adjusted.pathways if path.fuel_type == "bev")
    assert adjusted_bev.opex_fuel > baseline_bev.opex_fuel
    assert baseline.verdict.winner_pathway == "bev"
    assert adjusted.verdict.winner_pathway != baseline.verdict.winner_pathway


def test_incentive_override_reduces_non_diesel_pathway_cost():
    baseline = calculate_pathway_tco("bev", FleetInputPayload())
    adjusted = calculate_pathway_tco(
        "bev", FleetInputPayload(overrides=OverridesConfig(incentive_credits_usd=50000.0))
    )
    assert adjusted.incentives_applied == pytest.approx(50000.0)
    assert adjusted.tco_total == pytest.approx(baseline.tco_total - 50000.0, abs=0.01)


def test_incentive_override_does_not_reduce_diesel_baseline():
    result = calculate_pathway_tco(
        "diesel", FleetInputPayload(overrides=OverridesConfig(incentive_credits_usd=50000.0))
    )
    assert result.incentives_applied == 0.0

