import { useState, useEffect } from 'react'
import * as Sentry from '@sentry/react'
import { simulate } from '../api/client'
import ModelEstimateTag from './ModelEstimateTag'

export default function WhatIfPanel({ facilityId, onUpdateResult }) {
  const [occupancy, setOccupancy] = useState(70)
  const [temperature, setTemperature] = useState(30)
  const [acLevel, setAcLevel] = useState(0.8)
  const [simulating, setSimulating] = useState(false)
  const [simError, setSimError] = useState(null)

  // Debounced simulation API call (~300ms)
  useEffect(() => {
    const timer = setTimeout(async () => {
      setSimulating(true)
      setSimError(null)
      try {
        const res = await simulate({
          facility_id: facilityId,
          occupancy_pct: Number(occupancy),
          temperature_c: Number(temperature),
          ac_operating_level: Number(acLevel),
        })
        onUpdateResult(res.data)
      } catch (err) {
        console.error('Simulation error:', err)
        setSimError(err)
        Sentry.captureException(err, {
          tags: { component: 'WhatIfPanel', facilityId },
          extra: { occupancy, temperature, acLevel },
        })
      } finally {
        setSimulating(false)
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [occupancy, temperature, acLevel, facilityId])


  return (
    <div className="card" style={{ borderColor: 'rgba(59, 130, 246, 0.4)', background: 'rgba(15, 23, 42, 0.6)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <p className="card-title" style={{ margin: 0, color: 'var(--accent-blue)' }}>
          🎛 What-If Interactive Simulation
        </p>
        {simulating && (
          <span style={{ fontSize: '0.78rem', color: 'var(--accent-amber)', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <span className="spinner" style={{ width: 12, height: 12 }} /> Calculating…
          </span>
        )}
      </div>

      <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1.25rem' }}>
        Adjust parameters live to simulate real-time load changes and test optimizer responsiveness.
      </p>

      {simError && (
        <div className="error-box" style={{ marginBottom: '1rem' }}>
          <p className="error-box-title">⚠ {simError.error || 'Simulation Error'}</p>
          <p className="error-box-msg">{simError.message || 'The specified parameters created an infeasible constraint state.'}</p>
          {simError.suggestion && <p className="error-box-suggestion">{simError.suggestion}</p>}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1.25rem' }}>
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '4px' }}>
            <label style={{ textTransform: 'none', color: 'var(--text-primary)' }}>Occupancy Rate</label>
            <span style={{ fontWeight: 700, color: 'var(--accent-blue)' }}>{occupancy}%</span>
          </div>
          <input
            type="range"
            min="10"
            max="100"
            step="5"
            value={occupancy}
            onChange={(e) => setOccupancy(e.target.value)}
            style={{ width: '100%', cursor: 'pointer' }}
          />
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '4px' }}>
            <label style={{ textTransform: 'none', color: 'var(--text-primary)' }}>Ambient Temp</label>
            <span style={{ fontWeight: 700, color: 'var(--accent-amber)' }}>{temperature}°C</span>
          </div>
          <input
            type="range"
            min="20"
            max="42"
            step="1"
            value={temperature}
            onChange={(e) => setTemperature(e.target.value)}
            style={{ width: '100%', cursor: 'pointer' }}
          />
        </div>

        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.82rem', marginBottom: '4px' }}>
            <label style={{ textTransform: 'none', color: 'var(--text-primary)' }}>AC Target Setpoint</label>
            <span style={{ fontWeight: 700, color: 'var(--accent-green)' }}>{Math.round(acLevel * 100)}%</span>
          </div>
          <input
            type="range"
            min="0.3"
            max="1.0"
            step="0.05"
            value={acLevel}
            onChange={(e) => setAcLevel(e.target.value)}
            style={{ width: '100%', cursor: 'pointer' }}
          />
        </div>
      </div>

      <ModelEstimateTag label="What-If simulation — dynamically calls /api/simulate" />
    </div>
  )
}
