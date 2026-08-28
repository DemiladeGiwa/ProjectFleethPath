from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Union


class RegionConfig(BaseModel):
    state_prov: str = Field(default="IN", max_length=2, description="2-letter state or province code")


class FleetConfig(BaseModel):
    vehicle_type: str = Field(default="school_bus_typeC", description="Vehicle classification type")
    vehicle_count: int = Field(default=10, gt=0, description="Number of vehicles in fleet")
    annual_mileage_per_vehicle: float = Field(default=12000.0, gt=0.0, description="Annual miles per vehicle")
    lifecycle_years: int = Field(default=12, gt=0, description="Fleet lifecycle horizon in years")


class OverridesConfig(BaseModel):
    # NOTE: these overrides remain currency-unlabeled inputs. Not addressed
    # in this change set -- flagged separately, see delivery notes.
    electricity_rate_kwh: Optional[float] = None
    diesel_price_gal: Optional[float] = None
    incentive_credits_usd: Optional[float] = 0.0
    # DISCLOSED CHANGE (scoring-policy control): exposes the verdict
    # scorer's cost/carbon blend weight as a real user input instead of a
    # silent hardcoded 0.6. None resolves to that same 0.6 default in
    # api/main.py, so an unset value changes nothing for existing callers.
    # Represents "weight given to cost"; carbon weight is 1 - this value.
    cost_carbon_weight: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="User-selected weight given to cost vs. carbon in the verdict utility score; None uses the 0.6 default",
    )


class ClimateConfig(BaseModel):
    cold_climate_flag: Optional[bool] = None


class FleetInputPayload(BaseModel):
    region: RegionConfig = Field(default_factory=RegionConfig)
    fleet: FleetConfig = Field(default_factory=FleetConfig)
    overrides: OverridesConfig = Field(default_factory=OverridesConfig)
    climate: ClimateConfig = Field(default_factory=ClimateConfig)


class AssumptionEntry(BaseModel):
    param_id: str
    label: str
    value: Union[float, str]
    unit: str
    source_agency: str
    is_override: bool


class PathwayOutputMetrics(BaseModel):
    fuel_type: str
    currency: Literal["USD", "CAD"]
    tco_total: float
    capex_vehicle_amortized: float
    capex_infra_amortized: float
    opex_fuel: float
    opex_maintenance: float
    incentives_applied: float
    lifecycle_co2e_tons: float
    cold_climate_adjustment_applied: bool
    assumptions: List[AssumptionEntry] = Field(default_factory=list)


class VerdictConfig(BaseModel):
    winner_pathway: str
    summary_text: str
    payback_years: Optional[float] = None
    emissions_reduction_pct: float


class PaybackVectorItem(BaseModel):
    fuel_type: str
    currency: Literal["USD", "CAD"]
    cumulative_cost_by_year: List[float]


class AdvancedDashboardPayload(BaseModel):
    tco_composition: List[PathwayOutputMetrics] = Field(default_factory=list)
    payback_vector: List[PaybackVectorItem] = Field(default_factory=list)
    payback_vector_years_axis: List[int] = Field(default_factory=list)


class EngineOutputPayload(BaseModel):
    verdict: VerdictConfig
    pathways: List[PathwayOutputMetrics]
    advanced: Optional[AdvancedDashboardPayload] = None
