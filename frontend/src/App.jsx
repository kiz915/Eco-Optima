import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import NavBar from './components/NavBar'
import InputScreen from './screens/InputScreen'
import DashboardScreen from './screens/DashboardScreen'
import ResultScreen from './screens/ResultScreen'
import './index.css'

export default function App() {
  return (
    <BrowserRouter>
      <NavBar />
      <Routes>
        <Route path="/" element={<InputScreen />} />
        <Route path="/dashboard" element={<DashboardScreen />} />
        <Route path="/results" element={<ResultScreen />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  )
}
