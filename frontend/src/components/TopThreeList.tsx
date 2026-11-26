// Owner: Stream D · Roadmap: Stage 5d
// Purpose: tabs for Cheapest / Top rated / Best value, reading the id lists from the response.
// STUB: plain tabs.
import { useState } from 'react'
import type { SearchResponse } from '../types/api'
import { formatPrice } from './ProductCard'

const TABS = [
  { key: 'top_cheapest', label: 'Cheapest' },
  { key: 'top_rated', label: 'Top rated' },
  { key: 'best_value', label: 'Best value' },
] as const

export default function TopThreeList({ response }: { response: SearchResponse }) {
  const [tab, setTab] = useState<(typeof TABS)[number]['key']>('top_cheapest')
  const byId = new Map(response.candidates.map((c) => [c.id, c]))
  const items = response[tab].map((id) => byId.get(id)).filter((c) => c !== undefined)

  return (
    <section className="space-y-2">
      <div role="tablist" className="flex gap-2">
        {TABS.map((t) => (
          <button
            key={t.key}
            role="tab"
            aria-selected={tab === t.key}
            onClick={() => setTab(t.key)}
            className={`rounded px-3 py-1 text-sm ${tab === t.key ? 'bg-sky-600 text-white' : 'bg-slate-200 dark:bg-slate-800'}`}
          >
            {t.label}
          </button>
        ))}
      </div>
      <ol className="list-decimal space-y-1 pl-6 text-sm">
        {items.map((c) => (
          <li key={c.id}>
            <a href={c.link} target="_blank" rel="noreferrer" className="underline">
              {c.title}
            </a>{' '}
            · {formatPrice(c)}
            {c.adjusted_rating != null && ` · adj ★ ${c.adjusted_rating.toFixed(2)}`}
          </li>
        ))}
      </ol>
    </section>
  )
}
