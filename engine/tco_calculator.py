import json
import math
from pathlib import Path
from typing import Any, Dict

from .models import FleetInputPayload, PathwayOutputMetrics
from .emissions_calculator import (
    get_bev_effective_kwh_per_mile,
    get_hydrogen_effective_kg_per_mile,
    UnknownRegionError,
)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_json(filename: str) -> Dict[str, Any]:
    return json.loads((_DATA_DIR / filename).read_text(encoding="utf-8"))


_BASELINES: Dict[str, Any] = _load_json("afleet_baselines.json")
_CROSSWALK: Dict[str, Any] = _load_json("state_crosswalk.json")
_CA_REGIONAL_PRICING: Dict[str, Any] = _BASELINES.get("canadian_regional_pricing", {})
_FX_RATES: Dict[str, Any] = _load_json("fx_rates.json")

_ENGINE_CONSTANTS = _BASELINES["engine_constants"]
INFRA_LIFESPAN_YEARS: int = int(_ENGINE_CONSTANTS["infra_lifespan_years"]["value"])
BEV_CHARGER_RATIO: float = float(_ENGINE_CONSTANTS["bev_charger_ratio"]["value"])
H2_TIER_THRESHOLD_KG_DAY: float = float(_ENGINE_CONSTANTS["hydrogen_tier_threshold_kg_day"]["value"])
H2_CAPEX_SMALL_LIQUID: float = float(_ENGINE_CONSTANTS["hydrogen_capex_small_liquid_usd"]["value"])
H2_CAPEX_MEDIUM_DELIVERY: float = float(_ENGINE_CONSTANTS["hydrogen_capex_medium_delivery_usd"]["value"])
CNG_FLEET_THRESHOLD_FAST_FILL: int = int(_ENGINE_CONSTANTS["cng_fleet_threshold_fast_fill"]["value"])

assert INFRA_LIFESPAN_YEARS == 20, "CRITICAL: INFRA_LIFESPAN_YEARS mutated in afleet_baselines.json."

# DISCLOSED CHANGE (pricing-bug remediation, phase 2 of 2): every pathway now
# resolves fully to CAD for Canadian regions, closing the currency-mixing gap
# left open at the end of phase 1. Two citation tiers exist side by side and
# are labeled distinctly in the assumptions matrix (see assumptions_tracker.py
# tracked_fx_conversion):
#   - Native CAD: diesel/electricity pricing, sourced directly from NRCan /
#     Hydro-Quebec (canadian_regional_pricing in afleet_baselines.json).
#   - FX-converted: vehicle capex, infrastructure capex, maintenance CPM, and
#     CNG/hydrogen fuel price. No native Canadian benchmark was found for any
#     of these after a real search pass (see canadian_regional_pricing_gaps)
#     -- commercial bus/charger/station pricing is quote-based in both
#     countries and isn't published, and CUTA's fleet-cost statistics are
#     member-only. Converted via fx_rates.json, a dated Bank of Canada rate
#     refreshed offline by scripts/refresh_fx_snapshot.py -- this module
#     never calls that API itself.
# US regions are completely unaffected by any of this: currency stays "USD"
# and every value is read exactly as before.

def _resolve_region(state_prov: str) -> Dict[str, Any]:
    # DISCLOSED CHANGE (region-resolution consistency fix): previously
    # returned {} for an unrecognized code, silently defaulting every
    # downstream is_canadian check to False and applying USD pricing with
    # no indication anything was wrong. In the full pipeline this was
    # incidentally caught by bev's emissions calculation (which already
    # raises UnknownRegionError via get_subregion_for_state), but any
    # direct call to calculate_pathway_tco -- including several in this
    # test suite -- bypasses that check entirely. Now raises the same
    # UnknownRegionError emissions_calculator.py already uses, so both
    # lookup paths fail identically instead of one being silently lenient.
    state_code = state_prov.strip().upper()
    region_info = _CROSSWALK.get(state_code)
    if region_info is None:
        raise UnknownRegionError(
            f"No state_crosswalk.json entry for region code '{state_code}'."
        )
    return region_info


