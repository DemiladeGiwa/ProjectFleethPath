#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

mkdir -p data engine api tests

touch -a engine/__init__.py api/__init__.py tests/__init__.py

cat > data/afleet_baselines.json << 'EOF'
{
  "engine_constants": {
    "infra_lifespan_years": {
      "value": 20,
      "unit": "years",
      "param_id": "INFRA_LIFESPAN_YEARS",
      "note": "HARDCODED - must never read fleet.lifecycle_years"
    },
    "bev_charger_ratio": {
      "value": 2.5,
      "unit": "buses per charger",
      "param_id": "REF_INFRA_BEV_RATIO"
    },
    "hydrogen_tier_threshold_kg_day": {
      "value": 300.0,
      "unit": "kg H2/day",
      "param_id": "H2_TIER_THRESHOLD_KG_DAY",
      "note": "Boundary is strict greater-than; exactly 300 selects small tier"
    },
    "hydrogen_capex_small_liquid_usd": {
      "value": 2500000,
      "param_id": "H2_CAPEX_SMALL_LIQUID"
    },
    "hydrogen_capex_medium_delivery_usd": {
      "value": 4500000,
      "param_id": "H2_CAPEX_MEDIUM_DELIVERY"
    },
    "cng_fleet_threshold_fast_fill": {
      "value": 5,
      "unit": "vehicles",
      "param_id": "CNG_FLEET_THRESHOLD_FAST_FILL",
      "note": "<=5 vehicles selects time-fill; >5 selects fast-fill"
    }
  },
  "diesel": {
    "capex": {
      "vehicle_bus_usd": {
        "default": 140000,
        "range_low": 120000,
        "range_high": 160000,
        "unit": "USD/vehicle",
        "param_id": "REF_CAPEX_VEH_DIESEL_BUS",
        "source": "Argonne ANL AFLEET 2023"
      }
    },
    "maintenance": {
      "cost_per_mile_usd": {
        "default": 0.225,
        "range_low": 0.20,
        "range_high": 0.25,
        "unit": "USD/mile",
        "param_id": "REF_MAINT_CPM_DIESEL",
        "source": "Argonne ANL AFLEET 2023"
      }
    },
    "fuel_economy": {
      "bus_mpg": {
        "default": 6.0,
        "range_low": 5.0,
        "range_high": 7.0,
        "unit": "MPG",
        "param_id": "REF_FE_DIESEL_BUS_MPG",
        "source": "Argonne ANL AFLEET 2023 / GREET"
      }
    },
    "emissions": {
      "carbon_intensity_wtw": {
        "default": 22.4,
        "unit": "lb CO2e/gallon (WTW)",
        "param_id": "REF_CI_DIESEL_GHG",
        "source": "Argonne ANL GREET 2023 (via AFLEET)"
      }
    },
    "fuel_price": {
      "default_price_gal": {
        "default": 3.85,
        "unit": "USD/gal",
        "param_id": "REF_PRICE_DIESEL_GAL",
        "source": "U.S. EIA On-Highway Diesel Fuel Update"
      }
    }
  },
  "bev": {
    "capex": {
      "vehicle_bus_usd": {
        "default": 425000,
        "range_low": 350000,
        "range_high": 500000,
        "unit": "USD/vehicle",
        "param_id": "REF_CAPEX_VEH_BEV_BUS",
        "source": "Argonne ANL AFLEET 2023"
      }
    },
    "maintenance": {
      "cost_per_mile_usd": {
        "default": 0.16,
        "range_low": 0.14,
        "range_high": 0.18,
        "unit": "USD/mile",
        "param_id": "REF_MAINT_CPM_BEV",
        "source": "Argonne ANL AFLEET 2023"
      }
    },
    "fuel_economy": {
      "transit_bus_kwh_per_mile": {
        "default": 2.0,
        "range_low": 1.7,
        "range_high": 2.6,
        "unit": "kWh/mile",
        "param_id": "REF_FE_BEV_BUS_KWH",
        "source": "Argonne ANL AFLEET 2023 / GREET"
      },
      "school_bus_kwh_per_mile": {
        "default": 1.7,
        "unit": "kWh/mile",
        "param_id": "REF_FE_BEV_SCHOOLBUS_KWH",
        "source": "Argonne ANL AFLEET 2023"
      }
    },
    "infrastructure": {
      "charger_ratio_buses_per_charger": {
        "default": 2.5,
        "unit": "buses/charger",
        "param_id": "REF_INFRA_BEV_RATIO"
      },
      "dcfc_50_hardware_usd": {
        "default": 27900.00,
        "unit": "USD/charger",
        "param_id": "REF_INFRA_BEV_DCFC_50_HW",
        "source": "Argonne ANL AFLEET 2023"
      },
      "dcfc_50_make_ready_usd": {
        "default": 62700.00,
        "unit": "USD/charger",
        "param_id": "REF_INFRA_BEV_DCFC_50_MR",
        "source": "Argonne ANL AFLEET 2023"
      },
      "dcfc_150_hardware_usd": {
        "default": 87800.00,
        "unit": "USD/charger",
        "param_id": "REF_INFRA_BEV_DCFC_150_HW",
        "source": "Argonne ANL AFLEET 2023"
      },
      "dcfc_150_make_ready_usd": {
        "default": 91000.00,
        "unit": "USD/charger",
        "param_id": "REF_INFRA_BEV_DCFC_150_MR",
        "source": "Argonne ANL AFLEET 2023"
      },
      "annual_maintenance_pct": {
        "default": 0.005,
        "unit": "% of hardware cost/year",
        "param_id": "REF_INFRA_BEV_MAINT_PCT",
        "source": "Argonne ANL AFLEET 2023"
      },
      "warranty_pct_lifetime": {
        "default": 0.070,
        "unit": "% of hardware cost (one-time, lifetime)",
        "param_id": "REF_INFRA_BEV_WARRANT_PCT",
        "source": "Argonne ANL AFLEET 2023"
      },
      "annual_comms_usd": {
        "default": 255.00,
        "unit": "USD/charger/year",
        "param_id": "REF_INFRA_BEV_COMMS",
        "source": "Argonne ANL AFLEET 2023"
      }
    },
    "fuel_price": {
      "default_electricity_rate_usd_kwh": {
        "default": 0.135,
        "unit": "USD/kWh",
        "param_id": "REF_PRICE_ELEC_KWH",
        "source": "U.S. EIA Electricity Monthly (Commercial Sector)"
      }
    },
    "climate_adjustment": {
      "cold_climate_efficiency_penalty_pct": {
        "range_low": 0.15,
        "range_high": 0.30,
        "unit": "% increase in baseline consumption",
        "note": "Applied when climate.cold_climate_flag == true (cabin resistive heating + thermal management draw)"
      }
    }
  },
  "hydrogen": {
    "capex": {
      "vehicle_bus_usd": {
        "default": 975000,
        "range_low": 750000,
        "range_high": 1200000,
        "unit": "USD/vehicle",
        "param_id": "REF_CAPEX_VEH_H2FC_BUS",
        "source": "Argonne ANL AFLEET 2023 / NREL ATB 2024"
      }
    },
    "maintenance": {
      "cost_per_mile_usd": {
        "default": 0.18,
        "range_low": 0.16,
        "range_high": 0.20,
        "unit": "USD/mile",
        "param_id": "REF_MAINT_CPM_H2FC",
        "source": "Argonne ANL AFLEET 2023"
      }
    },
    "fuel_economy": {
      "bus_kg_per_mile": {
        "default": 0.09,
        "range_low": 0.07,
        "range_high": 0.12,
        "unit": "kg H2/mile",
        "param_id": "REF_FE_H2FC_BUS_KG",
        "source": "NREL ATB 2024 / Argonne GREET"
      }
    },
    "fuel_price": {
      "current_low_usd_per_kg": {
        "default": 9.10,
        "range_low": 6.20,
        "range_high": 12.00,
        "unit": "USD/kg H2",
        "param_id": "REF_PRICE_H2_CURRENT_LOW",
        "source": "NREL ATB 2024 (H2A-Lite, SMR pathway)",
        "note": "Reference/sensitivity value; production calc uses tier-specific infrastructure.*.price_per_kg"
      },
      "current_high_usd_per_kg": {
        "default": 13.10,
        "range_low": 8.20,
        "range_high": 18.00,
        "unit": "USD/kg H2",
        "param_id": "REF_PRICE_H2_CURRENT_HIGH",
        "source": "NREL ATB 2024 (H2A-Lite / Electrolysis)",
        "note": "Reference/sensitivity value"
      },
      "future_target_usd_per_kg": {
        "default": 4.00,
        "unit": "USD/kg H2",
        "param_id": "REF_PRICE_H2_FUTURE_TARGET",
        "source": "NREL ATB 2024 / DOE H2 Program",
        "note": "Future scenario toggle - not used in current-state calculation"
      }
    },
    "infrastructure": {
      "tier_threshold_kg_per_day": {
        "default": 300.0,
        "unit": "kg H2/day",
        "param_id": "H2_TIER_THRESHOLD_KG_DAY"
      },
      "small_liquid_delivery_capex_usd": {
        "default": 2500000,
        "range_low": 1500000,
        "range_high": 3500000,
        "unit": "USD/station",
        "param_id": "REF_INFRA_H2_STATION_CAPEX",
        "source": "NREL H2A / DOE HFTO Multi-Year Plan",
        "note": "Selected when daily_fleet_demand_kg_h2 <= 300",
        "max_capacity_kg_day": 300.0,
        "price_per_kg": {
          "default": 14.50,
          "unit": "USD/kg H2",
          "param_id": "REF_PRICE_H2_KG_SMALL",
          "source": "NREL H2A Delivered Liquid Station Model"
        }
      },
      "medium_delivery_capex_usd": {
        "default": 4500000,
        "unit": "USD/station",
        "param_id": "H2_CAPEX_MEDIUM_DELIVERY",
        "source": "NREL H2A / DOE HFTO Multi-Year Plan",
        "note": "Selected when daily_fleet_demand_kg_h2 > 300",
        "max_capacity_kg_day": 1000.0,
        "price_per_kg": {
          "default": 12.00,
          "unit": "USD/kg H2",
          "param_id": "REF_PRICE_H2_KG_MED",
          "source": "NREL H2A Delivered Liquid Station Model"
        }
      },
      "delivery_dispensing_cost_usd_per_kg": {
        "default": 5.00,
        "range_low": 3.00,
        "range_high": 7.00,
        "unit": "USD/kg H2 (of total retail price)",
        "param_id": "REF_INFRA_H2_DISP_COST",
        "source": "NREL ATB 2024 (Bracci et al.)"
      }
    },
    "climate_adjustment": {
      "cold_start_efficiency_penalty": {
        "note": "Minor sub-zero efficiency scaling for cold-start stabilization; applied when climate.cold_climate_flag == true"
      }
    }
  },
  "cng": {
    "capex": {
      "vehicle_bus_usd": {
        "default": 160000,
        "range_low": 140000,
        "range_high": 180000,
        "unit": "USD/vehicle",
        "param_id": "REF_CAPEX_VEH_CNG_BUS",
        "source": "Argonne ANL AFLEET 2023"
      }
    },
    "maintenance": {
      "cost_per_mile_usd": {
        "default": 0.21,
        "range_low": 0.19,
        "range_high": 0.23,
        "unit": "USD/mile",
        "param_id": "REF_MAINT_CPM_CNG",
        "source": "Argonne ANL AFLEET 2023"
      }
    },
    "fuel_economy": {
      "bus_dge_per_mile": {
        "default": 5.5,
        "range_low": 4.5,
        "range_high": 6.0,
        "unit": "DGE/mile (MPGde)",
        "param_id": "REF_FE_CNG_BUS_DGE",
        "source": "Argonne ANL AFLEET 2023"
      }
    },
    "emissions": {
      "carbon_intensity_wtw": {
        "default": 13.7,
        "unit": "lb CO2e/DGE (WTW)",
        "param_id": "REF_CI_CNG_GHG",
        "source": "Argonne ANL GREET 2023"
      }
    },
    "fuel_price": {
      "default_price_dge": {
        "default": 3.30,
        "unit": "USD/DGE",
        "param_id": "REF_PRICE_CNG_DGE",
        "source": "DOE Clean Cities Alternative Fuel Price Report"
      }
    },
    "infrastructure": {
      "fleet_threshold_fast_fill_vehicles": {
        "default": 5,
        "unit": "vehicles",
        "param_id": "CNG_FLEET_THRESHOLD_FAST_FILL"
      },
      "time_fill_station_capex_usd": {
        "default": 175000,
        "range_low": 100000,
        "range_high": 250000,
        "unit": "USD/station",
        "param_id": "REF_INFRA_CNG_STATION_TIME",
        "source": "Argonne ANL AFLEET 2023 / Clean Cities",
        "note": "Preferred default for school fleets - overnight slow-fill; selected when fleet.vehicle_count <= 5"
      },
      "fast_fill_station_capex_usd": {
        "default": 600000,
        "range_low": 400000,
        "range_high": 800000,
        "unit": "USD/station",
        "param_id": "REF_INFRA_CNG_STATION_FAST",
        "source": "Argonne ANL AFLEET 2023 / Clean Cities",
        "note": "Selected when fleet.vehicle_count > 5"
      }
    }
  },
  "biodiesel": {
    "capex": {
      "vehicle_bus_usd": {
        "default": 140000,
        "range_low": 120000,
        "range_high": 160000,
        "unit": "USD/vehicle",
        "param_id": "REF_CAPEX_VEH_B20_BUS",
        "source": "Argonne ANL AFLEET 2023",
        "note": "Same drivetrain as diesel, no CapEx premium"
      }
    },
    "maintenance": {
      "cost_per_mile_usd": {
        "default": 0.225,
        "range_low": 0.20,
        "range_high": 0.25,
        "unit": "USD/mile",
        "param_id": "REF_MAINT_CPM_B20",
        "source": "Argonne ANL AFLEET 2023",
        "note": "Same as diesel baseline"
      }
    },
    "fuel_economy": {
      "bus_mpg": {
        "default": 5.9,
        "range_low": 4.9,
        "range_high": 6.9,
        "unit": "MPG",
        "param_id": "REF_FE_B20_BUS_MPG",
        "source": "Argonne ANL AFLEET 2023",
        "note": "~2% fuel-economy penalty vs. diesel"
      }
    },
    "emissions": {
      "carbon_intensity_wtw": {
        "default": 18.0,
        "unit": "lb CO2e/gallon (WTW)",
        "param_id": "REF_CI_B20_GHG",
        "source": "Argonne ANL GREET 2023",
        "note": "~20% reduction vs. diesel"
      }
    },
    "fuel_price": {
      "default_price_gal": {
        "default": 3.85,
        "unit": "USD/gal",
        "param_id": "REF_PRICE_DIESEL_GAL",
        "source": "U.S. EIA On-Highway Diesel Fuel Update",
        "note": "Uses diesel baseline; no B20 price premium/discount currently modeled"
      }
    },
    "climate_adjustment": {
      "cold_weather_maintenance_premium": {
        "note": "Triggers cold-weather maintenance premium for gelling risk / filtration overhead when climate.cold_climate_flag == true"
      }
    }
  }
}
EOF

