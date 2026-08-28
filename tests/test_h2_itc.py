import pytest

from engine.models import FleetInputPayload, RegionConfig, FleetConfig, OverridesConfig, ClimateConfig
from engine.tco_calculator import calculate_pathway_tco, _BASELINES, _FX_RATES


def _build_payload(state_prov: str, vehicle_count: int = 10, annual_mileage_per_vehicle: float = 12000.0):
    return FleetInputPayload(
        region=RegionConfig(state_prov=state_prov),
        fleet=FleetConfig(
            vehicle_type="school_bus_typeC",
            vehicle_count=vehicle_count,
            annual_mileage_per_vehicle=annual_mileage_per_vehicle,
            lifecycle_years=12,
        ),
        overrides=OverridesConfig(),
        climate=ClimateConfig(cold_climate_flag=False),
    )


def test_canadian_federal_h2_itc_applied_in_ca_and_zero_in_us():
    ca_result = calculate_pathway_tco("hydrogen", _build_payload("QC"))
    us_result = calculate_pathway_tco("hydrogen", _build_payload("IN"))

    station_capex_usd = _BASELINES["engine_constants"]["hydrogen_capex_small_liquid_usd"]["value"]

    # DISCLOSED CHANGE (pricing-bug remediation, phase 2): CA station capex is
    # FX-converted to CAD (data/fx_rates.json, refreshed daily and offline by
    # scripts/refresh_fx_snapshot.py) before the 40% ITC is applied. Expected
    # values here are derived from the live-loaded rate the code itself uses,
    # not a hardcoded number -- a hardcoded rate would make this test start
    # failing every time the FX snapshot is legitimately refreshed.
    fx_rate = _FX_RATES["usd_to_cad"]["value"]
    station_capex_cad = station_capex_usd * fx_rate
    expected_ca_incentive = station_capex_cad * 0.40

    # CA province receives 40% Clean Hydrogen ITC on the CAD-converted station capex
    assert ca_result.incentives_applied == pytest.approx(expected_ca_incentive)
    assert ca_result.capex_infra_amortized == pytest.approx((station_capex_cad * 0.60) / 20)
    assert ca_result.currency == "CAD"

    # US state receives zero ITC and uses the raw USD baseline, unconverted
    assert us_result.incentives_applied == 0.0
    assert us_result.capex_infra_amortized == pytest.approx(station_capex_usd / 20)
    assert us_result.currency == "USD"

    # Vehicle capex is untouched by the station ITC specifically -- but it IS
    # FX-converted for the CA region, same as every other capex/maintenance
    # line item in phase 2, so CA and US vehicle capex are now proportional
    # by the FX rate rather than equal (they were equal pre-phase-2, when CA
    # hydrogen silently used the raw USD vehicle price with no conversion at
    # all -- that was the bug, not a property worth preserving).
    assert ca_result.capex_vehicle_amortized == pytest.approx(
        us_result.capex_vehicle_amortized * fx_rate
    )