def _fx_rate_usd_to_cad() -> float:
    return float(_FX_RATES["usd_to_cad"]["value"])


def _cold_climate_maintenance_multiplier(pathway: str, cold_climate_flag: bool) -> float:
    if not cold_climate_flag:
        return 1.0
    if pathway == "biodiesel":
        return _BASELINES["biodiesel"]["climate_adjustment"]["cold_weather_maintenance_multiplier"]["default"]
    return 1.0


def _calc_bev_infrastructure(vehicle_count: int, is_canadian: bool) -> Dict[str, float]:
    bev = _BASELINES["bev"]["infrastructure"]
    chargers_required = math.ceil(vehicle_count / BEV_CHARGER_RATIO)

    from .assumptions_tracker import tracked_fx_conversion  # local import avoids load-order coupling

    if is_canadian:
        fx = _fx_rate_usd_to_cad()
        hw_cost = tracked_fx_conversion(bev["dcfc_50_hardware_usd"], fx)
        mr_cost = tracked_fx_conversion(bev["dcfc_50_make_ready_usd"], fx)
        comms_cost = tracked_fx_conversion(bev["annual_comms_usd"], fx)
    else:
        hw_cost = bev["dcfc_50_hardware_usd"]["default"]
        mr_cost = bev["dcfc_50_make_ready_usd"]["default"]
        comms_cost = bev["annual_comms_usd"]["default"]

    cost_per_charger_unit = hw_cost + mr_cost
    total_infra_capex = chargers_required * cost_per_charger_unit

    # Percentages are dimensionless -- no FX conversion applies to these.
    maint_pct = bev["annual_maintenance_pct"]["default"]
    warranty_pct = bev["warranty_pct_lifetime"]["default"]

    annual_maint_cost = chargers_required * hw_cost * maint_pct
    annual_comms_total = chargers_required * comms_cost
    lifetime_warranty_cost = chargers_required * hw_cost * warranty_pct
    annual_warranty_amortized = lifetime_warranty_cost / INFRA_LIFESPAN_YEARS
    annual_om_total = annual_maint_cost + annual_comms_total + annual_warranty_amortized

    return {
        "chargers_required": chargers_required,
        "total_infra_capex": total_infra_capex,
        "annual_om_total": annual_om_total,
    }


def _calc_hydrogen_infrastructure(
    vehicle_count: int, annual_mileage_per_vehicle: float, is_canadian: bool
) -> Dict[str, Any]:
    h2 = _BASELINES["hydrogen"]
    kg_per_mile = h2["fuel_economy"]["bus_kg_per_mile"]["default"]

    daily_miles_per_vehicle = annual_mileage_per_vehicle / 365.0
    daily_fleet_demand_kg_h2 = vehicle_count * daily_miles_per_vehicle * kg_per_mile

    from .assumptions_tracker import tracked_fx_conversion  # local import avoids load-order coupling

    if daily_fleet_demand_kg_h2 <= H2_TIER_THRESHOLD_KG_DAY:
        tier = "small_liquid_delivery"
        usd_capex = H2_CAPEX_SMALL_LIQUID
        entry = h2["infrastructure"]["small_liquid_delivery_capex_usd"]
    else:
        tier = "medium_delivery"
        usd_capex = H2_CAPEX_MEDIUM_DELIVERY
        entry = h2["infrastructure"]["medium_delivery_capex_usd"]

    if is_canadian:
        total_infra_capex = tracked_fx_conversion(entry, _fx_rate_usd_to_cad())
    else:
        total_infra_capex = usd_capex

    return {
        "daily_fleet_demand_kg_h2": daily_fleet_demand_kg_h2,
        "station_tier": tier,
        "total_infra_capex": total_infra_capex,
    }


