import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { createFacility, getDemoFacility } from '../api/client'

const DEFAULT_EQUIPMENT_ROW = {
  type: '',
  quantity: 1,
  rated_power_kw: 1.0,
  min_level: 0.3,
  max_level: 1.0,
  controllable: true,
}

export default function InputScreen() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [demoLoading, setDemoLoading] = useState(false)
  const [error, setError] = useState(null)
  
  const [form, setForm] = useState({
    name: '',
    occupants: '',
    electricity_tariff: '',
    water_tariff: '',
  })

  const [equipment, setEquipment] = useState([
    { type: 'AC', quantity: 30, rated_power_kw: 1.5, min_level: 0.3, max_level: 1.0, controllable: true },
    { type: 'Lighting', quantity: 80, rated_power_kw: 0.02, min_level: 0.1, max_level: 1.0, controllable: true }
  ])

  const setFormField = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const handleEquipmentChange = (index, field, value) => {
    setEquipment((prev) => {
      const next = [...prev]
      next[index] = { ...next[index], [field]: value }
      return next
    })
  }

  const addEquipmentRow = () => {
    setEquipment((prev) => [...prev, { ...DEFAULT_EQUIPMENT_ROW }])
  }

  const removeEquipmentRow = (index) => {
    if (equipment.length <= 1) return
    setEquipment((prev) => prev.filter((_, i) => i !== index))
  }

  const handleDemo = async () => {
    setDemoLoading(true)
    setError(null)
    try {
      const res = await getDemoFacility()
      sessionStorage.setItem('facilityId', res.data.id)
      sessionStorage.setItem('facility', JSON.stringify(res.data))
      navigate('/dashboard')
    } catch (err) {
      setError(err)
    } finally {
      setDemoLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      const body = {
        name: form.name,
        occupants: Number(form.occupants),
        electricity_tariff: Number(form.electricity_tariff),
        water_tariff: Number(form.water_tariff),
        equipment: equipment.map((eq) => ({
          ...eq,
          quantity: Number(eq.quantity),
          rated_power_kw: Number(eq.rated_power_kw),
          min_level: Number(eq.min_level),
          max_level: Number(eq.max_level),
        })),
      }
      const res = await createFacility(body)
      sessionStorage.setItem('facilityId', res.data.id)
      sessionStorage.setItem('facility', JSON.stringify(res.data))
      navigate('/dashboard')
    } catch (err) {
      setError(err)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="page">
      <h1 className="page-title">Facility Input</h1>
      <p className="page-subtitle">
        Enter building details & equipment list to run resource optimization analysis.
      </p>

      {error && (
        <div className="error-box">
          <p className="error-box-title">⚠ {error.error || 'Validation Error'}</p>
          <p className="error-box-msg">{error.message}</p>
          {error.suggestion && <p className="error-box-suggestion">{error.suggestion}</p>}
        </div>
      )}

      <div className="card">
        <p className="card-title">🏢 Building Details</p>
        <form onSubmit={handleSubmit}>
          <div className="form-grid">
            <div className="form-group full">
              <label>Facility Name</label>
              <input
                id="facility-name"
                placeholder="e.g. Hostel Block A"
                value={form.name}
                onChange={setFormField('name')}
                required
              />
            </div>
            <div className="form-group">
              <label>Occupants</label>
              <input
                id="facility-occupants"
                type="number"
                placeholder="100"
                value={form.occupants}
                onChange={setFormField('occupants')}
                required
                min="1"
              />
            </div>
            <div className="form-group">
              <label>Electricity Tariff (₹/kWh)</label>
              <input
                id="facility-elec-tariff"
                type="number"
                step="0.01"
                placeholder="8.5"
                value={form.electricity_tariff}
                onChange={setFormField('electricity_tariff')}
                required
                min="0.01"
              />
            </div>
            <div className="form-group">
              <label>Water Tariff (₹/L)</label>
              <input
                id="facility-water-tariff"
                type="number"
                step="0.001"
                placeholder="0.02"
                value={form.water_tariff}
                onChange={setFormField('water_tariff')}
                required
                min="0.001"
              />
            </div>
          </div>

          <div style={{ marginTop: '1.5rem' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
              <p className="card-title" style={{ margin: 0 }}>⚡ Equipment Inventory</p>
              <button
                type="button"
                className="btn btn-ghost"
                style={{ padding: '4px 10px', fontSize: '0.8rem' }}
                onClick={addEquipmentRow}
              >
                + Add Equipment Row
              </button>
            </div>

            <div style={{ overflowX: 'auto', paddingBottom: '4px' }}>
              <div style={{ minWidth: '640px' }}>
                {/* Column Headers */}
                <div
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '2fr 1fr 1fr 1fr 1fr 0.8fr 30px',
                    gap: '8px',
                    padding: '0 8px 6px 8px',
                    fontSize: '0.72rem',
                    fontWeight: '700',
                    color: 'var(--text-muted)',
                    textTransform: 'uppercase',
                    letterSpacing: '0.04em',
                  }}
                >
                  <div>Type</div>
                  <div>Qty</div>
                  <div>kW/Unit</div>
                  <div>Min (0-1)</div>
                  <div>Max (0-1)</div>
                  <div style={{ textAlign: 'center' }}>Ctrl</div>
                  <div></div>
                </div>

                {equipment.map((row, idx) => (
                  <div
                    key={idx}
                    style={{
                      display: 'grid',
                      gridTemplateColumns: '2fr 1fr 1fr 1fr 1fr 0.8fr 30px',
                      gap: '8px',
                      alignItems: 'center',
                      marginBottom: '8px',
                      background: 'rgba(0,0,0,0.2)',
                      padding: '6px 8px',
                      borderRadius: '6px',
                    }}
                  >
                    <div style={{ minWidth: 0 }}>
                      <input
                        placeholder="e.g. AC"
                        value={row.type}
                        onChange={(e) => handleEquipmentChange(idx, 'type', e.target.value)}
                        style={{ width: '100%', padding: '8px 10px', fontSize: '0.85rem' }}
                        required
                      />
                    </div>
                    <div style={{ minWidth: 0 }}>
                      <input
                        type="number"
                        placeholder="30"
                        value={row.quantity}
                        onChange={(e) => handleEquipmentChange(idx, 'quantity', e.target.value)}
                        style={{ width: '100%', padding: '8px 10px', fontSize: '0.85rem' }}
                        required
                        min="1"
                      />
                    </div>
                    <div style={{ minWidth: 0 }}>
                      <input
                        type="number"
                        step="any"
                        placeholder="1.5"
                        value={row.rated_power_kw}
                        onChange={(e) => handleEquipmentChange(idx, 'rated_power_kw', e.target.value)}
                        style={{ width: '100%', padding: '8px 10px', fontSize: '0.85rem' }}
                        required
                        min="0.0001"
                      />
                    </div>
                    <div style={{ minWidth: 0 }}>
                      <input
                        type="number"
                        step="any"
                        placeholder="0.3"
                        value={row.min_level}
                        onChange={(e) => handleEquipmentChange(idx, 'min_level', e.target.value)}
                        style={{ width: '100%', padding: '8px 10px', fontSize: '0.85rem' }}
                        required
                        min="0"
                        max="1"
                      />
                    </div>
                    <div style={{ minWidth: 0 }}>
                      <input
                        type="number"
                        step="any"
                        placeholder="1.0"
                        value={row.max_level}
                        onChange={(e) => handleEquipmentChange(idx, 'max_level', e.target.value)}
                        style={{ width: '100%', padding: '8px 10px', fontSize: '0.85rem' }}
                        required
                        min="0"
                        max="1"
                      />
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                      <input
                        type="checkbox"
                        checked={row.controllable}
                        onChange={(e) => handleEquipmentChange(idx, 'controllable', e.target.checked)}
                        style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                        title="Is controllable by optimizer?"
                      />
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'center' }}>
                      {equipment.length > 1 && (
                        <button
                          type="button"
                          onClick={() => removeEquipmentRow(idx)}
                          style={{
                            background: 'transparent',
                            border: 'none',
                            color: 'var(--accent-red)',
                            cursor: 'pointer',
                            fontWeight: 'bold',
                            fontSize: '1rem',
                            padding: '4px',
                          }}
                          title="Remove row"
                        >
                          ✕
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="btn-row">
            <button id="btn-submit-facility" type="submit" className="btn btn-primary" disabled={loading}>
              {loading ? <><span className="spinner" /> Saving…</> : '→ Submit & Analyze'}
            </button>
            <button
              id="btn-use-demo"
              type="button"
              className="btn btn-ghost"
              onClick={handleDemo}
              disabled={demoLoading}
            >
              {demoLoading ? <><span className="spinner" /> Loading Demo…</> : '⚡ Use Demo Facility'}
            </button>
          </div>
        </form>
      </div>

      <div className="card" style={{ borderStyle: 'dashed', opacity: 0.7 }}>
        <p className="card-title" style={{ marginBottom: '0.5rem' }}>💡 Live Pitch Quick-Path</p>
        <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
          Click <strong>"Use Demo Facility"</strong> to instantly load <strong>Hostel Block A</strong> 
          (30 ACs, 40 Fans, 80 Lights, 2 Pumps) with pre-seeded 24h consumption telemetry.
        </p>
      </div>
    </div>
  )
}
