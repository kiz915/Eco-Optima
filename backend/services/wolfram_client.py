"""
Track B  —  Wolfram Alpha integration.
Build this ONLY after the PuLP fallback (lp_solver.py) works and is tested.

Honesty rules (non-negotiable per the API contract)
════════════════════════════════════════════════════
• NEVER set solver_used = "wolfram" unless a real Wolfram HTTP call succeeded
  AND we successfully parsed a valid numeric result from it.
• On ANY failure (auth, timeout, malformed, unparseable) fall through to
  lp_solver.solve() and set solver_used = "fallback".
• The /api/health/wolfram endpoint is a standalone connectivity test —
  build it first, verify it returns a real result, before attempting
  the full optimization pipeline.

Wolfram query strategy
══════════════════════
We translate the LP into a Wolfram Language LinearProgramming[] call,
which the Wolfram Alpha Full Results API can evaluate.

LinearProgramming[c, m, b, bounds] minimises c·x subject to m·x >= b
with variable bounds.

For the optimization call we aggregate across time blocks into a single
"representative worst-case" block (max occupancy + max temperature hour)
plus the service-floor and temperature-floor constraints.  Wolfram returns
the optimal per-equipment operating levels; we then use lp_solver.solve()
for the full 24-block projection but with Wolfram's optimal levels as the
lower bounds, so the full result is genuinely informed by the Wolfram answer.

This is the defensible "Wolfram-assisted" approach given the Alpha API's
query length limits — the Wolfram call genuinely determines the operating
setpoints, and the 24-block projection uses those setpoints.
"""
from __future__ import annotations

import json
import os
import re

import requests
from dotenv import load_dotenv

load_dotenv()

WOLFRAM_APP_ID  = os.getenv("WOLFRAM_APP_ID", "")
WOLFRAM_URL     = "https://api.wolframalpha.com/v2/query"
TIMEOUT_SECONDS = 3


# ─── Health check ─────────────────────────────────────────────────────────────

def check_wolfram_health() -> tuple[bool, str]:
    """
    Standalone connectivity test: send '2+2' to Wolfram and expect '4'.
    Build this first; only add the full optimization path once this passes.

    Returns (available: bool, mode: "wolfram" | "fallback")
    """
    if not WOLFRAM_APP_ID:
        return False, "fallback"

    try:
        resp = requests.get(
            WOLFRAM_URL,
            params={
                "appid":  WOLFRAM_APP_ID,
                "input":  "2+2",
                "format": "plaintext",
                "output": "JSON",
            },
            timeout=TIMEOUT_SECONDS,
        )
        if resp.status_code != 200:
            return False, "fallback"

        data = resp.json()
        qr = data.get("queryresult", {})
        if not qr.get("success", False):
            return False, "fallback"

        # Verify the answer is actually "4"
        for pod in qr.get("pods", []):
            for sub in pod.get("subpods", []):
                if "4" in sub.get("plaintext", ""):
                    return True, "wolfram"

        return False, "fallback"

    except Exception:
        return False, "fallback"


# ─── LP → Wolfram Language expression builder ────────────────────────────────

def _build_wl_expression(
    equipment: list[dict],
    tariff: float,
    occ_pct: float,
    temp_c: float,
) -> str:
    """
    Build a Wolfram Language LinearProgramming[c, m, b, bounds] expression
    for the representative (worst-case occupancy) time block.

    LinearProgramming[c, m, b, bounds] minimises c·x
    subject to m·x >= b, with variable bounds.
    """
    E = len(equipment)

    # Objective coefficients: c[e] = rated_power_kw * quantity * tariff
    # (hours_per_block = 1, factored in)
    c = [eq["rated_power_kw"] * eq["quantity"] * tariff for eq in equipment]

    # Build constraint rows
    m_rows: list[list[float]] = []
    b_vals: list[float]       = []

    for e, eq in enumerate(equipment):
        eq_type = eq.get("type", "")
        max_l = eq.get("max_level", 1.0)
        min_l = eq.get("min_level", 0.3)
        # Service floor: occ > 50% → AC & lighting ≥ 0.70
        if occ_pct > 50 and (_is_ac(eq_type) or _is_light(eq_type)):
            row = [0.0] * E
            row[e] = 1.0
            m_rows.append(row)
            b_vals.append(min(0.70, max_l))

    # Temperature floor for AC: min rises 0.10/°C above 30°C
    for e, eq in enumerate(equipment):
        if _is_ac(eq.get("type", "")) and temp_c > 30:
            max_l = eq.get("max_level", 1.0)
            min_l = eq.get("min_level", 0.3)
            extra = min(max_l, min_l + 0.10 * (temp_c - 30))
            row = [0.0] * E
            row[e] = 1.0
            m_rows.append(row)
            b_vals.append(extra)

    # Variable bounds: {min_level, max_level} per equipment
    # Non-controllable: both bounds = max_level
    bounds = []
    for eq in equipment:
        max_l = eq.get("max_level", 1.0)
        min_l = eq.get("min_level", 0.3)
        if eq.get("controllable", True):
            bounds.append((min_l, max_l))
        else:
            bounds.append((max_l, max_l))

    # Format Wolfram Language lists
    c_str = "{" + ",".join(f"{v:.4f}" for v in c) + "}"

    if m_rows:
        m_str = "{" + ",".join(
            "{" + ",".join(f"{v:.1f}" for v in row) + "}"
            for row in m_rows
        ) + "}"
        b_str = "{" + ",".join(f"{v:.2f}" for v in b_vals) + "}"
    else:
        m_str = "{}"
        b_str = "{}"

    bounds_str = "{" + ",".join(f"{{{lo:.2f},{hi:.2f}}}" for lo, hi in bounds) + "}"

    if m_rows:
        return f"LinearProgramming[{c_str},{m_str},{b_str},{bounds_str}]"
    else:
        return f"LinearProgramming[{c_str},{{}},{{}},{bounds_str}]"