cat > data/state_crosswalk.json << 'EOF'
{
  "CA": {"subregion": "CAMX", "cold_climate": false},
  "IN": {"subregion": "MROE", "cold_climate": true},
  "QC": {"subregion": "ECCC_QC", "cold_climate": false},
  "TX": {"subregion": "TRE", "cold_climate": false},
  "WA": {"subregion": "NWPP", "cold_climate": false}
}
EOF

cat > engine/models.py << 'EOF'
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class RegionConfig(BaseModel):
    state_prov: str = "CA"


class FleetConfig(BaseModel):
    vehicle_type: str = "school_bus_typeC"
    vehicle_count: int = 10
    annual_mileage_per_vehicle: float = 12000.0
    lifecycle_years: int = 12


class OverridesConfig(BaseModel):
    diesel_price_gal: Optional[float] = None
    electricity_rate_kwh: Optional[float] = None
    incentive_credits_usd: Optional[float] = None


class ClimateConfig(BaseModel):
    cold_climate_flag: Optional[bool] = None


class FleetInputPayload(BaseModel):
    region: RegionConfig = Field(default_factory=RegionConfig)
    fleet: FleetConfig = Field(default_factory=FleetConfig)
    overrides: OverridesConfig = Field(default_factory=OverridesConfig)
    climate: ClimateConfig = Field(default_factory=ClimateConfig)


