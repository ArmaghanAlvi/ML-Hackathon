// Owner: Stream D · Roadmap: Stage 5b
// Purpose: collect an image (camera/upload or URL) + optional text, call search(), go to Results.
import { useNavigate } from 'react-router-dom'
import type { Dispatch, SetStateAction } from 'react'
import ImageInput, { type ImageInputValue } from '../components/ImageInput'

interface Props {
  value: ImageInputValue
  onChange: Dispatch<SetStateAction<ImageInputValue>>
  onSearch: (value: ImageInputValue) => void
  loading: boolean
  error: string | null
}

export default function Home({ value, onChange, onSearch, loading, error }: Props) {
  const navigate = useNavigate()

  function handleSubmit(nextValue: ImageInputValue) {
    onSearch(nextValue)
    navigate('/results')
  }

  return (
    <section className="space-y-4">
      <h1 className="text-2xl font-bold">Find this product online</h1>
      <p className="text-slate-600 dark:text-slate-400">
        Take a photo, upload a screenshot, or paste an image URL.
      </p>
      <ImageInput
        value={value}
        onChange={onChange}
        onSubmit={handleSubmit}
      />
      {loading && <p className="text-sm">Searching…</p>}
      {error && <p className="text-sm text-red-600">{error}</p>}
    </section>
  )
}
