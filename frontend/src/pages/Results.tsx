// Owner: Stream D · Roadmap: Stage 5d
// Purpose: show the SearchResponse: pipeline animation, detections, top-3 tabs, cards, value scatter.
import { Link } from 'react-router-dom'
import { useState } from 'react'
import type { Dispatch, SetStateAction } from 'react'
import DetectionOverlay from '../components/DetectionOverlay'
import ImageInput, { type ImageInputValue } from '../components/ImageInput'
import PipelineAnimation from '../components/PipelineAnimation'
import ProductCard from '../components/ProductCard'
import TopThreeList from '../components/TopThreeList'
import ValueScatter from '../components/ValueScatter'
import { mergeStandIns } from '../dev/mergeStandIns'
import type { DevCandidate, DevSearchResponse } from '../dev/types'
import type { SearchResponse } from '../types/api'

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

function Group({ title, items }: { title: string; items: DevCandidate[] }) {
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
  const [activeTab, setActiveTab] = useState<'items' | 'suggestions'>('items')
  const [selectedSuggestion, setSelectedSuggestion] = useState<number | null>(null)
  const response: DevSearchResponse | null = result ? mergeStandIns(result.response) : null
  const imageSrc = result?.imageSrc ?? null
  const suggestions = response?.suggestions ?? []
  const identical = response?.candidates.filter((c) => c.match_label === 'identical') ?? []
  const similar = response?.candidates.filter((c) => c.match_label === 'similar') ?? []
  const none = response?.candidates.filter((c) => c.match_label === 'none') ?? []
  const selectedSuggestionData =
    selectedSuggestion == null ? undefined : suggestions[selectedSuggestion]
  const candidatesById = new Map(response?.candidates.map((candidate) => [candidate.id, candidate]) ?? [])
  const suggestedCandidates =
    selectedSuggestionData?.candidate_ids
      .map((id) => candidatesById.get(id))
      .filter((candidate): candidate is DevCandidate => candidate !== undefined) ?? []

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
            imageSrc={imageSrc}
            detections={response.detections}
            selected={value.request.box ?? null}
            onSelectionChange={(box) =>
              onChange((current) => ({ ...current, request: { ...current.request, box } }))
            }
          />
          <TopThreeList response={response} />
          <section className="space-y-4">
            <div role="tablist" aria-label="Product results" className="flex gap-2 border-b border-slate-200 dark:border-slate-800">
              <button
                type="button"
                role="tab"
                aria-selected={activeTab === 'items'}
                onClick={() => setActiveTab('items')}
                className={`border-b-2 px-3 py-2 text-sm font-medium ${
                  activeTab === 'items'
                    ? 'border-sky-600 text-sky-700 dark:text-sky-400'
                    : 'border-transparent text-slate-600 dark:text-slate-400'
                }`}
              >
                Items
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={activeTab === 'suggestions'}
                onClick={() => setActiveTab('suggestions')}
                className={`border-b-2 px-3 py-2 text-sm font-medium ${
                  activeTab === 'suggestions'
                    ? 'border-sky-600 text-sky-700 dark:text-sky-400'
                    : 'border-transparent text-slate-600 dark:text-slate-400'
                }`}
              >
                Suggestions
              </button>
            </div>
            {activeTab === 'items' ? (
              <div role="tabpanel" className="space-y-6">
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
              </div>
            ) : (
              <div role="tabpanel" className="space-y-4">
                {suggestions.length === 0 ? (
                  <p className="text-sm text-slate-500">No suggestions available yet.</p>
                ) : (
                  <div className="flex flex-wrap gap-2">
                    {suggestions.map((suggestion, index) => (
                    <div key={`${suggestion.keyword}-${index}`} className="flex items-center gap-1">
                      <button
                        type="button"
                        aria-pressed={selectedSuggestion === index}
                        onClick={() => setSelectedSuggestion(index)}
                        className={`rounded-full border px-3 py-1.5 text-sm ${
                          selectedSuggestion === index
                            ? 'border-sky-600 bg-sky-100 text-sky-900 dark:bg-sky-950 dark:text-sky-200'
                            : 'border-slate-300 bg-white dark:border-slate-700 dark:bg-slate-900'
                        }`}
                      >
                        {suggestion.keyword}
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          const existingText = value.request.text?.trim()
                          const text = [existingText, suggestion.keyword].filter(Boolean).join(' ')
                          onSearch({
                            ...value,
                            request: { ...value.request, text },
                          })
                        }}
                        className="rounded px-2 py-1.5 text-xs text-sky-700 underline dark:text-sky-400"
                      >
                        Search
                      </button>
                    </div>
                    ))}
                  </div>
                )}
                {suggestions.length === 0 ? null : selectedSuggestion == null ? (
                  <p className="text-sm text-slate-500">Choose a suggestion to see matching products.</p>
                ) : !selectedSuggestionData ? (
                  <p className="text-sm text-slate-500">Choose a suggestion to see matching products.</p>
                ) : suggestedCandidates.length ? (
                  <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
                    {suggestedCandidates.map((candidate) => (
                      <ProductCard key={candidate.id} candidate={candidate} />
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-slate-500">No products for this suggestion.</p>
                )}
              </div>
            )}
          </section>
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
