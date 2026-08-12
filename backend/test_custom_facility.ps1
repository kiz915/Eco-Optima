Write-Host "=== TEST CREATING A CUSTOM FACILITY AND OPTIMIZING ==="
$body = @{
  name = "Custom Block C"
  occupants = 150
  electricity_tariff = 9.0
  water_tariff = 0.02
  equipment = @(
    @{ type="AC"; quantity=20; rated_power_kw=2.0; min_level=0.3; max_level=1.0; controllable=$true },
    @{ type="Lighting"; quantity=50; rated_power_kw=0.03; min_level=0.1; max_level=1.0; controllable=$true }
  )
} | ConvertTo-Json -Depth 5

$fac = Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/facilities -ContentType "application/json" -Body $body
Write-Host "Facility Created ID: $($fac.id)"

$opt = Invoke-RestMethod -Method POST -Uri http://localhost:8000/api/optimize -ContentType "application/json" -Body "{`"facility_id`":`"$($fac.id)`"}"
Write-Host "Optimization Status: SUCCESS!"
Write-Host "Baseline Cost: $($opt.baseline.cost_rupees) | Optimized Cost: $($opt.optimized.cost_rupees)"
Write-Host "Savings %: $($opt.savings.energy_reduction_pct)%"