class PathwayOutputMetrics(BaseModel):
    fuel_type: str
    tco_total_usd: float
    capex_vehicle_amortized_usd: float
    capex_infra_amortized_usd: float
    opex_fuel_usd: float
    opex_maintenance_usd: float
    incentives_applied_usd: float
    lifecycle_co2e_tons: float
    cold_climate_adjustment_applied: bool


class VerdictConfig(BaseModel):
    winner_pathway: str
    summary_text: str
    payback_years: float
    emissions_reduction_pct: float


class EngineOutputPayload(BaseModel):
    verdict: VerdictConfig
    pathways: List[PathwayOutputMetrics]
EOF

cat > engine/emissions_calculator.py << 'EOF'
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

from .models import FleetInputPayload

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_GRID_FACTORS_PATH = _DATA_DIR / "grid_factors.json"
_CROSSWALK_PATH = _DATA_DIR / "state_crosswalk.json"


class UnknownRegionError(ValueError):
    pass


def _load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


_GRID_FACTORS = _load_json(_GRID_FACTORS_PATH)
_CROSSWALK = _load_json(_CROSSWALK_PATH)


def get_subregion_for_state(state_code: str) -> str:
    code = state_code.strip().upper()
    try:
        return _CROSSWALK[code]["subregion"]
    except KeyError as exc:
        raise UnknownRegionError(f"Unknown region code: {state_code}") from exc


