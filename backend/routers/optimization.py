"""
Optimization router — /api/optimize and /api/simulate.

Both endpoints reuse the same solve_with_wolfram_or_fallback() function.
/api/simulate passes overrides; /api/optimize passes none.
InfeasibleError is caught and returned as the shared 422 error shape.
"""
from fastapi import APIRouter, HTTPException

from models import OptimizeRequest, SimulateRequest, OptimizeResponse
from services.storage import get_facility_data
from services.wolfram_client import solve_with_wolfram_or_fallback
from services.lp_solver import InfeasibleError

router = APIRouter()


def _not_found(facility_id: str):
    raise HTTPException(
        status_code=404,
        detail={
            "error": "facility_not_found",
            "message": f"No facility found with id '{facility_id}'.",
            "suggestion": (
                "Use facility_id 'demo-1' for the pre-seeded demo, "
                "or POST /api/facilities to register a new facility."
            ),
        },
    )


@router.post("/optimize", response_model=OptimizeResponse)
async def optimize(body: OptimizeRequest):
    """
    Run the full optimization with no overrides.
    Tries Wolfram first; falls back to PuLP transparently.
    solver_used in the response tells you which path ran.
    """
    facility, df = get_facility_data(body.facility_id)
    if facility is None:
        _not_found(body.facility_id)

    records = df.to_dict("records") if not df.empty else []

    try:
        result = solve_with_wolfram_or_fallback(facility, records)
    except InfeasibleError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "lp_infeasible",
                "message": str(exc),
                "suggestion": (
                    "Check that min_level < max_level for every equipment item "
                    "and that the service-floor constraints (AC/lighting ≥ 0.70 "
                    "during peak occupancy) are achievable."
                ),
            },
        )

    return result


@router.post("/simulate", response_model=OptimizeResponse)
async def simulate(body: SimulateRequest):
    """
    Re-run the same optimization with optional overrides substituted in.
    Reuses solve_with_wolfram_or_fallback() — no duplicated logic.

    Overrides:
      occupancy_pct      — replace occupancy in all 24 blocks
      temperature_c      — replace temperature in all 24 blocks
      ac_operating_level — pin AC operating level (min = max = that value)
    """
    facility, df = get_facility_data(body.facility_id)
    if facility is None:
        _not_found(body.facility_id)

    records = df.to_dict("records") if not df.empty else []

    overrides: dict = {}
    if body.occupancy_pct is not None:
        overrides["occupancy_pct"] = body.occupancy_pct
    if body.temperature_c is not None:
        overrides["temperature_c"] = body.temperature_c
    if body.ac_operating_level is not None:
        overrides["ac_operating_level"] = body.ac_operating_level

    try:
        result = solve_with_wolfram_or_fallback(facility, records, overrides)
    except InfeasibleError as exc:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "lp_infeasible",
                "message": str(exc),
                "suggestion": (
                    "The combination of overrides created an infeasible region. "
                    "Try a less extreme ac_operating_level or occupancy value."
                ),
            },
        )

    return result
