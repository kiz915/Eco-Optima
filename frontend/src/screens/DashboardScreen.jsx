import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'
import { getDemoConsumption, detectWaste } from '../api/client'
import WasteCard from '../components/WasteCard'

export default function DashboardScreen() {
  const navigate = useNavigate()
  const facilityId = sessionStorage.getItem('facilityId') || 'demo-1'
  const facility = JSON.parse(sessionStorage.getItem('facility') || '{}')

  const [consumption, setConsumption] = useState([])
  const [issues, setIssues] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const load = async () => {
      try {
        const [consRes, wasteRes] = await Promise.all([
          getDemoConsumption(),
          detectWaste(facilityId),
        ])
        // Format timestamps to HH:MM for chart
        setConsumption(
          consRes.data.records.map((r) => ({
            ...r,
            hour: r.timestamp.split('T')[1].slice(0, 5),
          }))
        )
        setIssues(wasteRes.data.issues)
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
        <p style={{ color: 'var(--text-secondary)', marginTop: '1rem' }}>Loading facility data…</p>
      </div>
    )
  }

  const highCount = issues.filter((i) => i.severity === 'high').length
  const totalImpact = issues.reduce((s, i) => s + i.estimated_impact_kwh, 0)

  return (
    <div className="page">
      <h1 className="page-title">Dashboard</h1>
      <p className="page-subtitle">
        {facility.name || 'Facility'} · {facility.occupants || '—'} occupants ·
        ₹{facility.electricity_tariff || '—'}/kWh
      </p>

      {error && (
        <div className="error-box">
          <p className="error-box-title">⚠ {error.error || 'Error'}</p>
          <p className="error-box-msg">{error.message}</p>
        </div>
      )}

      {/* Summary Stats */}
      <div className="stat-grid" style={{ marginBottom: '1.5rem' }}>
        <div className="stat-card">
          <p className="stat-label">Waste Issues</p>
          <p className="stat-value" style={{ color: highCount > 0 ? 'var(--accent-red)' : 'var(--accent-green)' }}>
            {issues.length}
          </p>
          <p className="stat-unit">{highCount} high severity</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">Est. Wasted Energy</p>
          <p className="stat-value">{totalImpact.toFixed(0)}</p>
          <p className="stat-unit">kWh recoverable</p>
        </div>
        <div className="stat-card">
          <p className="stat-label">Peak Consumption</p>
          <p className="stat-value">{consumption.length ? Math.max(...consumption.map(r => r.energy_kwh)).toFixed(1) : '—'}</p>
          <p className="stat-unit">kWh/hr peak</p>
        </div>
      </div>

      {/* Consumption Chart */}
      <div className="card">
        <p className="card-title">📈 24-Hour Energy & Occupancy</p>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={consumption} margin={{ top: 5, right: 20, left: 0, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
            <XAxis dataKey="hour" tick={{ fill: '#8b949e', fontSize: 11 }} interval={3} />
            <YAxis yAxisId="energy" tick={{ fill: '#8b949e', fontSize: 11 }} />
            <YAxis yAxisId="occ" orientation="right" tick={{ fill: '#8b949e', fontSize: 11 }} />
            <Tooltip
              contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8 }}
              labelStyle={{ color: '#e6edf3' }}
            />
            <Legend wrapperStyle={{ color: '#8b949e', fontSize: 12 }} />
            <Line
              yAxisId="energy"
              type="monotone"
              dataKey="energy_kwh"
              name="Energy (kWh)"
              stroke="#22c55e"
              strokeWidth={2}
              dot={false}
            />
            <Line
              yAxisId="occ"
              type="monotone"
              dataKey="occupancy_pct"
              name="Occupancy (%)"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={false}
              strokeDasharray="5 3"
            />
          </LineChart>
        </ResponsiveContainer>
        <p className="estimate-tag" style={{ textAlign: 'right', marginTop: 8 }}>※ Model estimate — synthetic 24-hour data</p>
      </div>

      {/* Waste Issues */}
      <div className="card">
        <p className="card-title">⚠ Detected Waste Patterns</p>
        {issues.length === 0 ? (
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>No waste patterns detected. Facility looks efficient!</p>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {issues.map((issue, i) => <WasteCard key={i} issue={issue} />)}
          </div>
        )}
      </div>

      <div className="btn-row">
        <button
          id="btn-optimize"
          className="btn btn-primary"
          onClick={() => navigate('/results')}
        >
          ⚡ Optimize Now →
        </button>
        <button
          className="btn btn-ghost"
          onClick={() => navigate('/')}
        >
          ← Back to Input
        </button>
      </div>
    </div>
  )
}
