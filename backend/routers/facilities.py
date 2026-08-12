import uuid
from fastapi import APIRouter, HTTPException
from models import FacilityCreate, FacilityResponse
from services.storage import save_facility, get_facility

router = APIRouter()


@router.post("/facilities", response_model=FacilityResponse, status_code=201)
async def create_facility(body: FacilityCreate):
    facility_id = str(uuid.uuid4())[:8]
    data = body.model_dump()
    saved = save_facility(facility_id, data)
    return saved


@router.get("/facilities/{facility_id}", response_model=FacilityResponse)
async def get_facility_by_id(facility_id: str):
    facility = get_facility(facility_id)
    if not facility:
        raise HTTPException(
            status_code=404,
            detail={
                "error": "facility_not_found",
                "message": f"Facility '{facility_id}' does not exist.",
                "suggestion": "Use GET /api/demo/facility for the pre-seeded demo, or POST /api/facilities to create one.",
            },
        )
    return facility
