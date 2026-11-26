// Owner: Stream D · Roadmap: Stage 5e
// Purpose: price vs. adjusted rating scatter, frontier highlighted, weight slider re-ranking via lib/ranking.ts.
// STUB: placeholder box listing the frontier ids.
import type { SearchResponse } from '../types/api'

export default function ValueScatter({ response }: { response: SearchResponse }) {
  return (
    <section className="rounded border border-dashed border-slate-400 p-3 text-sm">
      <p className="font-medium">Value scatter (placeholder)</p>
      <p className="text-slate-600 dark:text-slate-400">Pareto frontier: {response.frontier.join(', ') || 'none'}</p>
    </section>
  )
}
