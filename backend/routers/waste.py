from fastapi import APIRouter, HTTPException
from models import WasteDetectionRequest, WasteDetectionResponse
from services.storage import get_facility
from services.waste_detector import detect_waste
from seed import DEMO_CONSUMPTION

router = APIRouter()


@router.post("/waste-detection", response_model=WasteDetectionResponse)
async def waste_detection(body: WasteDetectionRequest):
    facility = get_facility(body.facility_id)
    if not facility:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "facility_not_found",
                "message": f"No facility found with id '{body.facility_id}'.",
                "suggestion": "Use facility_id 'demo-1' for the pre-seeded demo, "
                              "or POST /api/facilities to register a new facility.",
            },
        )
    # Run the 3 rule-based checks against the consumption dataset.
    # For demo-1 this is the NumPy-generated 24h series with 3 injected faults.
    issues = detect_waste(DEMO_CONSUMPTION)
    return {"issues": [i.model_dump() for i in issues]}
