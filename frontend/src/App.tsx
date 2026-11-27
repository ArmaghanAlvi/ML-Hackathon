// Owner: Stream D · Roadmap: Stage 5a. Routes: / (Home), /results, /camera.
import { useRef, useState } from 'react'
import { Link, Route, Routes } from 'react-router-dom'
import { USE_MOCKS, search } from './api/client'
import type { ImageInputValue } from './components/ImageInput'
import Camera from './pages/Camera'
import Home from './pages/Home'
import Results from './pages/Results'
import type { SearchResponse } from './types/api'

interface SearchResult {
  response: SearchResponse
  imageSrc: string | null
}

export default function App() {
  const [draft, setDraft] = useState<ImageInputValue>({
    request: { image_base64: null, image_url: null, text: '', box: null },
    previewSrc: null,
  })
  const [result, setResult] = useState<SearchResult | null>(null)
  const [searching, setSearching] = useState(false)
  const [searchError, setSearchError] = useState<string | null>(null)
  const searchId = useRef(0)

  async function runSearch(value: ImageInputValue) {
    const requestId = ++searchId.current
    setDraft(value)
    setSearching(true)
    setSearchError(null)

    try {
      const response = await search(value.request)
      if (requestId === searchId.current) {
        setResult({ response, imageSrc: value.previewSrc })
      }
    } catch (e) {
      if (requestId === searchId.current) {
        setSearchError(e instanceof Error ? e.message : String(e))
      }
    } finally {
      if (requestId === searchId.current) setSearching(false)
    }
  }

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
          <Route
            path="/"
            element={
              <Home
                value={draft}
                onChange={setDraft}
                onSearch={runSearch}
                loading={searching}
                error={searchError}
              />
            }
          />
          <Route
            path="/results"
            element={
              <Results
                value={draft}
                onChange={setDraft}
                onSearch={runSearch}
                result={result}
                loading={searching}
                error={searchError}
              />
            }
          />
          <Route path="/camera" element={<Camera />} />
        </Routes>
      </main>
    </div>
  )
}
