// Owner: Stream D · Roadmap: Stage 5a. Routes: / (Home), /results, /camera.
import { Link, Route, Routes } from 'react-router-dom'
import { USE_MOCKS } from './api/client'
import Camera from './pages/Camera'
import Home from './pages/Home'
import Results from './pages/Results'

export default function App() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <header className="flex items-center justify-between border-b border-slate-200 px-4 py-3 dark:border-slate-800">
        <Link to="/" className="font-semibold">
          Product Compare <span className="text-xs font-normal text-slate-500">(working title)</span>
        </Link>
        <nav className="flex items-center gap-3 text-sm">
          {USE_MOCKS && <span className="rounded bg-amber-200 px-2 py-0.5 text-amber-900">mock data</span>}
          <Link to="/camera" className="underline">
            Live camera
          </Link>
        </nav>
      </header>
      <main className="mx-auto max-w-5xl p-4">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/results" element={<Results />} />
          <Route path="/camera" element={<Camera />} />
        </Routes>
      </main>
    </div>
  )
}
