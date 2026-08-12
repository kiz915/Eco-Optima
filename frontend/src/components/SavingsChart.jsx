import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts'

const COLORS = { baseline: '#ef4444', optimized: '#22c55e' }

export default function SavingsChart({ baseline, optimized }) {
  const data = [
    {
      name: 'Energy (kWh)',
      Baseline: baseline.energy_kwh,
      Optimized: optimized.energy_kwh,
    },
    {
      name: 'Cost (₹ / 100)',
      Baseline: Math.round(baseline.cost_rupees / 100),
      Optimized: Math.round(optimized.cost_rupees / 100),
    },
    {
      name: 'Water (L / 100)',
      Baseline: Math.round(baseline.water_liters / 100),
      Optimized: Math.round(optimized.water_liters / 100),
    },
  ]

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
        <XAxis dataKey="name" tick={{ fill: '#8b949e', fontSize: 12 }} />
        <YAxis tick={{ fill: '#8b949e', fontSize: 12 }} />
        <Tooltip
          contentStyle={{ background: '#161b22', border: '1px solid #30363d', borderRadius: 8 }}
          labelStyle={{ color: '#e6edf3' }}
        />
        <Legend wrapperStyle={{ color: '#8b949e', fontSize: 12 }} />
        <Bar dataKey="Baseline" fill={COLORS.baseline} radius={[4, 4, 0, 0]} />
        <Bar dataKey="Optimized" fill={COLORS.optimized} radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}
