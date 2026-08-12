import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { optimize, getWolframHealth } from '../api/client'
import SolverBadge from '../components/SolverBadge'
import ModelEstimateTag from '../components/ModelEstimateTag'
import SavingsChart from '../components/SavingsChart'
import ScheduleTable from '../components/ScheduleTable'
import WhatIfPanel from '../components/WhatIfPanel'

export default function ResultScreen() {
  const navigate = useNavigate()
  const facilityId = sessionStorage.getItem('facilityId') || 'demo-1'
  const facility = JSON.parse(sessionStorage.getItem('facility') || '{}')

  const [result, setResult] = useState(null)
  const [wolframStatus, setWolframStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const load = async () => {
      try {
        const [optRes, healthRes] = await Promise.all([
          optimize(facilityId),
          getWolframHealth(),
        ])
        setResult(optRes.data)
        setWolframStatus(healthRes.data)
      } catch (err) {
        setError(err)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [facilityId])

  if (loading) {
    return (
      <div className="page" style={{ textAlign: 'center', paddingTop: '4rem' }}>
        <span className="spinner" style={{ width: 36, height: 36, borderWidth: 3 }} />
        <p style={{ color: 'var(--text-secondary)', marginTop: '1rem' }}>
          Running optimization engine…
        </p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page">
        <div className="error-box">
          <p className="error-box-title">⚠ {error.error || 'Optimization Error'}</p>
          <p className="error-box-msg">{error.message}</p>
          {error.suggestion && <p className="error-box-suggestion">{error.suggestion}</p>}
        </div>
        <button className="btn btn-ghost" onClick={() => navigate('/dashboard')}>← Back</button>
      </div>
    )
  }

  const { solver_used, baseline, optimized, savings, schedule } = result

  return (
    <div className="page">
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
        <div>
          <h1 className="page-title">Optimization Result</h1>
          <p className="page-subtitle">{facility.name || 'Facility'} · 30-day projection</p>
        </div>
        <SolverBadge solver={solver_used} />
      </div>

      {/* Wolfram status banner — only display when Wolfram is offline and fallback is active */}
      {wolframStatus && !wolframStatus.wolfram_available && solver_used === 'fallback' && (
        <div className="wolfram-banner down">
          🔧 Using local LP fallback solver — Wolfram API unavailable
        </div>
      )}

      {/* Bonus What-If interactive simulation panel */}
      <WhatIfPanel facilityId={facilityId} onUpdateResult={(newResult) => setResult(newResult)} />

      {/* Savings summary */}
      <div className="stat-grid" style={{ marginBottom: '1.5rem', marginTop: '1.5rem' }}>
        <div className="stat-card">
          <p className="stat-label">Energy Saved</p>
          <p className="stat-value" style={{ color: 'var(--accent-green)' }}>
            {savings.energy_reduction_pct}%
          </p>
          <p className="stat-unit">{(baseline.energy_kwh - optimized.energy_kwh).toFixed(0)} kWh / month</p>
          <ModelEstimateTag label="Optimization result" />
        </div>
        <div className="stat-card">
          <p className="stat-label">Cost Saving</p>
          <p className="stat-value" style={{ color: 'var(--accent-green)' }}>
            {savings.cost_saving_pct}%
          </p>
          <p className="stat-unit">₹{(baseline.cost_rupees - optimized.cost_rupees).toLocaleString()} / month</p>
          <ModelEstimateTag label="Optimization result" />
        </div>
        <div className="stat-card">
          <p className="stat-label">Water Saved</p>
          <p className="stat-value" style={{ color: 'var(--accent-blue)' }}>
            {baseline.water_liters > 0
              ? (((baseline.water_liters - optimized.water_liters) / baseline.water_liters) * 100).toFixed(1)
              : '0.0'}%
          </p>
          <p className="stat-unit">{(baseline.water_liters - optimized.water_liters).toLocaleString()} L / month</p>
          <ModelEstimateTag label="Optimization result" />
        </div>
      </div>

      {/* Savings chart */}
      <div className="card">
        <p className="card-title">📊 Baseline vs Optimized (30-day)</p>
        <SavingsChart baseline={baseline} optimized={optimized} />
        <ModelEstimateTag label="Model estimate — based on LP optimization" />
      </div>

      {/* Baseline vs Optimized details */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.25rem' }}>
        <div className="card">
          <p className="card-title" style={{ color: 'var(--accent-red)' }}>📉 Baseline</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div>
              <p style={{ fontSize: '1.2rem', fontWeight: 700 }}>{baseline.energy_kwh.toLocaleString()} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>kWh</span></p>
              <ModelEstimateTag />
            </div>
            <div>
              <p style={{ fontSize: '1.2rem', fontWeight: 700 }}>₹{baseline.cost_rupees.toLocaleString()}</p>
              <ModelEstimateTag />
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{baseline.water_liters.toLocaleString()} L water</p>
          </div>
        </div>
        <div className="card" style={{ borderColor: 'rgba(34,197,94,0.3)' }}>
          <p className="card-title" style={{ color: 'var(--accent-green)' }}>✅ Optimized</p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            <div>
              <p style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-green)' }}>{optimized.energy_kwh.toLocaleString()} <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>kWh</span></p>
              <ModelEstimateTag label="Optimization result" />
            </div>
            <div>
              <p style={{ fontSize: '1.2rem', fontWeight: 700, color: 'var(--accent-green)' }}>₹{optimized.cost_rupees.toLocaleString()}</p>
              <ModelEstimateTag label="Optimization result" />
            </div>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{optimized.water_liters.toLocaleString()} L water</p>
          </div>
        </div>
      </div>

      {/* Schedule */}
      <div className="card">
        <p className="card-title">🕙 Optimized Equipment Schedule</p>
        <ScheduleTable schedule={schedule} />
      </div>

      <div className="btn-row">
        <button className="btn btn-ghost" onClick={() => navigate('/dashboard')}>← Back to Dashboard</button>
        <button className="btn btn-ghost" onClick={() => navigate('/')}>↺ New Facility</button>
      </div>
    </div>
  )
}