def get_grid_factor_lb_per_mwh(state_code: str) -> float:
    subregion = get_subregion_for_state(state_code)
    return float(_GRID_FACTORS[subregion]["grid_factor_lb_per_mwh"])


def get_bev_effective_kwh_per_mile(base_kwh_per_mile: float, cold_climate_flag: bool) -> float:
    if cold_climate_flag:
        return base_kwh_per_mile * 1.25
    return base_kwh_per_mile


def get_hydrogen_effective_kg_per_mile(base_kg_per_mile: float, cold_climate_flag: bool) -> float:
    if cold_climate_flag:
        return base_kg_per_mile * 1.10
    return base_kg_per_mile


def calculate_all_pathway_emissions(inputs: FleetInputPayload) -> Dict[str, float]:
    fleet = inputs.fleet
    region_code = inputs.region.state_prov
    total_miles = fleet.vehicle_count * fleet.annual_mileage_per_vehicle

    diesel_grams = total_miles * 0.0001
    biodiesel_grams = diesel_grams * 0.8

    bev_factor = get_grid_factor_lb_per_mwh(region_code)
    bev_grams = total_miles * 0.0002 * (bev_factor / 1000.0)

    h2_factor = get_grid_factor_lb_per_mwh(region_code)
    hydrogen_grams = total_miles * 0.00015 * (h2_factor / 1000.0)

    cng_grams = total_miles * 0.00012

    return {
        "diesel": round(diesel_grams, 6),
        "biodiesel": round(biodiesel_grams, 6),
        "bev": round(bev_grams, 6),
        "hydrogen": round(hydrogen_grams, 6),
        "cng": round(cng_grams, 6),
    }
EOF

cat > engine/tco_calculator.py << 'EOF'
"""
FleetPath - TCO Calculation Engine
"""

import json
import math
from pathlib import Path
from typing import Any, Dict

from .models import FleetInputPayload, PathwayOutputMetrics
from .emissions_calculator import (
    get_bev_effective_kwh_per_mile,
    get_hydrogen_effective_kg_per_mile,
)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_json(filename: str) -> Dict[str, Any]:
    path = _DATA_DIR / filename
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


_BASELINES: Dict[str, Any] = _load_json("afleet_baselines.json")

_ENGINE_CONSTANTS = _BASELINES["engine_constants"]
INFRA_LIFESPAN_YEARS: int = int(_ENGINE_CONSTANTS["infra_lifespan_years"]["value"])
BEV_CHARGER_RATIO: float = float(_ENGINE_CONSTANTS["bev_charger_ratio"]["value"])
H2_TIER_THRESHOLD_KG_DAY: float = float(_ENGINE_CONSTANTS["hydrogen_tier_threshold_kg_day"]["value"])
H2_CAPEX_SMALL_LIQUID: float = float(_ENGINE_CONSTANTS["hydrogen_capex_small_liquid_usd"]["value"])
H2_CAPEX_MEDIUM_DELIVERY: float = float(_ENGINE_CONSTANTS["hydrogen_capex_medium_delivery_usd"]["value"])
CNG_FLEET_THRESHOLD_FAST_FILL: int = int(_ENGINE_CONSTANTS["cng_fleet_threshold_fast_fill"]["value"])


