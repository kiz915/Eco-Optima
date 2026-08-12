export interface Equipment {
  type: string
  quantity: number
  rated_power_kw: number
  min_level: number
  max_level: number
  controllable: boolean
}

export interface FacilityCreate {
  name: string
  occupants: number
  electricity_tariff: number
  water_tariff: number
  equipment: Equipment[]
}

export interface FacilityResponse extends FacilityCreate {
  id: string
}

export interface ConsumptionRecord {
  timestamp: string
  occupancy_pct: number
  temperature_c: number
  energy_kwh: number
  water_liters: number
}

export interface ConsumptionResponse {
  records: ConsumptionRecord[]
}

export interface WasteIssue {
  title: string
  severity: 'high' | 'medium' | 'low'
  evidence: string
  estimated_impact_kwh: number
  recommendation: string
}

export interface WasteDetectionResponse {
  issues: WasteIssue[]
}

export interface ResourceSummary {
  energy_kwh: number
  cost_rupees: number
  water_liters: number
}

export interface Savings {
  energy_reduction_pct: number
  cost_saving_pct: number
}

export interface ScheduleEntry {
  time: string
  equipment: string
  current_level: number
  optimized_level: number
}

export interface OptimizeResponse {
  solver_used: 'wolfram' | 'fallback'
  baseline: ResourceSummary
  optimized: ResourceSummary
  savings: Savings
  schedule: ScheduleEntry[]
}

export interface SimulateRequest {
  facility_id: string
  occupancy_pct?: number
  temperature_c?: number
  ac_operating_level?: number
}

export interface HealthResponse {
  status: string
}

export interface WolframHealthResponse {
  wolfram_available: boolean
  mode: 'wolfram' | 'fallback'
  note?: string
}

export interface ApiError {
  error: string
  message: string
  suggestion?: string
}
