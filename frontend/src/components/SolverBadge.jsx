export default function SolverBadge({ solver }) {
  const isWolfram = solver === 'wolfram'
  return (
    <span className={`solver-badge ${isWolfram ? 'wolfram' : 'fallback'}`}>
      {isWolfram ? '⚡ Solved via Wolfram Alpha' : '🔧 Solved via local fallback solver'}
    </span>
  )
}