def _calc_cng_infrastructure(vehicle_count: int, is_canadian: bool) -> Dict[str, Any]:
    cng = _BASELINES["cng"]["infrastructure"]
    from .assumptions_tracker import tracked_fx_conversion  # local import avoids load-order coupling

    if vehicle_count <= CNG_FLEET_THRESHOLD_FAST_FILL:
        station_type = "time_fill"
        entry = cng["time_fill_station_capex_usd"]
    else:
        station_type = "fast_fill"
        entry = cng["fast_fill_station_capex_usd"]

    if is_canadian:
        total_infra_capex = tracked_fx_conversion(entry, _fx_rate_usd_to_cad())
    else:
        total_infra_capex = entry["default"]

    return {"station_type": station_type, "total_infra_capex": total_infra_capex}


def _amortize_vehicle_capex(capex_vehicle_total: float, fleet_lifecycle_years: int) -> float:
    return capex_vehicle_total / fleet_lifecycle_years


def _amortize_infra_capex(total_infra_capex: float) -> float:
    return total_infra_capex / INFRA_LIFESPAN_YEARS


def _calc_diesel_pathway(inputs: FleetInputPayload) -> Dict[str, Any]:
    diesel = _BASELINES["diesel"]
    fleet, overrides = inputs.fleet, inputs.overrides

    from .assumptions_tracker import tracked_choice, tracked_fx_conversion  # local import avoids load-order coupling

    region_info = _resolve_region(inputs.region.state_prov)
    province = region_info.get("code", "")
    is_canadian = region_info.get("country") == "CA" and province in _CA_REGIONAL_PRICING

    if is_canadian:
        fx = _fx_rate_usd_to_cad()
        capex_vehicle_total = tracked_fx_conversion(diesel["capex"]["vehicle_bus_usd"], fx) * fleet.vehicle_count
        ca_price_entry = _CA_REGIONAL_PRICING[province]["diesel"]
        price_per_gal = tracked_choice(overrides.diesel_price_gal, ca_price_entry, value_key="default_price_per_gal_cad")
        maint_cpm = tracked_fx_conversion(diesel["maintenance"]["cost_per_mile_usd"], fx)
        currency = "CAD"
    else:
        capex_vehicle_total = diesel["capex"]["vehicle_bus_usd"]["default"] * fleet.vehicle_count
        price_per_gal = tracked_choice(overrides.diesel_price_gal, diesel["fuel_price"]["default_price_gal"])
        maint_cpm = diesel["maintenance"]["cost_per_mile_usd"]["default"]
        currency = "USD"

    mpg = diesel["fuel_economy"]["bus_mpg"]["default"]
    total_miles = fleet.vehicle_count * fleet.annual_mileage_per_vehicle
    gallons_consumed = total_miles / mpg
    opex_fuel = gallons_consumed * price_per_gal

    multiplier = _cold_climate_maintenance_multiplier("diesel", inputs.climate.cold_climate_flag)
    opex_maintenance = total_miles * maint_cpm * multiplier

    return {
        "capex_vehicle_total": capex_vehicle_total,
        "total_infra_capex": 0.0,
        "opex_fuel": opex_fuel,
        "opex_maintenance": opex_maintenance,
        "currency": currency,
    }


