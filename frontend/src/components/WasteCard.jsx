export default function WasteCard({ issue }) {
  return (
    <div className={`waste-card ${issue.severity}`}>
      <div className="waste-card-header">
        <span className="waste-card-title">{issue.title}</span>
        <span className={`severity-chip ${issue.severity}`}>{issue.severity}</span>
      </div>
      <p className="waste-evidence">{issue.evidence}</p>
      {issue.estimated_impact_kwh > 0 && (
        <p className="waste-impact">⚡ Est. impact: {issue.estimated_impact_kwh} kWh</p>
      )}
      <p className="waste-recommendation">💡 {issue.recommendation}</p>
    </div>
  )
}
