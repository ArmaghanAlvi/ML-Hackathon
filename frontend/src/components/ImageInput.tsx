// Owner: Stream D · Roadmap: Stage 5b
// Purpose: camera capture / upload (capture="environment"), image URL, optional text refinement.
import {
  useCallback,
  useEffect,
  useState,
  type Dispatch,
  type FormEvent,
  type SetStateAction,
} from 'react'
import type { SearchRequest } from '../types/api'

export interface ImageInputValue {
  request: SearchRequest
  previewSrc: string | null
}

interface Props {
  value: ImageInputValue
  onChange: Dispatch<SetStateAction<ImageInputValue>>
  onSubmit: (value: ImageInputValue) => void
  disabled?: boolean
  compact?: boolean
}

function readAsDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(reader.error)
    reader.readAsDataURL(file)
  })
}

export default function ImageInput({ value, onChange, onSubmit, disabled, compact = false }: Props) {
  const [error, setError] = useState<string | null>(null)

  const setImageFile = useCallback(async (file: File) => {
    try {
      const dataUrl = await readAsDataUrl(file)
      const base64 = dataUrl.slice(dataUrl.indexOf(',') + 1)
      onChange((current) => ({
        request: {
          ...current.request,
          image_base64: base64,
          image_url: null,
          box: null,
        },
        previewSrc: dataUrl,
      }))
      setError(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not read the selected image.')
    }
  }, [onChange])

  useEffect(() => {
    function handlePaste(event: ClipboardEvent) {
      const items = event.clipboardData?.items
      if (!items) return

      for (const item of Array.from(items)) {
        if (!item.type.startsWith('image/')) continue

        const pastedFile = item.getAsFile()
        if (!pastedFile) continue

        event.preventDefault()
        void setImageFile(pastedFile)
        break
      }
    }

    document.addEventListener('paste', handlePaste)
    return () => document.removeEventListener('paste', handlePaste)
  }, [setImageFile])

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setError(null)
    const imageUrl = value.request.image_url?.trim()
    if (!value.request.image_base64 && !imageUrl) {
      setError('Add a photo or an image URL.')
      return
    }

    onSubmit({
      request: {
        ...value.request,
        image_url: value.request.image_base64 ? null : imageUrl,
        text: value.request.text?.trim() || null,
      },
      previewSrc: value.previewSrc,
    })
  }

  const field = 'w-full rounded border border-slate-300 bg-white px-3 py-2 dark:border-slate-700 dark:bg-slate-900'

  return (
    <form onSubmit={handleSubmit} className={compact ? 'flex flex-wrap items-center gap-3 rounded-lg border border-slate-200 bg-white p-3 dark:border-slate-800 dark:bg-slate-900' : 'space-y-3'}>
      {compact && (
        value.previewSrc ? (
          <img src={value.previewSrc} alt="Current search image" className="h-12 w-12 flex-none rounded object-cover" />
        ) : (
          <div className="flex h-12 w-12 flex-none items-center justify-center rounded bg-slate-100 text-xs text-slate-500 dark:bg-slate-800">
            No image
          </div>
        )
      )}
      <label className={compact ? 'cursor-pointer rounded border border-slate-300 px-3 py-2 text-sm font-medium dark:border-slate-700' : 'block space-y-1'}>
        <span className={compact ? '' : 'text-sm font-medium'}>
          {compact ? 'Replace image' : 'Photo or screenshot'}
        </span>
        <input
          type="file"
          accept="image/*"
          capture="environment"
          onChange={(e) => {
            const file = e.currentTarget.files?.[0]
            e.currentTarget.value = ''
            if (file) void setImageFile(file)
          }}
          className={compact ? 'sr-only' : 'block w-full text-sm'}
        />
      </label>
      <label className={compact ? 'min-w-40 flex-1' : 'block space-y-1'}>
        <span className={compact ? 'sr-only' : 'text-sm font-medium'}>…or image URL</span>
        <input
          type="url"
          placeholder={compact ? 'Image URL' : 'https://example.com/product.jpg'}
          value={value.request.image_url ?? ''}
          onChange={(e) => {
            const imageUrl = e.currentTarget.value
            onChange((current) => ({
              request: {
                ...current.request,
                image_base64: null,
                image_url: imageUrl || null,
                box: null,
              },
              previewSrc: imageUrl || null,
            }))
            setError(null)
          }}
          className={field}
        />
      </label>
      <label className={compact ? 'min-w-40 flex-1' : 'block space-y-1'}>
        <span className={compact ? 'sr-only' : 'text-sm font-medium'}>Refine (optional)</span>
        <input
          type="text"
          placeholder='e.g. "yellow version"'
          value={value.request.text ?? ''}
          onChange={(e) => {
            const text = e.currentTarget.value
            onChange((current) => ({
              ...current,
              request: { ...current.request, text },
            }))
          }}
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