def _calc_biodiesel_pathway(inputs: FleetInputPayload) -> Dict[str, Any]:
    biodiesel = _BASELINES["biodiesel"]
    fleet, overrides = inputs.fleet, inputs.overrides

    from .assumptions_tracker import tracked_choice, tracked_fx_conversion  # local import avoids load-order coupling

    region_info = _resolve_region(inputs.region.state_prov)
    province = region_info.get("code", "")
    is_canadian = region_info.get("country") == "CA" and province in _CA_REGIONAL_PRICING

    if is_canadian:
        fx = _fx_rate_usd_to_cad()
        capex_vehicle_total = tracked_fx_conversion(biodiesel["capex"]["vehicle_bus_usd"], fx) * fleet.vehicle_count
        # Biodiesel shares the diesel price baseline, same as before this change.
        ca_price_entry = _CA_REGIONAL_PRICING[province]["diesel"]
        price_per_gal = tracked_choice(overrides.diesel_price_gal, ca_price_entry, value_key="default_price_per_gal_cad")
        maint_cpm = tracked_fx_conversion(biodiesel["maintenance"]["cost_per_mile_usd"], fx)
        currency = "CAD"
    else:
        capex_vehicle_total = biodiesel["capex"]["vehicle_bus_usd"]["default"] * fleet.vehicle_count
        price_per_gal = tracked_choice(overrides.diesel_price_gal, biodiesel["fuel_price"]["default_price_gal"])
        maint_cpm = biodiesel["maintenance"]["cost_per_mile_usd"]["default"]
        currency = "USD"

    mpg = biodiesel["fuel_economy"]["bus_mpg"]["default"]
    total_miles = fleet.vehicle_count * fleet.annual_mileage_per_vehicle
    gallons_consumed = total_miles / mpg
    opex_fuel = gallons_consumed * price_per_gal

    multiplier = _cold_climate_maintenance_multiplier("biodiesel", inputs.climate.cold_climate_flag)
    opex_maintenance = total_miles * maint_cpm * multiplier

    return {
        "capex_vehicle_total": capex_vehicle_total,
        "total_infra_capex": 0.0,
        "opex_fuel": opex_fuel,
        "opex_maintenance": opex_maintenance,
        "currency": currency,
    }


def _calc_bev_pathway(inputs: FleetInputPayload) -> Dict[str, Any]:
    bev = _BASELINES["bev"]
    fleet, overrides = inputs.fleet, inputs.overrides

    from .assumptions_tracker import tracked_choice, tracked_fx_conversion  # local import avoids load-order coupling

    region_info = _resolve_region(inputs.region.state_prov)
    province = region_info.get("code", "")
    is_canadian = region_info.get("country") == "CA" and province in _CA_REGIONAL_PRICING

    infra = _calc_bev_infrastructure(fleet.vehicle_count, is_canadian)

    base_kwh_per_mile = bev["fuel_economy"]["transit_bus_kwh_per_mile"]["default"]
    kwh_per_mile_effective = get_bev_effective_kwh_per_mile(
        base_kwh_per_mile=base_kwh_per_mile,
        cold_climate_flag=inputs.climate.cold_climate_flag,
    )

    if is_canadian:
        fx = _fx_rate_usd_to_cad()
        capex_vehicle_total = tracked_fx_conversion(bev["capex"]["vehicle_bus_usd"], fx) * fleet.vehicle_count
        ca_price_entry = _CA_REGIONAL_PRICING[province]["electricity"]
        electricity_rate = tracked_choice(overrides.electricity_rate_kwh, ca_price_entry, value_key="default_price_per_kwh_cad")
        maint_cpm = tracked_fx_conversion(bev["maintenance"]["cost_per_mile_usd"], fx)
        currency = "CAD"
    else:
        capex_vehicle_total = bev["capex"]["vehicle_bus_usd"]["default"] * fleet.vehicle_count
        electricity_rate = tracked_choice(overrides.electricity_rate_kwh, bev["fuel_price"]["default_electricity_rate_usd_kwh"])
        maint_cpm = bev["maintenance"]["cost_per_mile_usd"]["default"]
        currency = "USD"

    # DISCLOSED CHANGE (BEV incentive gap, PRD §6 priority 2): Quebec's PETS
    # program (Programme d'electrification du transport scolaire) is a real,
    # cited purchase rebate -- applied to vehicle capex before amortization,
    # same mechanism as the hydrogen Clean Hydrogen ITC's capex-side
    # reduction. Gated strictly to province == "QC", not a general CA check
    # -- no equivalent was found for any other province after a real search
    # pass (see canadian_regional_pricing_gaps.bev_incentive_outside_quebec).
    qc_pets_incentive_cad = 0.0
    if province == "QC":
        pets_entry = bev["incentives"]["qc_pets_purchase_rebate_cad_per_bus"]
        per_bus_rebate = pets_entry["value"]
        qc_pets_incentive_cad = per_bus_rebate * fleet.vehicle_count
        capex_vehicle_total = capex_vehicle_total - qc_pets_incentive_cad

    total_miles = fleet.vehicle_count * fleet.annual_mileage_per_vehicle
    kwh_consumed = total_miles * kwh_per_mile_effective
    opex_fuel = kwh_consumed * electricity_rate

    multiplier = _cold_climate_maintenance_multiplier("bev", inputs.climate.cold_climate_flag)
    fleet_maintenance_cost = total_miles * maint_cpm * multiplier
    opex_maintenance = fleet_maintenance_cost + infra["annual_om_total"]

    return {
        "capex_vehicle_total": capex_vehicle_total,
        "total_infra_capex": infra["total_infra_capex"],
        "qc_pets_incentive_cad": qc_pets_incentive_cad,
        "opex_fuel": opex_fuel,
        "opex_maintenance": opex_maintenance,
        "currency": currency,
    }