def _cold_climate_maintenance_multiplier(pathway: str, cold_climate_flag: bool) -> float:
    if not cold_climate_flag:
        return 1.0
    if pathway == "biodiesel":
        return 1.10
    return 1.0


def _calc_bev_infrastructure(vehicle_count: int) -> Dict[str, float]:
    bev = _BASELINES["bev"]["infrastructure"]
    chargers_required = math.ceil(vehicle_count / BEV_CHARGER_RATIO)
    hw_cost = bev["dcfc_50_hardware_usd"]["default"]
    mr_cost = bev["dcfc_50_make_ready_usd"]["default"]
    cost_per_charger_unit = hw_cost + mr_cost
    total_infra_capex = chargers_required * cost_per_charger_unit
    maint_pct = bev["annual_maintenance_pct"]["default"]
    comms_cost = bev["annual_comms_usd"]["default"]
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


def _calc_hydrogen_infrastructure(vehicle_count: int, annual_mileage_per_vehicle: float) -> Dict[str, Any]:
    h2 = _BASELINES["hydrogen"]
    kg_per_mile = h2["fuel_economy"]["bus_kg_per_mile"]["default"]
    daily_miles_per_vehicle = annual_mileage_per_vehicle / 365.0
    daily_fleet_demand_kg_h2 = vehicle_count * daily_miles_per_vehicle * kg_per_mile
    if daily_fleet_demand_kg_h2 <= H2_TIER_THRESHOLD_KG_DAY:
        tier = "small_liquid_delivery"
        total_infra_capex = H2_CAPEX_SMALL_LIQUID
    else:
        tier = "medium_delivery"
        total_infra_capex = H2_CAPEX_MEDIUM_DELIVERY
    return {
        "daily_fleet_demand_kg_h2": daily_fleet_demand_kg_h2,
        "station_tier": tier,
        "total_infra_capex": total_infra_capex,
    }


def _calc_cng_infrastructure(vehicle_count: int) -> Dict[str, Any]:
    cng = _BASELINES["cng"]["infrastructure"]
    if vehicle_count <= CNG_FLEET_THRESHOLD_FAST_FILL:
        station_type = "time_fill"
        total_infra_capex = cng["time_fill_station_capex_usd"]["default"]
    else:
        station_type = "fast_fill"
        total_infra_capex = cng["fast_fill_station_capex_usd"]["default"]
    return {"station_type": station_type, "total_infra_capex": total_infra_capex}


def _amortize_vehicle_capex(capex_vehicle_total: float, fleet_lifecycle_years: int) -> float:
    return capex_vehicle_total / fleet_lifecycle_years


def _amortize_infra_capex(total_infra_capex: float) -> float:
    return total_infra_capex / INFRA_LIFESPAN_YEARS


def _calc_diesel_pathway(inputs: FleetInputPayload) -> Dict[str, Any]:
    diesel = _BASELINES["diesel"]
    fleet, overrides = inputs.fleet, inputs.overrides
    capex_vehicle_total = diesel["capex"]["vehicle_bus_usd"]["default"] * fleet.vehicle_count
    mpg = diesel["fuel_economy"]["bus_mpg"]["default"]
    price_per_gal = overrides.diesel_price_gal or diesel["fuel_price"]["default_price_gal"]["default"]
    total_miles = fleet.vehicle_count * fleet.annual_mileage_per_vehicle
    gallons_consumed = total_miles / mpg
    opex_fuel = gallons_consumed * price_per_gal
    maint_cpm = diesel["maintenance"]["cost_per_mile_usd"]["default"]
    multiplier = _cold_climate_maintenance_multiplier("diesel", inputs.climate.cold_climate_flag)
    opex_maintenance = total_miles * maint_cpm * multiplier
    return {
        "capex_vehicle_total": capex_vehicle_total,
        "total_infra_capex": 0.0,
        "opex_fuel_usd": opex_fuel,
        "opex_maintenance_usd": opex_maintenance,
    }


def _calc_biodiesel_pathway(inputs: FleetInputPayload) -> Dict[str, Any]:
    biodiesel = _BASELINES["biodiesel"]
    fleet, overrides = inputs.fleet, inputs.overrides
    capex_vehicle_total = biodiesel["capex"]["vehicle_bus_usd"]["default"] * fleet.vehicle_count
    mpg = biodiesel["fuel_economy"]["bus_mpg"]["default"]
    price_per_gal = overrides.diesel_price_gal or biodiesel["fuel_price"]["default_price_gal"]["default"]
    total_miles = fleet.vehicle_count * fleet.annual_mileage_per_vehicle
    gallons_consumed = total_miles / mpg
    opex_fuel = gallons_consumed * price_per_gal
    maint_cpm = biodiesel["maintenance"]["cost_per_mile_usd"]["default"]
    multiplier = _cold_climate_maintenance_multiplier("biodiesel", inputs.climate.cold_climate_flag)
    opex_maintenance = total_miles * maint_cpm * multiplier
    return {
        "capex_vehicle_total": capex_vehicle_total,
        "total_infra_capex": 0.0,
        "opex_fuel_usd": opex_fuel,
        "opex_maintenance_usd": opex_maintenance,
    }