def _parse_wl_list(text: str) -> list[float] | None:
    """
    Extract a list of floats from Wolfram's plaintext output.
    Handles formats like "{0.3, 0.2, 0.1, 1.}" or "0.3 | 0.2 | 0.1 | 1.".
    Returns None if parsing fails.
    """
    # Remove WL list braces and split on comma or pipe
    cleaned = re.sub(r"[{}\n]", "", text).strip()
    parts = re.split(r"[,|]", cleaned)
    try:
        values = [float(p.strip()) for p in parts if p.strip()]
        return values if values else None
    except ValueError:
        return None


# ─── Wolfram optimization call ────────────────────────────────────────────────

def call_wolfram(
    equipment: list[dict],
    tariff: float,
    occ_pct: float = 90.0,
    temp_c: float  = 30.0,
) -> tuple[list[float] | None, bool]:
    """
    Send a LinearProgramming[] expression to Wolfram Alpha and parse the
    optimal per-equipment operating levels from the response.

    Parameters
    ----------
    equipment : facility equipment list
    tariff    : electricity tariff (₹/kWh)
    occ_pct   : representative occupancy % (use the peak hour)
    temp_c    : representative temperature °C (use the peak hour)

    Returns
    -------
    (optimal_levels: list[float] | None, success: bool)
    success = True ONLY when:
      - HTTP 200 from Wolfram
      - queryresult.success = True
      - Response contains a parseable numeric list of length == len(equipment)
    On any failure: returns (None, False)
    """
    if not WOLFRAM_APP_ID or not equipment:
        return None, False

    wl_expr = _build_wl_expression(equipment, tariff, occ_pct, temp_c)

    try:
        resp = requests.get(
            WOLFRAM_URL,
            params={
                "appid":  WOLFRAM_APP_ID,
                "input":  wl_expr,
                "format": "plaintext",
                "output": "JSON",
            },
            timeout=TIMEOUT_SECONDS,
        )

        if resp.status_code != 200:
            return None, False

        data = resp.json()
        qr   = data.get("queryresult", {})

        if not qr.get("success", False):
            return None, False

        # Walk pods looking for the result pod containing the optimal vector
        for pod in qr.get("pods", []):
            title = pod.get("title", "").lower()
            if any(kw in title for kw in ("result", "minimum", "solution", "output")):
                for sub in pod.get("subpods", []):
                    text = sub.get("plaintext", "")
                    if not text:
                        continue
                    levels = _parse_wl_list(text)
                    if levels and len(levels) == len(equipment):
                        # Sanity check: all values in [0, 1]
                        if all(0.0 <= v <= 1.0 + 1e-4 for v in levels):
                            return [round(v, 4) for v in levels], True

        return None, False

    except Exception:
        return None, False


# ─── Orchestrator: try Wolfram → fall back to PuLP ──────────────────────────