def _calc_hydrogen_pathway(inputs: FleetInputPayload) -> Dict[str, Any]:
    h2 = _BASELINES["hydrogen"]
    fleet = inputs.fleet

    region_info = _resolve_region(inputs.region.state_prov)
    is_canadian = region_info.get("country") == "CA"

    from .assumptions_tracker import tracked_fx_conversion  # local import avoids load-order coupling

    infra = _calc_hydrogen_infrastructure(fleet.vehicle_count, fleet.annual_mileage_per_vehicle, is_canadian)

    if is_canadian:
        fx = _fx_rate_usd_to_cad()
        capex_vehicle_total = tracked_fx_conversion(h2["capex"]["vehicle_bus_usd"], fx) * fleet.vehicle_count
    else:
        capex_vehicle_total = h2["capex"]["vehicle_bus_usd"]["default"] * fleet.vehicle_count

    station_capex = infra["total_infra_capex"]  # already FX-converted above if is_canadian
    h2_itc_incentive_usd = 0.0
    if is_canadian:
        itc_rate = h2["infrastructure"]["ca_federal_clean_hydrogen_itc_rate"]["default"]
        h2_itc_incentive_usd = station_capex * itc_rate  # in CAD now, name kept for API-shape continuity
        station_capex = station_capex - h2_itc_incentive_usd

    base_kg_per_mile = h2["fuel_economy"]["bus_kg_per_mile"]["default"]
    kg_per_mile_effective = get_hydrogen_effective_kg_per_mile(
        base_kg_per_mile=base_kg_per_mile,
        cold_climate_flag=inputs.climate.cold_climate_flag,
    )

    tier_key = (
        "small_liquid_delivery_capex_usd"
        if infra["station_tier"] == "small_liquid_delivery"
        else "medium_delivery_capex_usd"
    )
    price_entry = h2["infrastructure"][tier_key]["price_per_kg"]
    if is_canadian:
        price_per_kg = tracked_fx_conversion(price_entry, _fx_rate_usd_to_cad())
        maint_cpm = tracked_fx_conversion(h2["maintenance"]["cost_per_mile_usd"], _fx_rate_usd_to_cad())
        currency = "CAD"
    else:
        price_per_kg = price_entry["default"]
        maint_cpm = h2["maintenance"]["cost_per_mile_usd"]["default"]
        currency = "USD"

    total_miles = fleet.vehicle_count * fleet.annual_mileage_per_vehicle
    kg_consumed = total_miles * kg_per_mile_effective
    opex_fuel = kg_consumed * price_per_kg

    multiplier = _cold_climate_maintenance_multiplier("hydrogen", inputs.climate.cold_climate_flag)
    opex_maintenance = total_miles * maint_cpm * multiplier

    return {
        "capex_vehicle_total": capex_vehicle_total,
        "total_infra_capex": station_capex,
        "h2_itc_incentive_usd": h2_itc_incentive_usd,
        "opex_fuel": opex_fuel,
        "opex_maintenance": opex_maintenance,
        "currency": currency,
    }


