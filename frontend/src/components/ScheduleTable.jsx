import ModelEstimateTag from './ModelEstimateTag'

export default function ScheduleTable({ schedule }) {
  if (!schedule || schedule.length === 0) {
    return <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>No schedule adjustments needed.</p>
  }

  return (
    <div style={{ overflowX: 'auto' }}>
      <table className="schedule-table">
        <thead>
          <tr>
            <th>Time</th>
            <th>Equipment</th>
            <th>Current Level</th>
            <th>Optimized Level</th>
            <th>Change</th>
          </tr>
        </thead>
        <tbody>
          {schedule.map((row, i) => {
            const reduction = Math.round((row.current_level - row.optimized_level) / row.current_level * 100)
            return (
              <tr key={i}>
                <td style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{row.time}</td>
                <td style={{ color: 'var(--text-primary)' }}>{row.equipment}</td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div className="level-bar-bg">
                      <div className="level-bar old" style={{ width: `${row.current_level * 100}%` }} />
                    </div>
                    <span>{Math.round(row.current_level * 100)}%</span>
                  </div>
                  <ModelEstimateTag label="Optimization result" />
                </td>
                <td>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                    <div className="level-bar-bg">
                      <div className="level-bar" style={{ width: `${row.optimized_level * 100}%` }} />
                    </div>
                    <span style={{ color: 'var(--accent-green)', fontWeight: 600 }}>
                      {Math.round(row.optimized_level * 100)}%
                    </span>
                  </div>
                </td>
                <td>
                  {reduction > 0
                    ? <span style={{ color: 'var(--accent-green)', fontWeight: 600 }}>↓ {reduction}% reduction</span>
                    : <span style={{ color: 'var(--text-muted)' }}>No change</span>
                  }
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}
