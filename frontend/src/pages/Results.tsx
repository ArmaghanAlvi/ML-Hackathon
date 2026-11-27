// Owner: Stream D · Roadmap: Stage 5d
// Purpose: show the SearchResponse: pipeline animation, detections, top-3 tabs, cards, value scatter.
import { Link } from 'react-router-dom'
import type { Dispatch, SetStateAction } from 'react'
import DetectionOverlay from '../components/DetectionOverlay'
import ImageInput, { type ImageInputValue } from '../components/ImageInput'
import PipelineAnimation from '../components/PipelineAnimation'
import ProductCard from '../components/ProductCard'
import TopThreeList from '../components/TopThreeList'
import ValueScatter from '../components/ValueScatter'
import type { Candidate, SearchResponse } from '../types/api'

interface SearchResult {
  response: SearchResponse
  imageSrc: string | null
}

interface Props {
  value: ImageInputValue
  onChange: Dispatch<SetStateAction<ImageInputValue>>
  onSearch: (value: ImageInputValue) => void
  result: SearchResult | null
  loading: boolean
  error: string | null
}

function Group({ title, items }: { title: string; items: Candidate[] }) {
  return (
    <section className="space-y-2">
      <h2 className="text-lg font-semibold">
        {title} <span className="text-sm font-normal text-slate-500">({items.length})</span>
      </h2>
      {items.length === 0 ? (
        <p className="text-sm text-slate-500">No {title.toLowerCase()} matches.</p>
      ) : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {items.map((c) => (
            <ProductCard key={c.id} candidate={c} />
          ))}
        </div>
      )}
    </section>
  )
}

export default function Results({ value, onChange, onSearch, result, loading, error }: Props) {
  const response = result?.response
  const identical = response?.candidates.filter((c) => c.match_label === 'identical') ?? []
  const similar = response?.candidates.filter((c) => c.match_label === 'similar') ?? []
  const none = response?.candidates.filter((c) => c.match_label === 'none') ?? []

  return (
    <div className="space-y-6">
      <ImageInput value={value} onChange={onChange} onSubmit={onSearch} compact />
      {loading && (
        <p role="status" className="text-sm text-sky-700 dark:text-sky-300">
          {response ? 'Searching… Previous results remain visible.' : 'Searching…'}
        </p>
      )}
      {error && <p className="text-sm text-red-600">{error}</p>}
      {response ? (
        <>
          <PipelineAnimation timings={response.timings_ms} cached={response.cached} />
          <DetectionOverlay
            imageSrc={result.imageSrc}
            detections={response.detections}
            selected={value.request.box ?? null}
            onSelectionChange={(box) =>
              onChange((current) => ({ ...current, request: { ...current.request, box } }))
            }
          />
          <TopThreeList response={response} />
          <Group title="Identical" items={identical} />
          <Group title="Similar" items={similar} />
          <details className="space-y-3">
            <summary className="cursor-pointer text-lg font-semibold">
              None <span className="text-sm font-normal text-slate-500">({none.length})</span>
            </summary>
            {none.length === 0 ? (
              <p className="text-sm text-slate-500">No non-matching products.</p>
            ) : (
              <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                {none.map((c) => (
                  <ProductCard key={c.id} candidate={c} />
                ))}
              </div>
            )}
          </details>
          <ValueScatter response={response} />
        </>
      ) : (
        <p>
          {loading ? 'Your search is in progress.' : 'No results yet. '}
          {!loading && (
            <>
              <Link to="/" className="underline">
                Start a search
              </Link>
            </>
          )}
        </p>
      )}
    </div>
  )
}
