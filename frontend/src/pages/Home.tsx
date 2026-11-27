// Owner: Stream D · Roadmap: Stage 5b
// Purpose: collect an image (camera/upload or URL) + optional text, call search(), go to Results.
// STUB: minimal flow; loading animation and paste-a-screenshot come later (5b, 5f).
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { search } from '../api/client'
import ImageInput, { type ImageInputValue } from '../components/ImageInput'

export default function Home() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(value: ImageInputValue) {
    setLoading(true)
    setError(null)
    try {
      const response = await search(value.request)
      navigate('/results', { state: { response, imageSrc: value.previewSrc, request: value.request } })
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    } finally {
      setLoading(false)
    }
  }

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-bold">Find this product online</h1>
      <p className="text-slate-600 dark:text-slate-400">
        Take a photo, upload a screenshot, or paste an image URL.
      </p>
      <ImageInput onSubmit={handleSubmit} disabled={loading} />
      {loading && <p className="text-sm">Searching…</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}
    </section>
  )
}
