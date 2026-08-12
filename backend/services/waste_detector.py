"""
Rule-based waste detection against the real consumption dataset.

Exactly 3 rules, each using actual numbers computed from the records —
no placeholder text.  The three rules match the three injected
inefficiencies in seed.py so the evidence is always checkable.
"""
from models import WasteIssue


def detect_waste(records: list[dict]) -> list[WasteIssue]:
    """
    Analyse consumption records and return up to 3 WasteIssue objects.
    Evidence strings contain real numbers computed from `records`.
    """
    if not records:
        return []

    issues: list[WasteIssue] = []
    all_energy = [r["energy_kwh"] for r in records]
    daily_peak = max(all_energy)

    # ── Rule 1: Low occupancy + high energy ──────────────────────────────────
    # Condition: occupancy < 30 % AND energy > 70 % of daily peak.
    # Catches Injected Inefficiency A (AC full 11pm–5am).
    threshold_70pct = 0.70 * daily_peak
    low_occ_hi_nrg = [
        r for r in records
        if r["occupancy_pct"] < 30 and r["energy_kwh"] > threshold_70pct
    ]
    if low_occ_hi_nrg:
        avg_occ   = round(sum(r["occupancy_pct"] for r in low_occ_hi_nrg) / len(low_occ_hi_nrg), 1)
        avg_nrg   = round(sum(r["energy_kwh"]    for r in low_occ_hi_nrg) / len(low_occ_hi_nrg), 1)
        avg_pct   = round(avg_nrg / daily_peak * 100, 1)
        # Counterfactual: if AC stepped to 30 % (min_level) those hours,
        # AC load drops from ~90 % to ~30 % of 45 kW → saves ~27 kW/hr.
        ac_full_kw   = 30 * 1.5          # 45 kW installed
        ac_waste_kw  = round(ac_full_kw * (0.90 - 0.30), 1)   # ~27 kW
        impact_kwh   = round(ac_waste_kw * len(low_occ_hi_nrg), 1)
        timestamps   = ", ".join(r["timestamp"].split("T")[1][:5] for r in low_occ_hi_nrg)

        issues.append(WasteIssue(
            title="AC running at full power during low occupancy",
            severity="high",
            evidence=(
                f"{len(low_occ_hi_nrg)} hours ({timestamps}) had occupancy avg {avg_occ} % "
                f"but energy avg {avg_nrg} kWh/hr — {avg_pct} % of the daily peak "
                f"({daily_peak} kWh/hr). AC appears stuck at ≥85 % capacity."
            ),
            estimated_impact_kwh=impact_kwh,
            recommendation=(
                "Configure BMS setback schedule: step AC to ≤30 % operating level "
                "between 23:00 and 05:00.  Estimated monthly saving: "
                f"{round(impact_kwh * 30, 0):.0f} kWh "
                f"(₹{round(impact_kwh * 30 * 8.5, 0):.0f} at ₹8.5/kWh)."
            ),
        ))

    # ── Rule 2: Elevated nighttime load (23:00–05:00) ────────────────────────
    # Catches Injected Inefficiency B (no setback mode → baseline too high).
    night_hours = {23, 0, 1, 2, 3, 4}
    night_recs = [
        r for r in records
        if int(r["timestamp"].split("T")[1][:2]) in night_hours
    ]
    if night_recs:
        avg_night   = round(sum(r["energy_kwh"] for r in night_recs) / len(night_recs), 1)
        # Expected setback baseline: pumps (7.4 kW) + 15 % lights (0.24 kW)
        # + AC at 30 % (13.5 kW) + fans at 5 % (0.15 kW) ≈ 21.3 kW
        expected_baseline = round(7.4 + 0.24 + 30 * 1.5 * 0.30 + 40 * 0.075 * 0.05, 1)
        excess_per_hr     = round(max(0, avg_night - expected_baseline), 1)
        impact_kwh        = round(excess_per_hr * len(night_recs), 1)
        night_labels = ", ".join(r["timestamp"].split("T")[1][:5] for r in night_recs)

        if excess_per_hr > 1:    # only flag if meaningful excess
            issues.append(WasteIssue(
                title="Nighttime energy well above setback baseline",
                severity="high",
                evidence=(
                    f"Hours {night_labels}: avg {avg_night} kWh/hr. "
                    f"Expected setback baseline is ≈{expected_baseline} kWh/hr "
                    f"(pumps + minimal lighting + AC at 30 %). "
                    f"Excess: {excess_per_hr} kWh/hr — likely no BMS setback configured."
                ),
                estimated_impact_kwh=impact_kwh,
                recommendation=(
                    "Enable BMS night-setback mode (23:00–05:00): "
                    "AC → 30 %, fans off, lighting → 15 % in common areas only. "
                    f"Recoverable: ≈{round(impact_kwh * 30, 0):.0f} kWh/month."
                ),
            ))

    # ── Rule 3: Irrigation timer misaligned with occupancy ───────────────────
    # Catches Injected Inefficiency C (450 L dump at 02:00, lowest occupancy).
    # Condition: water_liters > 2× the median water reading AND occupancy < 15 %.
    median_water = sorted(r["water_liters"] for r in records)[len(records) // 2]
    water_anomalies = [
        r for r in records
        if r["water_liters"] > 2.0 * median_water and r["occupancy_pct"] < 15
    ]
    if water_anomalies:
        worst = max(water_anomalies, key=lambda r: r["water_liters"])
        hour  = worst["timestamp"].split("T")[1][:5]
        water_L   = worst["water_liters"]
        occ_at    = worst["occupancy_pct"]
        # Cost estimate
        excess_L  = round(water_L - median_water, 1)
        cost_day  = round(excess_L * 0.02, 2)     # ₹0.02/L

        issues.append(WasteIssue(
            title="Automated irrigation firing during lowest-occupancy window",
            severity="medium",
            evidence=(
                f"At {hour} (occupancy {occ_at} %) water consumption spiked to "
                f"{water_L} L — {round(water_L / median_water, 1)}× the hourly median "
                f"({median_water} L).  Pattern consistent with a fixed irrigation "
                f"timer, not occupancy-demand."
            ),
            estimated_impact_kwh=0.0,
            recommendation=(
                f"Reschedule irrigation to 05:30–06:00 (pre-occupancy, cooler temp). "
                f"Excess water per day: ≈{excess_L} L (₹{cost_day}/day, "
                f"₹{round(cost_day*365, 0):.0f}/yr at ₹0.02/L)."
            ),
        ))

    return issues
