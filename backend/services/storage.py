"""
Pandas + CSV storage layer.
Thread-safe in-memory dict (facility_id → dict), persisted to facilities.csv.

PUBLIC API FOR OPTIMIZATION OWNER
──────────────────────────────────
The optimization module can import and call get_facility_data() directly
instead of making an HTTP call to the same process:

    from services.storage import get_facility_data
    facility, consumption_df = get_facility_data("demo-1")

`facility`        — plain dict matching FacilityResponse shape
`consumption_df`  — pandas DataFrame with columns:
                    timestamp, occupancy_pct, temperature_c, energy_kwh, water_liters
                    (comes from seed.DEMO_CONSUMPTION for demo-1; empty for user facilities)
"""
import json
import threading
from pathlib import Path

import pandas as pd

_lock = threading.Lock()
_DATA_DIR = Path(__file__).parent.parent / "data"
_CSV_PATH = _DATA_DIR / "facilities.csv"

# In-memory store: id → facility dict
_store: dict[str, dict] = {}


# ─── Init ──────────────────────────────────────────────────────────────────────

def _ensure_data_dir() -> None:
    try:
        _DATA_DIR.mkdir(exist_ok=True)
    except Exception:
        pass


def _load_from_csv() -> None:
    """Populate _store from CSV on startup (survives a restart during rehearsal)."""
    if not _CSV_PATH.exists():
        return
    try:
        df = pd.read_csv(_CSV_PATH)
        for _, row in df.iterrows():
            fid = str(row["id"])
            equipment = json.loads(row.get("equipment", "[]"))
            _store[fid] = {
                "id": fid,
                "name": row["name"],
                "occupants": int(row["occupants"]),
                "electricity_tariff": float(row["electricity_tariff"]),
                "water_tariff": float(row["water_tariff"]),
                "equipment": equipment,
            }
    except Exception:
        pass  # Corrupt CSV — start fresh; seed() will repopulate


def _save_to_csv() -> None:
    """Persist current in-memory store to CSV (called on every write)."""
    try:
        rows = [
            {
                "id": f["id"],
                "name": f["name"],
                "occupants": f["occupants"],
                "electricity_tariff": f["electricity_tariff"],
                "water_tariff": f["water_tariff"],
                "equipment": json.dumps(f["equipment"]),
            }
            for f in _store.values()
        ]
        pd.DataFrame(rows).to_csv(_CSV_PATH, index=False)
    except Exception:
        pass  # Read-only filesystem (e.g. Vercel serverless) — keep in-memory


def init_storage() -> None:
    """Call once at application startup."""
    _ensure_data_dir()
    _load_from_csv()


# ─── Write ─────────────────────────────────────────────────────────────────────

def save_facility(facility_id: str, data: dict) -> dict:
    """Store or overwrite a facility record and persist to CSV."""
    with _lock:
        record = {**data, "id": facility_id}
        _store[facility_id] = record
        _save_to_csv()
        return record


# ─── Read ──────────────────────────────────────────────────────────────────────

def get_facility(facility_id: str) -> dict:
    """Return facility dict from store, or fallback record for serverless stateless execution."""
    with _lock:
        if facility_id in _store:
            return _store[facility_id]
        
        # Fallback for serverless stateless execution across Lambda instances
        try:
            from seed import DEMO_FACILITY
            return {**DEMO_FACILITY, "id": facility_id}
        except Exception:
            return {
                "id": facility_id,
                "name": "Campus Facility",
                "occupants": 100,
                "electricity_tariff": 8.5,
                "water_tariff": 0.02,
                "equipment": [
                    {"type": "AC", "quantity": 30, "rated_power_kw": 1.5, "min_level": 0.3, "max_level": 1.0, "controllable": True},
                    {"type": "Lighting", "quantity": 80, "rated_power_kw": 0.02, "min_level": 0.1, "max_level": 1.0, "controllable": True}
                ]
            }


def all_facility_ids() -> list[str]:
    """Return list of all stored facility IDs."""
    with _lock:
        return list(_store.keys())


# ─── Optimization-owner integration ───────────────────────────────────────────

def get_facility_data(facility_id: str) -> tuple[dict | None, pd.DataFrame]:
    """
    Public function for the optimization owner to call directly.

    Returns
    -------
    facility : dict | None
        The facility record (same shape as FacilityResponse), or None if
        the ID does not exist.
    consumption_df : pd.DataFrame
        24-hour consumption records as a DataFrame with columns:
            timestamp       (str)   ISO-8601 hourly
            occupancy_pct   (float) 0–100
            temperature_c   (float) °C
            energy_kwh      (float) measured kWh/hr
            water_liters    (float) measured L/hr
        For the demo facility ("demo-1") this is the seeded synthetic data.
        For user-created facilities it is currently an empty DataFrame
        (extend here when live metering is added).

    Usage (from optimization module)
    ---------------------------------
        from services.storage import get_facility_data
        import pandas as pd

        facility, df = get_facility_data("demo-1")
        if facility is None:
            raise ValueError("Facility not found")

        tariff = facility["electricity_tariff"]
        equipment = facility["equipment"]
        peak_hour_energy = df.loc[df["energy_kwh"].idxmax()]
    """
    facility = get_facility(facility_id)

    # Import here to avoid circular import at module load time
    try:
        from seed import DEMO_CONSUMPTION
        consumption_df = pd.DataFrame(DEMO_CONSUMPTION)
    except ImportError:
        consumption_df = pd.DataFrame(
            columns=["timestamp", "occupancy_pct", "temperature_c",
                     "energy_kwh", "water_liters"]
        )

    return facility, consumption_df