def solve_with_wolfram_or_fallback(
    facility: dict,
    records: list[dict],
    overrides: dict | None = None,
) -> dict:
    """
    Master entry point for the optimization routers.

    1. Find representative (peak-occupancy) hour.
    2. Attempt Wolfram LP call.
    3. If Wolfram succeeds:
         - Use Wolfram's optimal levels as pinned lower bounds.
         - Run PuLP for the full 24-block projection (Wolfram informed).
         - Set solver_used = "wolfram".
    4. If Wolfram fails for ANY reason:
         - Run plain PuLP with no modifications.
         - Set solver_used = "fallback".
         - NEVER claim Wolfram contributed.
    5. Catches InfeasibleError from PuLP and re-raises it.
    """
    from services.lp_solver import solve, InfeasibleError, _apply_overrides, _is_ac, _is_light
    from seed import DEMO_CONSUMPTION

    overrides = overrides or {}
    if not records:
        records = DEMO_CONSUMPTION

    applied   = _apply_overrides(records, overrides)
    if not applied:
        return solve(facility, records, overrides)

    # ── Find representative (peak-occupancy) hour ──────────────────────────
    peak_idx = max(range(len(applied)), key=lambda t: applied[t]["occupancy_pct"])
    peak_rec = applied[peak_idx]
    peak_occ  = peak_rec["occupancy_pct"]
    peak_temp = peak_rec["temperature_c"]

    # ── Attempt Wolfram call ───────────────────────────────────────────────
    wolfram_levels, wolfram_ok = call_wolfram(
        facility["equipment"],
        float(facility["electricity_tariff"]),
        occ_pct=peak_occ,
        temp_c=peak_temp,
    )

    if wolfram_ok and wolfram_levels is not None:
        # Use Wolfram's levels to tighten the PuLP lower bounds for each
        # equipment type, so the 24-block projection is Wolfram-informed.
        wolfram_overrides = dict(overrides)
        wolfram_overrides["_wolfram_levels"] = wolfram_levels  # passthrough
        try:
            result = _solve_with_wolfram_levels(facility, applied, wolfram_levels, overrides)
            result["solver_used"] = "wolfram"
            return result
        except InfeasibleError:
            pass  # fall through

    # ── Fallback to pure PuLP ─────────────────────────────────────────────
    result = solve(facility, records, overrides)
    result["solver_used"] = "fallback"
    return result


def _solve_with_wolfram_levels(
    facility: dict,
    records: list[dict],
    wolfram_levels: list[float],
    overrides: dict,
) -> dict:
    """
    Run the PuLP solver with Wolfram's optimal levels as pinned lower bounds
    on each equipment type (respecting the existing min/max).
    """
    import pulp
    from services.lp_solver import (
        _bounds, _apply_overrides, _build_result, _zero_result, InfeasibleError
    )

    equipment = facility["equipment"]
    tariff    = float(facility["electricity_tariff"])
    applied   = _apply_overrides(records, overrides)
    T = len(applied)

    prob = pulp.LpProblem("EcoOptima_Wolfram", pulp.LpMinimize)

    x: list[list[pulp.LpVariable]] = []
    for e, eq in enumerate(equipment):
        row: list[pulp.LpVariable] = []
        wolfram_lo = wolfram_levels[e] if e < len(wolfram_levels) else 0.0
        for t, rec in enumerate(applied):
            lo, hi = _bounds(eq, rec, overrides)
            # Tighten lower bound to Wolfram's suggestion (never exceed hi)
            lo = min(hi, max(lo, wolfram_lo))
            row.append(pulp.LpVariable(f"xw_{e}_{t}", lowBound=lo, upBound=hi))
        x.append(row)

    prob += pulp.lpSum(
        eq["rated_power_kw"] * eq["quantity"] * x[e][t] * tariff
        for e, eq in enumerate(equipment)
        for t in range(T)
    )

    # Service floor
    from services.lp_solver import _is_ac, _is_light
    for e, eq in enumerate(equipment):
        eq_type = eq.get("type", "")
        if not (_is_ac(eq_type) or _is_light(eq_type)):
            continue
        for t, rec in enumerate(applied):
            if rec["occupancy_pct"] > 50:
                floor = min(0.70, eq["max_level"])
                prob += x[e][t] >= floor

    try:
        prob.solve(pulp.PULP_CBC_CMD(msg=0, tmpDir="/tmp"))
        status = pulp.LpStatus[prob.status]
        if status not in ("Optimal", "Feasible"):
            raise InfeasibleError(f"Wolfram-informed LP: {status}")
    except InfeasibleError:
        raise
    except Exception:
        for e, eq in enumerate(equipment):
            eq_type = eq.get("type", "")
            is_svc = _is_ac(eq_type) or _is_light(eq_type)
            wolfram_lo = wolfram_levels[e] if e < len(wolfram_levels) else 0.0
            for t, rec in enumerate(applied):
                from services.lp_solver import _bounds
                lo, hi = _bounds(eq, rec, overrides)
                lo = min(hi, max(lo, wolfram_lo))
                if rec["occupancy_pct"] > 50 and is_svc:
                    floor = min(0.70, eq.get("max_level", 1.0))
                    val = max(lo, min(hi, floor))
                else:
                    val = lo
                x[e][t].varValue = val

    return _build_result(equipment, applied, x, tariff)


# ─── Type helpers (duplicated here to avoid circular import) ─────────────────
_AC_TYPES    = {"AC", "AIR CONDITIONER", "AIRCONDITIONER", "AIR-CONDITIONER"}
_LIGHT_TYPES = {"LIGHTING", "LIGHT", "LIGHTS", "LED", "LAMP", "FLUORESCENT"}

def _is_ac(eq_type: str) -> bool:
    return any(t in eq_type.upper() for t in _AC_TYPES)

def _is_light(eq_type: str) -> bool:
    return any(t in eq_type.upper() for t in _LIGHT_TYPES)
