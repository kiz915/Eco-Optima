from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from services.storage import init_storage
from seed import seed

from routers.health import router as health_router
from routers.facilities import router as facilities_router
from routers.demo import router as demo_router
from routers.waste import router as waste_router
from routers.optimization import router as optimization_router

app = FastAPI(
    title="EcoOptima API",
    description="HackZen'26 — Wolfram-powered campus resource optimization",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Eager initialization for serverless cold starts
init_storage()
seed()

# Startup: init storage and seed demo data
@app.on_event("startup")
async def startup():
    init_storage()
    seed()

# Mount all routers under /api
app.include_router(health_router, prefix="/api", tags=["Health"])
app.include_router(facilities_router, prefix="/api", tags=["Facilities"])
app.include_router(demo_router, prefix="/api", tags=["Demo"])
app.include_router(waste_router, prefix="/api", tags=["Waste Detection"])
app.include_router(optimization_router, prefix="/api", tags=["Optimization"])
