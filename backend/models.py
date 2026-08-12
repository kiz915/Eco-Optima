"""
Pydantic models — field validators enforce the contract's data rules so
the input screen returns clear 422s instead of silent bad data.
"""
from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


# ─── Equipment ────────────────────────────────────────────────────────────────

class Equipment(BaseModel):
    type: str = Field(..., min_length=1, description="Equipment type label")
    quantity: int = Field(..., gt=0, description="Must be ≥ 1")
    rated_power_kw: float = Field(..., gt=0, description="kW per unit — must be > 0")
    min_level: float = Field(0.3, ge=0.0, le=1.0, description="Minimum operating level 0–1")
    max_level: float = Field(1.0, ge=0.0, le=1.0, description="Maximum operating level 0–1")
    controllable: bool = True

    @field_validator("type")
    @classmethod
    def type_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Equipment type cannot be blank")
        return v.strip()

    @model_validator(mode="after")
    def min_le_max(self) -> "Equipment":
        if self.min_level > self.max_level:
            raise ValueError(
                f"min_level ({self.min_level}) must be ≤ max_level ({self.max_level})"
            )
        return self


# ─── Facilities ───────────────────────────────────────────────────────────────

class FacilityCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Facility display name")
    occupants: int = Field(..., gt=0, description="Number of occupants — must be > 0")
    electricity_tariff: float = Field(..., gt=0, description="₹/kWh — must be > 0")
    water_tariff: float = Field(..., gt=0, description="₹/litre — must be > 0")
    equipment: List[Equipment] = Field(
        ..., min_length=1, description="At least one equipment entry required"
    )

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Facility name cannot be blank")
        return v.strip()

    @field_validator("electricity_tariff", "water_tariff")
    @classmethod
    def tariffs_sensible(cls, v: float, info) -> float:
        # Upper-bound sanity: no real tariff is ₹10,000/kWh
        if v > 10_000:
            raise ValueError(f"{info.field_name} seems unrealistically high ({v})")
        return v


class FacilityResponse(FacilityCreate):
    id: str


# ─── Demo ─────────────────────────────────────────────────────────────────────

class ConsumptionRecord(BaseModel):
    timestamp: str
    occupancy_pct: float
    temperature_c: float
    energy_kwh: float
    water_liters: float


class ConsumptionResponse(BaseModel):
    records: List[ConsumptionRecord]


# ─── Waste Detection ──────────────────────────────────────────────────────────

class WasteDetectionRequest(BaseModel):
    facility_id: str = Field(..., min_length=1)


class WasteIssue(BaseModel):
    title: str
    severity: str          # "high" | "medium" | "low"
    evidence: str          # real numbers from actual dataset, never placeholder text
    estimated_impact_kwh: float
    recommendation: str


class WasteDetectionResponse(BaseModel):
    issues: List[WasteIssue]


# ─── Optimization (optimization owner's territory — shapes only) ────────────

class OptimizeRequest(BaseModel):
    facility_id: str


class SimulateRequest(BaseModel):
    facility_id: str
    occupancy_pct: Optional[float] = None
    temperature_c: Optional[float] = None
    ac_operating_level: Optional[float] = None


class ResourceSummary(BaseModel):
    energy_kwh: float
    cost_rupees: float
    water_liters: float


class Savings(BaseModel):
    energy_reduction_pct: float
    cost_saving_pct: float


class ScheduleEntry(BaseModel):
    time: str
    equipment: str
    current_level: float
    optimized_level: float


class OptimizeResponse(BaseModel):
    solver_used: str   # "wolfram" or "fallback" — optimization owner sets this
    baseline: ResourceSummary
    optimized: ResourceSummary
    savings: Savings
    schedule: List[ScheduleEntry]


# ─── Health ───────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str


class WolframHealthResponse(BaseModel):
    wolfram_available: bool
    mode: str              # "wolfram" or "fallback"
    note: Optional[str] = None


# ─── Standard error shape ────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    error: str
    message: str
    suggestion: str