def _calc_bev_pathway(inputs: FleetInputPayload) -> Dict[str, Any]:
    bev = _BASELINES["bev"]
    fleet, overrides = inputs.fleet, inputs.overrides
    capex_vehicle_total = bev["capex"]["vehicle_bus_usd"]["default"] * fleet.vehicle_count
    infra = _calc_bev_infrastructure(fleet.vehicle_count)
    base_kwh_per_mile = bev["fuel_economy"]["transit_bus_kwh_per_mile"]["default"]
    kwh_per_mile_effective = get_bev_effective_kwh_per_mile(
        base_kwh_per_mile=base_kwh_per_mile,
        cold_climate_flag=inputs.climate.cold_climate_flag,
    )
    electricity_rate = overrides.electricity_rate_kwh or bev["fuel_price"]["default_electricity_rate_usd_kwh"]["default"]
    total_miles = fleet.vehicle_count * fleet.annual_mileage_per_vehicle
    kwh_consumed = total_miles * kwh_per_mile_effective
    opex_fuel = kwh_consumed * electricity_rate
    maint_cpm = bev["maintenance"]["cost_per_mile_usd"]["default"]
    multiplier = _cold_climate_maintenance_multiplier("bev", inputs.climate.cold_climate_flag)
    opex_maintenance = total_miles * maint_cpm * multiplier + infra["annual_om_total"]
    return {
        "capex_vehicle_total": capex_vehicle_total,
        "total_infra_capex": infra["total_infra_capex"],
        "opex_fuel_usd": opex_fuel,
        "opex_maintenance_usd": opex_maintenance,
    }


def _calc_hydrogen_pathway(inputs: FleetInputPayload) -> Dict[str, Any]:
    h2 = _BASELINES["hydrogen"]
    fleet = inputs.fleet
    capex_vehicle_total = h2["capex"]["vehicle_bus_usd"]["default"] * fleet.vehicle_count
    infra = _calc_hydrogen_infrastructure(fleet.vehicle_count, fleet.annual_mileage_per_vehicle)
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
    price_per_kg = h2["infrastructure"][tier_key]["price_per_kg"]["default"]
    total_miles = fleet.vehicle_count * fleet.annual_mileage_per_vehicle
    kg_consumed = total_miles * kg_per_mile_effective
    opex_fuel = kg_consumed * price_per_kg
    maint_cpm = h2["maintenance"]["cost_per_mile_usd"]["default"]
    multiplier = _cold_climate_maintenance_multiplier("hydrogen", inputs.climate.cold_climate_flag)
    opex_maintenance = total_miles * maint_cpm * multiplier
    return {
        "capex_vehicle_total": capex_vehicle_total,
        "total_infra_capex": infra["total_infra_capex"],
        "opex_fuel_usd": opex_fuel,
        "opex_maintenance_usd": opex_maintenance,
    }


