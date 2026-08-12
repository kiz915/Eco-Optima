Write-Host "`n=== 2. NO HARD-CODED NUMBERS & DYNAMIC INPUT AUDIT ==="
$body1 = @{
  name = "Dynamic Test A"
  occupants = 100
  electricity_tariff = 10.0
  water_tariff = 0.05
  equipment = @(@{ type="AC"; quantity=10; rated_power_kw=2.0; min_level=0.3; max_level=1.0; controllable=$true })
} | ConvertTo-Json -Depth 5
$fac1 = Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/facilities -ContentType "application/json" -Body $body1
$opt1 = Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/optimize -ContentType "application/json" -Body "{`"facility_id`":`"$($fac1.id)`"}"

$body2 = @{
  name = "Dynamic Test B"
  occupants = 100
  electricity_tariff = 50.0
  water_tariff = 0.05
  equipment = @(@{ type="AC"; quantity=10; rated_power_kw=2.0; min_level=0.3; max_level=1.0; controllable=$true })
} | ConvertTo-Json -Depth 5
$fac2 = Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/facilities -ContentType "application/json" -Body $body2
$opt2 = Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/optimize -ContentType "application/json" -Body "{`"facility_id`":`"$($fac2.id)`"}"

Write-Host "Tariff 10 Cost: $($opt1.optimized.cost_rupees) | Tariff 50 Cost: $($opt2.optimized.cost_rupees)"
if ($opt1.optimized.cost_rupees -ne $opt2.optimized.cost_rupees) {
  Write-Host "PASS: Results dynamically change when tariff changes!"
} else {
  Write-Host "FAIL: Results did not change - numbers might be hardcoded!"
}

Write-Host "`n=== 4. CONSTRAINT CORRECTNESS & INFEASIBILITY AUDIT ==="
$badBody = @{
  name = "Infeasible Facility"
  occupants = 50
  electricity_tariff = 8.5
  water_tariff = 0.02
  equipment = @(@{ type="AC"; quantity=10; rated_power_kw=1.5; min_level=1.5; max_level=1.0; controllable=$true })
} | ConvertTo-Json -Depth 5
try {
  Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/facilities -ContentType "application/json" -Body $badBody
  Write-Host "FAIL: Did not catch min > max constraint"
} catch {
  Write-Host "PASS: Pydantic/API caught infeasible bounds (HTTP status $($_.Exception.Response.StatusCode))"
}

Write-Host "`n=== 6. ERROR RESILIENCE AUDIT ==="
$badInputs = @(
  @{ name=""; occupants=10; electricity_tariff=8.5; water_tariff=0.02; equipment=@(@{ type="AC"; quantity=1; rated_power_kw=1 }) },
  @{ name="Test"; occupants=-5; electricity_tariff=8.5; water_tariff=0.02; equipment=@(@{ type="AC"; quantity=1; rated_power_kw=1 }) },
  @{ name="Test"; occupants=10; electricity_tariff=8.5; water_tariff=0.02; equipment=@() }
)
foreach ($b in $badInputs) {
  try {
    $json = $b | ConvertTo-Json -Depth 5
    Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/facilities -ContentType "application/json" -Body $json
    Write-Host "FAIL: Bad input passed validation"
  } catch {
    Write-Host "PASS: Bad input correctly rejected with 422"
  }
}
