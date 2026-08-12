from fastapi import APIRouter
from models import FacilityResponse, ConsumptionResponse
from seed import DEMO_FACILITY, DEMO_FACILITY_ID, DEMO_CONSUMPTION

router = APIRouter()


@router.get("/demo/facility", response_model=FacilityResponse)
async def demo_facility():
    """Return the pre-seeded demo facility — skip live data entry during pitch."""
    return {**DEMO_FACILITY, "id": DEMO_FACILITY_ID}


@router.get("/demo/consumption", response_model=ConsumptionResponse)
async def demo_consumption():
    """Return the 24-hour NumPy-generated consumption series with injected inefficiencies."""
    return {"records": DEMO_CONSUMPTION}
