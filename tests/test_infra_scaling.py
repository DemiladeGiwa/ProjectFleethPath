import pytest

from engine.models import FleetInputPayload, RegionConfig, FleetConfig, OverridesConfig, ClimateConfig
from engine.resolver import resolve_input_payload
from engine.tco_calculator import calculate_all_pathways, INFRA_LIFESPAN_YEARS, _BASELINES


def _build_payload(vehicle_count, annual_mileage_per_vehicle=12000, lifecycle_years=12, state_prov="CA"):
    payload = FleetInputPayload(
        region=RegionConfig(state_prov=state_prov),
        fleet=FleetConfig(
            vehicle_type="school_bus_typeC",
            vehicle_count=vehicle_count,
            annual_mileage_per_vehicle=annual_mileage_per_vehicle,
            lifecycle_years=lifecycle_years,
        ),
        overrides=OverridesConfig(),
        climate=ClimateConfig(cold_climate_flag=None),
    )
    return resolve_input_payload(payload)


def test_bev_charger_step_up_at_ratio_boundary():
    hw_cost = _BASELINES["bev"]["infrastructure"]["dcfc_50_hardware_usd"]["default"]
    mr_cost = _BASELINES["bev"]["infrastructure"]["dcfc_50_make_ready_usd"]["default"]
    cost_per_charger = hw_cost + mr_cost
    result_10 = calculate_all_pathways(_build_payload(vehicle_count=10))["bev"]
    result_11 = calculate_all_pathways(_build_payload(vehicle_count=11))["bev"]
    expected_infra_amortized_10 = (4 * cost_per_charger) / INFRA_LIFESPAN_YEARS
    expected_infra_amortized_11 = (5 * cost_per_charger) / INFRA_LIFESPAN_YEARS
    assert result_10.capex_infra_amortized == pytest.approx(expected_infra_amortized_10, abs=0.01)
    assert result_11.capex_infra_amortized == pytest.approx(expected_infra_amortized_11, abs=0.01)
    assert result_11.capex_infra_amortized > result_10.capex_infra_amortized


def test_hydrogen_station_tier_steps_up_past_300kg_day():
    result_101 = calculate_all_pathways(_build_payload(vehicle_count=101))["hydrogen"]
    result_102 = calculate_all_pathways(_build_payload(vehicle_count=102))["hydrogen"]
    small_tier_capex = _BASELINES["engine_constants"]["hydrogen_capex_small_liquid_usd"]["value"]
    medium_tier_capex = _BASELINES["engine_constants"]["hydrogen_capex_medium_delivery_usd"]["value"]
    assert result_101.capex_infra_amortized == pytest.approx(small_tier_capex / INFRA_LIFESPAN_YEARS, abs=0.01)
    assert result_102.capex_infra_amortized == pytest.approx(medium_tier_capex / INFRA_LIFESPAN_YEARS, abs=0.01)


def test_cng_station_type_steps_up_past_5_vehicles():
    time_fill_capex = _BASELINES["cng"]["infrastructure"]["time_fill_station_capex_usd"]["default"]
    fast_fill_capex = _BASELINES["cng"]["infrastructure"]["fast_fill_station_capex_usd"]["default"]
    result_5 = calculate_all_pathways(_build_payload(vehicle_count=5))["cng"]
    result_6 = calculate_all_pathways(_build_payload(vehicle_count=6))["cng"]
    assert result_5.capex_infra_amortized == pytest.approx(time_fill_capex / INFRA_LIFESPAN_YEARS, abs=0.01)
    assert result_6.capex_infra_amortized == pytest.approx(fast_fill_capex / INFRA_LIFESPAN_YEARS, abs=0.01)


def test_infrastructure_amortization_is_decoupled_from_fleet_lifecycle_years():
    result_10yr = calculate_all_pathways(_build_payload(vehicle_count=10, lifecycle_years=10))["bev"]
    result_15yr = calculate_all_pathways(_build_payload(vehicle_count=10, lifecycle_years=15))["bev"]
    assert result_10yr.capex_infra_amortized == pytest.approx(result_15yr.capex_infra_amortized, abs=0.001)
    assert result_10yr.capex_vehicle_amortized != pytest.approx(result_15yr.capex_vehicle_amortized, abs=0.001)
    assert result_10yr.capex_vehicle_amortized > result_15yr.capex_vehicle_amortized