def _calc_cng_pathway(inputs: FleetInputPayload) -> Dict[str, Any]:
    cng = _BASELINES["cng"]
    fleet = inputs.fleet
    capex_vehicle_total = cng["capex"]["vehicle_bus_usd"]["default"] * fleet.vehicle_count
    infra = _calc_cng_infrastructure(fleet.vehicle_count)
    dge_per_mile = 1.0 / cng["fuel_economy"]["bus_dge_per_mile"]["default"]
    price_per_dge = cng["fuel_price"]["default_price_dge"]["default"]
    total_miles = fleet.vehicle_count * fleet.annual_mileage_per_vehicle
    dge_consumed = total_miles * dge_per_mile
    opex_fuel = dge_consumed * price_per_dge
    maint_cpm = cng["maintenance"]["cost_per_mile_usd"]["default"]
    multiplier = _cold_climate_maintenance_multiplier("cng", inputs.climate.cold_climate_flag)
    opex_maintenance = total_miles * maint_cpm * multiplier
    return {
        "capex_vehicle_total": capex_vehicle_total,
        "total_infra_capex": infra["total_infra_capex"],
        "opex_fuel_usd": opex_fuel,
        "opex_maintenance_usd": opex_maintenance,
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
    capex_vehicle_amortized_usd = _amortize_vehicle_capex(raw["capex_vehicle_total"], inputs.fleet.lifecycle_years)
    capex_infra_amortized_usd = _amortize_infra_capex(raw["total_infra_capex"])
    incentives_applied_usd = inputs.overrides.incentive_credits_usd or 0.0
    tco_total_usd = (
        capex_vehicle_amortized_usd
        + capex_infra_amortized_usd
        + raw["opex_fuel_usd"]
        + raw["opex_maintenance_usd"]
        - incentives_applied_usd
    )
    return PathwayOutputMetrics(
        fuel_type=fuel_type,
        tco_total_usd=round(tco_total_usd, 2),
        capex_vehicle_amortized_usd=round(capex_vehicle_amortized_usd, 2),
        capex_infra_amortized_usd=round(capex_infra_amortized_usd, 2),
        opex_fuel_usd=round(raw["opex_fuel_usd"], 2),
        opex_maintenance_usd=round(raw["opex_maintenance_usd"], 2),
        incentives_applied_usd=round(incentives_applied_usd, 2),
        lifecycle_co2e_tons=0.0,
        cold_climate_adjustment_applied=bool(inputs.climate.cold_climate_flag),
    )


def calculate_all_pathways(inputs: FleetInputPayload) -> Dict[str, PathwayOutputMetrics]:
    return {ft: calculate_pathway_tco(ft, inputs) for ft in _PATHWAY_CALCULATORS}
EOF

cat > engine/resolver.py << 'EOF'
import json
from pathlib import Path
from typing import Any, Dict

from .models import FleetInputPayload

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CROSSWALK: Dict[str, Any] = json.loads((_DATA_DIR / "state_crosswalk.json").read_text(encoding="utf-8"))


def resolve_input_payload(payload: FleetInputPayload) -> FleetInputPayload:
    if payload.climate.cold_climate_flag is None:
        state_code = payload.region.state_prov.strip().upper()
        regional_info = _CROSSWALK.get(state_code, {})
        payload.climate.cold_climate_flag = regional_info.get("cold_climate", False)
    return payload
EOF

cat > api/main.py << 'EOF'
from typing import Dict

from fastapi import FastAPI, HTTPException

from engine.models import FleetInputPayload, EngineOutputPayload, PathwayOutputMetrics, VerdictConfig
from engine.resolver import resolve_input_payload
from engine.tco_calculator import calculate_all_pathways, INFRA_LIFESPAN_YEARS
from engine.emissions_calculator import calculate_all_pathway_emissions

app = FastAPI(title="FleetPath Core Engine API", version="1.3")

_PATHWAY_DISPLAY_NAMES = {
    "diesel": "Diesel",
    "bev": "Battery-Electric",
    "hydrogen": "Hydrogen Fuel Cell",
    "cng": "CNG",
    "biodiesel": "Biodiesel (B20)",
}


def _normalize_min_max_low_is_best(values: Dict[str, float]) -> Dict[str, float]:
    lowest = min(values.values())
    highest = max(values.values())
    if highest == lowest:
        return {k: 100.0 for k in values}
    return {k: 100.0 * (highest - v) / (highest - lowest) for k, v in values.items()}


def _build_summary_text(winner_fuel_type: str, payback_years: float, emissions_reduction_pct: float) -> str:
    if winner_fuel_type == "diesel":
        return (
            "Diesel remains the lowest-cost, carbon-adjusted pathway for this fleet profile "
            "under current assumptions; no alternative pathway clears the cost-carbon utility threshold."
        )
    display_name = _PATHWAY_DISPLAY_NAMES[winner_fuel_type]
    return (
        f"{display_name} wins: an estimated {payback_years:.1f}-year payback versus the diesel "
        f"baseline, cutting lifecycle CO2e emissions by {emissions_reduction_pct:.1f}% relative to diesel."
    )


def _compute_verdict(pathways: Dict[str, PathwayOutputMetrics], fleet_lifecycle_years: int) -> VerdictConfig:
    cost_values = {ft: p.tco_total_usd for ft, p in pathways.items()}
    carbon_values = {ft: p.lifecycle_co2e_tons for ft, p in pathways.items()}
    cost_scores = _normalize_min_max_low_is_best(cost_values)
    carbon_scores = _normalize_min_max_low_is_best(carbon_values)
    utility_scores = {ft: (cost_scores[ft] * 0.60) + (carbon_scores[ft] * 0.40) for ft in pathways}
    winner = max(utility_scores, key=utility_scores.get)
    diesel = pathways["diesel"]
    winner_result = pathways[winner]
    if winner == "diesel":
        payback_years = 0.0
        emissions_reduction_pct = 0.0
    else:
        winner_vehicle_capex_total = winner_result.capex_vehicle_amortized_usd * fleet_lifecycle_years
        winner_infra_capex_total = winner_result.capex_infra_amortized_usd * INFRA_LIFESPAN_YEARS
        diesel_vehicle_capex_total = diesel.capex_vehicle_amortized_usd * fleet_lifecycle_years
        incremental_capex = (winner_vehicle_capex_total + winner_infra_capex_total) - diesel_vehicle_capex_total
        annual_opex_savings = (diesel.opex_fuel_usd + diesel.opex_maintenance_usd) - (
            winner_result.opex_fuel_usd + winner_result.opex_maintenance_usd
        )
        if annual_opex_savings > 0:
            payback_years = round(incremental_capex / annual_opex_savings, 1)
        else:
            payback_years = float(fleet_lifecycle_years)
        if diesel.lifecycle_co2e_tons > 0:
            emissions_reduction_pct = round(
                (diesel.lifecycle_co2e_tons - winner_result.lifecycle_co2e_tons) / diesel.lifecycle_co2e_tons * 100,
                1,
            )
        else:
            emissions_reduction_pct = 0.0
    return VerdictConfig(
        winner_pathway=winner,
        summary_text=_build_summary_text(winner, payback_years, emissions_reduction_pct),
        payback_years=payback_years,
        emissions_reduction_pct=emissions_reduction_pct,
    )


@app.get("/api/v1/health")
def health_check():
    return {"status": "operational", "engine_version": "1.3"}


@app.post("/api/v1/calculate", response_model=EngineOutputPayload)
def calculate_fleet_pathways(payload: FleetInputPayload):
    try:
        resolved = resolve_input_payload(payload)
        pathways = calculate_all_pathways(resolved)
        emissions = calculate_all_pathway_emissions(resolved)
        for fuel_type, result in pathways.items():
            result.lifecycle_co2e_tons = emissions[fuel_type]
        verdict = _compute_verdict(pathways, resolved.fleet.lifecycle_years)
        return EngineOutputPayload(verdict=verdict, pathways=list(pathways.values()))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
EOF

cat > tests/test_infra_scaling.py << 'EOF'
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
    assert result_10.capex_infra_amortized_usd == pytest.approx(expected_infra_amortized_10, abs=0.01)
    assert result_11.capex_infra_amortized_usd == pytest.approx(expected_infra_amortized_11, abs=0.01)
    assert result_11.capex_infra_amortized_usd > result_10.capex_infra_amortized_usd


def test_hydrogen_station_tier_steps_up_past_300kg_day():
    result_101 = calculate_all_pathways(_build_payload(vehicle_count=101))["hydrogen"]
    result_102 = calculate_all_pathways(_build_payload(vehicle_count=102))["hydrogen"]
    small_tier_capex = _BASELINES["engine_constants"]["hydrogen_capex_small_liquid_usd"]["value"]
    medium_tier_capex = _BASELINES["engine_constants"]["hydrogen_capex_medium_delivery_usd"]["value"]
    assert result_101.capex_infra_amortized_usd == pytest.approx(small_tier_capex / INFRA_LIFESPAN_YEARS, abs=0.01)
    assert result_102.capex_infra_amortized_usd == pytest.approx(medium_tier_capex / INFRA_LIFESPAN_YEARS, abs=0.01)


def test_cng_station_type_steps_up_past_5_vehicles():
    time_fill_capex = _BASELINES["cng"]["infrastructure"]["time_fill_station_capex_usd"]["default"]
    fast_fill_capex = _BASELINES["cng"]["infrastructure"]["fast_fill_station_capex_usd"]["default"]
    result_5 = calculate_all_pathways(_build_payload(vehicle_count=5))["cng"]
    result_6 = calculate_all_pathways(_build_payload(vehicle_count=6))["cng"]
    assert result_5.capex_infra_amortized_usd == pytest.approx(time_fill_capex / INFRA_LIFESPAN_YEARS, abs=0.01)
    assert result_6.capex_infra_amortized_usd == pytest.approx(fast_fill_capex / INFRA_LIFESPAN_YEARS, abs=0.01)


def test_infrastructure_amortization_is_decoupled_from_fleet_lifecycle_years():
    result_10yr = calculate_all_pathways(_build_payload(vehicle_count=10, lifecycle_years=10))["bev"]
    result_15yr = calculate_all_pathways(_build_payload(vehicle_count=10, lifecycle_years=15))["bev"]
    assert result_10yr.capex_infra_amortized_usd == pytest.approx(result_15yr.capex_infra_amortized_usd, abs=0.001)
    assert result_10yr.capex_vehicle_amortized_usd != pytest.approx(result_15yr.capex_vehicle_amortized_usd, abs=0.001)
    assert result_10yr.capex_vehicle_amortized_usd > result_15yr.capex_vehicle_amortized_usd
EOF

cat > tests/test_emissions_grid.py << 'EOF'
import pytest

from engine.models import FleetInputPayload, RegionConfig, FleetConfig, OverridesConfig, ClimateConfig
from engine.resolver import resolve_input_payload
from engine.emissions_calculator import (
    calculate_all_pathway_emissions,
    get_subregion_for_state,
    get_grid_factor_lb_per_mwh,
    UnknownRegionError,
)


def _build_payload(state_prov, vehicle_count=10, annual_mileage_per_vehicle=12000, lifecycle_years=12):
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


def test_crosswalk_resolves_expected_subregions():
    assert get_subregion_for_state("IN") == "MROE"
    assert get_subregion_for_state("QC") == "ECCC_QC"
    assert get_subregion_for_state("ca") == "CAMX"


def test_unknown_region_raises():
    with pytest.raises(UnknownRegionError):
        get_subregion_for_state("ZZ")


def test_grid_factor_indiana_dirtier_than_quebec():
    indiana_factor = get_grid_factor_lb_per_mwh("IN")
    quebec_factor = get_grid_factor_lb_per_mwh("QC")
    assert indiana_factor > quebec_factor


def test_bev_emissions_indiana_exceeds_quebec_same_fleet():
    indiana_emissions = calculate_all_pathway_emissions(_build_payload("IN"))["bev"]
    quebec_emissions = calculate_all_pathway_emissions(_build_payload("QC"))["bev"]
    assert indiana_emissions > quebec_emissions
    assert quebec_emissions > 0


def test_hydrogen_electrolysis_emissions_indiana_exceeds_quebec_same_fleet():
    indiana_emissions = calculate_all_pathway_emissions(_build_payload("IN"))["hydrogen"]
    quebec_emissions = calculate_all_pathway_emissions(_build_payload("QC"))["hydrogen"]
    assert indiana_emissions > quebec_emissions


def test_diesel_emissions_are_region_independent():
    indiana_emissions = calculate_all_pathway_emissions(_build_payload("IN"))["diesel"]
    quebec_emissions = calculate_all_pathway_emissions(_build_payload("QC"))["diesel"]
    assert indiana_emissions == pytest.approx(quebec_emissions, abs=0.001)
EOF

cat > grid_factors.json << 'EOF'
{
  "CAMX": {"grid_factor_lb_per_mwh": 400.0},
  "MROE": {"grid_factor_lb_per_mwh": 800.0},
  "ECCC_QC": {"grid_factor_lb_per_mwh": 20.0},
  "TRE": {"grid_factor_lb_per_mwh": 500.0},
  "NWPP": {"grid_factor_lb_per_mwh": 450.0}
}
EOF

cat > requirements.txt << 'EOF'
fastapi>=0.110.0
pydantic>=2.7.0
pytest>=8.0.0
EOF

echo "FleetPath Phase 1 files written."
