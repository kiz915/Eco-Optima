import { useLocation, Link } from 'react-router-dom'

const STEPS = [
  { path: '/', label: '1 · Input' },
  { path: '/dashboard', label: '2 · Dashboard' },
  { path: '/results', label: '3 · Optimization' },
]

export default function NavBar() {
  const { pathname } = useLocation()
  const currentIdx = STEPS.findIndex((s) => s.path === pathname)

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-logo">
        🌿 <span>EcoOptima</span>
      </Link>
      <div className="navbar-steps">
        {STEPS.map((s, i) => (
          <span
            key={s.path}
            className={`nav-step ${i === currentIdx ? 'active' : i < currentIdx ? 'done' : ''}`}
          >
            {s.label}
          </span>
        ))}
      </div>
    </nav>
  )
}
