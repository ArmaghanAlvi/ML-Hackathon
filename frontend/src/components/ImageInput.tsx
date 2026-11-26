// Owner: Stream D · Roadmap: Stage 5b
// Purpose: camera capture / upload (capture="environment"), image URL, optional text refinement.
// STUB: minimal form; paste-a-screenshot and validation polish come later.
import { useState, type FormEvent } from 'react'
import type { SearchRequest } from '../types/api'

export interface ImageInputValue {
  request: SearchRequest
  previewSrc: string | null
}

interface Props {
  onSubmit: (value: ImageInputValue) => void
  disabled?: boolean
}

function readAsDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })
}

export default function ImageInput({ onSubmit, disabled }: Props) {
  const [file, setFile] = useState<File | null>(null)
  const [imageUrl, setImageUrl] = useState('')
  const [text, setText] = useState('')
  const [error, setError] = useState<string | null>(null)

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    const refinement = text.trim() || null
    if (file) {
      const dataUrl = await readAsDataUrl(file)
      const base64 = dataUrl.slice(dataUrl.indexOf(',') + 1)
      onSubmit({ request: { image_base64: base64, text: refinement }, previewSrc: dataUrl })
    } else if (imageUrl.trim()) {
      onSubmit({ request: { image_url: imageUrl.trim(), text: refinement }, previewSrc: imageUrl.trim() })
    } else {
      setError('Add a photo or an image URL.')
    }
  }

  const field = 'w-full rounded border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-900'

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <label className="block space-y-1">
        <span className="text-sm font-medium">Photo or screenshot</span>
        <input
          type="file"
          accept="image/*"
          capture="environment"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="block w-full text-sm"
        />
      </label>
      <label className="block space-y-1">
        <span className="text-sm font-medium">…or image URL</span>
        <input
          type="url"
          placeholder="https://example.com/product.jpg"
          value={imageUrl}
          onChange={(e) => setImageUrl(e.target.value)}
          className={field}
        />
      </label>
      <label className="block space-y-1">
        <span className="text-sm font-medium">Refine (optional)</span>
        <input
          type="text"
          placeholder='e.g. "yellow version"'
          value={text}
          onChange={(e) => setText(e.target.value)}
          className={field}
        />
      </label>
      {error && <p className="text-sm text-red-600">{error}</p>}
      <button
        type="submit"
        disabled={disabled}
        className="rounded bg-sky-600 px-4 py-2 font-medium text-white disabled:opacity-50"
      >
        Search
      </button>
    </form>
  )
}
