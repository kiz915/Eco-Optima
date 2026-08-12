import axios, { AxiosResponse } from 'axios'
import {
  FacilityCreate,
  FacilityResponse,
  ConsumptionResponse,
  WasteDetectionResponse,
  OptimizeResponse,
  SimulateRequest,
  HealthResponse,
  WolframHealthResponse,
  ApiError,
} from '../services/api'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

api.interceptors.response.use(
  (res) => res,
  (err) => {
    const detail = err.response?.data?.detail
    if (detail && typeof detail === 'object') {
      return Promise.reject(detail as ApiError)
    }
    return Promise.reject({
      error: 'network_error',
      message: err.message || 'Request failed',
      suggestion: 'Check that the backend server is running on port 8000.',
    } as ApiError)
  }
)

export const getHealth = (): Promise<AxiosResponse<HealthResponse>> =>
  api.get('/health')

export const getWolframHealth = (): Promise<AxiosResponse<WolframHealthResponse>> =>
  api.get('/health/wolfram')

export const getDemoFacility = (): Promise<AxiosResponse<FacilityResponse>> =>
  api.get('/demo/facility')

export const getDemoConsumption = (): Promise<AxiosResponse<ConsumptionResponse>> =>
  api.get('/demo/consumption')

export const createFacility = (
  data: FacilityCreate
): Promise<AxiosResponse<FacilityResponse>> => api.post('/facilities', data)

export const getFacility = (
  id: string
): Promise<AxiosResponse<FacilityResponse>> => api.get(`/facilities/${id}`)

export const detectWaste = (
  facility_id: string
): Promise<AxiosResponse<WasteDetectionResponse>> =>
  api.post('/waste-detection', { facility_id })

export const optimize = (
  facility_id: string
): Promise<AxiosResponse<OptimizeResponse>> =>
  api.post('/optimize', { facility_id })

export const simulate = (
  req: SimulateRequest
): Promise<AxiosResponse<OptimizeResponse>> => api.post('/simulate', req)

export default api
