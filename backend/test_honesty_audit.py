import os
import services.wolfram_client as wc

print("=== 3. SOLVER HONESTY AUDIT ===")

# Test 1: Real health check
avail1, mode1 = wc.check_wolfram_health()
print(f"Live Key Health -> available: {avail1}, mode: {mode1}")

# Test 2: Break key
wc.WOLFRAM_APP_ID = "INVALID_KEY_999"
avail2, mode2 = wc.check_wolfram_health()
res, ok = wc.call_wolfram([{"type":"AC", "quantity":1, "rated_power_kw":1.0}], 8.5)

print(f"Broken Key Health -> available: {avail2}, mode: {mode2}")
print(f"Broken Key Optimization Call -> ok: {ok}")

if not avail2 and not ok and mode2 == "fallback":
    print("PASS: System cleanly & honestly falls back to PuLP when Wolfram key fails!")
else:
    print("FAIL: Fallback mechanism failed.")
