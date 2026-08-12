"""
Demo facility seed + NumPy-generated synthetic 24-hour consumption.

The consumption data has THREE deliberately injected inefficiencies
so waste detection has real, checkable patterns to catch:

  INEFFICIENCY A — AC at full power 11pm–5am despite <15% occupancy.
    Hours 23, 00, 01, 02, 03, 04 → energy stays at ~52–56 kWh/hr
    (should drop to ~22 kWh/hr if AC stepped down to minimum).
    This is what Rule 1 (low-occ + high energy) catches.

  INEFFICIENCY B — Elevated baseline after midnight even when
    occupancy ≈ 5 % because lighting + AC never enter setback mode.
    Rule 2 (nighttime load above baseline) catches this.

  INEFFICIENCY C — Peak water draw at 02:00 (irrigation timer fires
    during lowest occupancy window). Rule 3 catches the
    occupancy-vs-water misalignment.
"""
import numpy as np
from services.storage import save_facility

DEMO_FACILITY_ID = "demo-1"

DEMO_FACILITY = {
    "name": "Hostel Block A",
    "occupants": 100,
    "electricity_tariff": 8.5,
    "water_tariff": 0.02,
    "equipment": [
        # 30 ACs × 1.5 kW  — primary waste driver
        {
            "type": "AC",
            "quantity": 30,
            "rated_power_kw": 1.5,
            "min_level": 0.3,
            "max_level": 1.0,
            "controllable": True,
        },
        # 40 ceiling fans × 0.075 kW
        {
            "type": "Fan",
            "quantity": 40,
            "rated_power_kw": 0.075,
            "min_level": 0.2,
            "max_level": 1.0,
            "controllable": True,
        },
        # 80 LED lights × 0.02 kW
        {
            "type": "Lighting",
            "quantity": 80,
            "rated_power_kw": 0.02,
            "min_level": 0.05,
            "max_level": 1.0,
            "controllable": True,
        },
        # 2 water pumps × 3.7 kW  — non-controllable (always on)
        {
            "type": "Water Pump",
            "quantity": 2,
            "rated_power_kw": 3.7,
            "min_level": 1.0,
            "max_level": 1.0,
            "controllable": False,
        },
    ],
}


def _generate_consumption() -> list[dict]:
    """
    Generate a realistic 24-hour consumption series with NumPy.
    Three real inefficiencies are injected — see module docstring.
    """
    rng = np.random.default_rng(seed=42)   # reproducible

    # ── Base occupancy profile (realistic hostel rhythm) ──────────────────
    # Hour:  0   1   2   3   4   5   6   7   8   9  10  11  12
    occ =  [12,  8,  5,  5,  8, 20, 45, 72, 85, 90, 88, 80, 70,
    # Hour: 13  14  15  16  17  18  19  20  21  22  23
            65, 60, 58, 68, 82, 90, 95, 88, 72, 35, 15]

    # ── Temperature profile (°C, peaks 14:00) ─────────────────────────────
    temp = [24, 23, 23, 22, 22, 23, 25, 26, 27, 28, 29, 30, 31,
            32, 33, 33, 32, 31, 30, 29, 28, 27, 26, 25]

    # ── Max installed capacity (kW) ────────────────────────────────────────
    # 30 AC × 1.5 + 40 fan × 0.075 + 80 light × 0.02 + 2 pump × 3.7
    ac_full    = 30 * 1.5          # 45.0 kW
    fan_full   = 40 * 0.075        # 3.0 kW
    light_full = 80 * 0.02         # 1.6 kW
    pump_base  = 2  * 3.7          # 7.4 kW  (always on)

    records = []
    daily_peak_energy = None   # we'll compute after first pass

    for h in range(24):
        occ_frac  = occ[h] / 100
        temp_c    = temp[h]
        noise     = rng.normal(0, 0.8)

        # ── AC: proportional to occupancy + temperature ─────────────────
        # Normal behaviour: scale between 30% (min setback) and 100% with occ+temp
        ac_scale = max(0.3, min(1.0,
            0.3 + 0.5 * occ_frac + 0.2 * (temp_c - 22) / 11
        ))

        # INJECT INEFFICIENCY A & B: 11pm (23) through 5am (04) AC stays at
        # full power because the BMS timer was never configured to step down.
        # Occupancy 5–15%, but AC runs at 85–95% of full capacity.
        if h in (23, 0, 1, 2, 3, 4):
            ac_scale = rng.uniform(0.85, 0.95)   # ← injected fault

        ac_kw = ac_full * ac_scale

        # Fan: steps with occupancy, off below 10% occ
        fan_kw = fan_full * max(0.0, occ_frac - 0.1) if occ_frac > 0.1 else fan_full * 0.05

        # Lighting: on 6am-11pm proportional to occ, reduced after 10pm
        if 6 <= h <= 22:
            light_kw = light_full * max(0.1, occ_frac)
        else:
            # should be near-off at night — but not fully off (common area lights)
            light_kw = light_full * 0.15

        energy_kwh = round(ac_kw + fan_kw + light_kw + pump_base + noise, 2)

        # ── Water ───────────────────────────────────────────────────────
        # Normal: tracks occupancy; 150 L/person at peak
        base_water = occ_frac * 100 * 1.5 * max(0.1, 1 - abs(h - 8) / 16)

        # INJECT INEFFICIENCY C: irrigation timer fires at 02:00 —
        # autonomous 450 L dump regardless of occupancy.
        if h == 2:
            base_water += 450   # ← injected fault

        water_liters = round(max(20, base_water + rng.normal(0, 15)), 1)

        records.append({
            "timestamp": f"2026-08-11T{h:02d}:00:00",
            "occupancy_pct": float(occ[h]),
            "temperature_c": float(temp_c),
            "energy_kwh": energy_kwh,
            "water_liters": water_liters,
        })

    return records


# Generate once at import time so waste_detector can use the same list
DEMO_CONSUMPTION: list[dict] = _generate_consumption()


def seed():
    """Seed demo facility into storage — called once at startup."""
    save_facility(DEMO_FACILITY_ID, DEMO_FACILITY)
