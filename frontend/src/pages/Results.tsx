// Owner: Stream D · Roadmap: Stage 5d
// Purpose: show the SearchResponse: pipeline animation, detections, top-3 tabs, cards, value scatter.
// STUB: animation and scatter are placeholders.
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useState } from 'react'
import { search } from '../api/client'
import DetectionOverlay from '../components/DetectionOverlay'
import PipelineAnimation from '../components/PipelineAnimation'
import ProductCard from '../components/ProductCard'
import TopThreeList from '../components/TopThreeList'
import ValueScatter from '../components/ValueScatter'
import type { Box, Candidate, SearchRequest, SearchResponse } from '../types/api'

interface ResultsState {
  response?: SearchResponse
  imageSrc?: string | null
  request?: SearchRequest
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

export default function Results() {
  const state = (useLocation().state ?? {}) as ResultsState
  const navigate = useNavigate()
  const response = state.response
  const [selectedBox, setSelectedBox] = useState<Box | null>(response?.selected_box ?? null)
  const [searchingSelection, setSearchingSelection] = useState(false)
  const [selectionError, setSelectionError] = useState<string | null>(null)

  if (!response) {
    return (
      <p>
        No results yet.{' '}
        <Link to="/" className="underline">
          Start a search
        </Link>
      </p>
    )
  }

  const identical = response.candidates.filter((c) => c.match_label === 'identical')
  const similar = response.candidates.filter((c) => c.match_label === 'similar')
  const none = response.candidates.filter((c) => c.match_label === 'none')

  async function searchSelectedArea() {
    if (!selectedBox || !state.request) return

    setSearchingSelection(true)
    setSelectionError(null)
    try {
      const refinedResponse = await search({ ...state.request, box: selectedBox })
      navigate('/results', {
        replace: true,
        state: { ...state, response: refinedResponse, request: { ...state.request, box: selectedBox } },
      })
    } catch (e) {
      setSelectionError(e instanceof Error ? e.message : String(e))
    } finally {
      setSearchingSelection(false)
    }
  }

  return (
    <div className="space-y-6">
      <PipelineAnimation timings={response.timings_ms} cached={response.cached} />
      <DetectionOverlay
        imageSrc={state.imageSrc ?? null}
        detections={response.detections}
        selected={selectedBox}
        onSelectionChange={setSelectedBox}
      />
      {selectedBox && state.request && (
        <div className="space-y-2">
          <button
            type="button"
            onClick={searchSelectedArea}
            disabled={searchingSelection}
            className="rounded bg-sky-600 px-4 py-2 font-medium text-white disabled:opacity-50"
          >
            {searchingSelection ? 'Searching selected area…' : 'Search selected area'}
          </button>
          {selectionError && <p className="text-sm text-red-600">{selectionError}</p>}
        </div>
      )}
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
    </div>
  )
}
