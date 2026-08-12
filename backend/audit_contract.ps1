Write-Host "=== 1. CONTRACT COMPLIANCE AUDIT ==="
$endpoints = @(
  @{ Uri = "http://localhost:8000/api/health"; Method = "GET" },
  @{ Uri = "http://localhost:8000/api/health/wolfram"; Method = "GET" },
  @{ Uri = "http://localhost:8000/api/demo/facility"; Method = "GET" },
  @{ Uri = "http://localhost:8000/api/demo/consumption"; Method = "GET" },
  @{ Uri = "http://localhost:8000/api/waste-detection"; Method = "POST"; Body = '{"facility_id":"demo-1"}' },
  @{ Uri = "http://localhost:8000/api/optimize"; Method = "POST"; Body = '{"facility_id":"demo-1"}' },
  @{ Uri = "http://localhost:8000/api/simulate"; Method = "POST"; Body = '{"facility_id":"demo-1", "occupancy_pct":50}' }
)

foreach ($ep in $endpoints) {
  try {
    if ($ep.Method -eq "GET") {
      $res = Invoke-RestMethod -Uri $ep.Uri
    } else {
      $res = Invoke-RestMethod -Uri $ep.Uri -Method POST -ContentType "application/json" -Body $ep.Body
    }
    Write-Host "PASS: $($ep.Method) $($ep.Uri)"
  } catch {
    Write-Host "FAIL: $($ep.Method) $($ep.Uri) - $($_.Exception.Message)"
  }
}
