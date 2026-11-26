// Owner: Stream D · Roadmap: Stage 5d
// Purpose: show the SearchResponse: pipeline animation, detections, top-3 tabs, cards, value scatter.
// STUB: layout only; animation, overlay interaction and scatter are placeholders.
import { Link, useLocation } from 'react-router-dom'
import DetectionOverlay from '../components/DetectionOverlay'
import PipelineAnimation from '../components/PipelineAnimation'
import ProductCard from '../components/ProductCard'
import TopThreeList from '../components/TopThreeList'
import ValueScatter from '../components/ValueScatter'
import type { Candidate, SearchResponse } from '../types/api'

interface ResultsState {
  response?: SearchResponse
  imageSrc?: string | null
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
  const response = state.response

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

  return (
    <div className="space-y-6">
      <PipelineAnimation timings={response.timings_ms} cached={response.cached} />
      <DetectionOverlay
        imageSrc={state.imageSrc ?? null}
        detections={response.detections}
        selected={response.selected_box ?? null}
      />
      <TopThreeList response={response} />
      <Group title="Identical" items={identical} />
      <Group title="Similar" items={similar} />
      <ValueScatter response={response} />
    </div>
  )
}