def _calc_cng_pathway(inputs: FleetInputPayload) -> Dict[str, Any]:
    cng = _BASELINES["cng"]
    fleet = inputs.fleet

    region_info = _resolve_region(inputs.region.state_prov)
    is_canadian = region_info.get("country") == "CA"

    from .assumptions_tracker import tracked_fx_conversion  # local import avoids load-order coupling

    infra = _calc_cng_infrastructure(fleet.vehicle_count, is_canadian)

    dge_per_mile = 1.0 / cng["fuel_economy"]["bus_dge_per_mile"]["default"]

    if is_canadian:
        fx = _fx_rate_usd_to_cad()
        capex_vehicle_total = tracked_fx_conversion(cng["capex"]["vehicle_bus_usd"], fx) * fleet.vehicle_count
        price_per_dge = tracked_fx_conversion(cng["fuel_price"]["default_price_dge"], fx)
        maint_cpm = tracked_fx_conversion(cng["maintenance"]["cost_per_mile_usd"], fx)
        currency = "CAD"
    else:
        capex_vehicle_total = cng["capex"]["vehicle_bus_usd"]["default"] * fleet.vehicle_count
        price_per_dge = cng["fuel_price"]["default_price_dge"]["default"]
        maint_cpm = cng["maintenance"]["cost_per_mile_usd"]["default"]
        currency = "USD"

    total_miles = fleet.vehicle_count * fleet.annual_mileage_per_vehicle
    dge_consumed = total_miles * dge_per_mile
    opex_fuel = dge_consumed * price_per_dge

    multiplier = _cold_climate_maintenance_multiplier("cng", inputs.climate.cold_climate_flag)
    opex_maintenance = total_miles * maint_cpm * multiplier

    return {
        "capex_vehicle_total": capex_vehicle_total,
        "total_infra_capex": infra["total_infra_capex"],
        "opex_fuel": opex_fuel,
        "opex_maintenance": opex_maintenance,
        "currency": currency,
    }


_PATHWAY_CALCULATORS = {
    "diesel": _calc_diesel_pathway,
    "biodiesel": _calc_biodiesel_pathway,
    "bev": _calc_bev_pathway,
    "hydrogen": _calc_hydrogen_pathway,
    "cng": _calc_cng_pathway,
}


def calculate_pathway_tco(fuel_type: str, inputs: FleetInputPayload) -> PathwayOutputMetrics:
    if fuel_type not in _PATHWAY_CALCULATORS:
        raise ValueError(f"Unknown fuel_type: {fuel_type}")

    raw = _PATHWAY_CALCULATORS[fuel_type](inputs)

    capex_vehicle_amortized = _amortize_vehicle_capex(raw["capex_vehicle_total"], inputs.fleet.lifecycle_years)
    capex_infra_amortized = _amortize_infra_capex(raw["total_infra_capex"])
    user_incentives = inputs.overrides.incentive_credits_usd or 0.0
    if fuel_type == "diesel":
        incentives_applied = 0.0
    else:
        h2_itc = raw.get("h2_itc_incentive_usd", 0.0)
        qc_pets = raw.get("qc_pets_incentive_cad", 0.0)
        incentives_applied = user_incentives + h2_itc + qc_pets

    tco_total = (
        capex_vehicle_amortized
        + capex_infra_amortized
        + raw["opex_fuel"]
        + raw["opex_maintenance"]
        - user_incentives
    )

    return PathwayOutputMetrics(
        fuel_type=fuel_type,
        currency=raw["currency"],
        tco_total=round(tco_total, 2),
        capex_vehicle_amortized=round(capex_vehicle_amortized, 2),
        capex_infra_amortized=round(capex_infra_amortized, 2),
        opex_fuel=round(raw["opex_fuel"], 2),
        opex_maintenance=round(raw["opex_maintenance"], 2),
        incentives_applied=round(incentives_applied, 2),
        lifecycle_co2e_tons=0.0,
        cold_climate_adjustment_applied=bool(inputs.climate.cold_climate_flag),
    )


def calculate_all_pathways(inputs: FleetInputPayload) -> Dict[str, PathwayOutputMetrics]:
    return {ft: calculate_pathway_tco(ft, inputs) for ft in _PATHWAY_CALCULATORS}
