// Owner: Stream D · Roadmap: Stage 5d
// Purpose: one candidate: image, title, price, listed + adjusted rating, store link, match label.
// STUB: plain styling.
import type { Candidate } from '../types/api'

export function formatPrice(c: Candidate): string {
  return c.price == null ? 'Price n/a' : new Intl.NumberFormat('en-US', { style: 'currency', currency: c.currency }).format(c.price)
}

export default function ProductCard({ candidate: c }: { candidate: Candidate }) {
  return (
    <article className="flex gap-3 rounded border border-slate-200 bg-white p-3 dark:border-slate-800 dark:bg-slate-900">
      <img src={c.image_url} alt="" className="h-20 w-20 flex-none rounded object-cover" loading="lazy" />
      <div className="min-w-0 space-y-1 text-sm">
        <a href={c.link} target="_blank" rel="noreferrer" className="line-clamp-2 font-medium underline">
          {c.title}
        </a>
        <p>
          <span className="font-semibold">{formatPrice(c)}</span> · {c.source}
        </p>
        <p className="text-slate-600 dark:text-slate-400">
          {c.rating == null ? 'No rating' : `★ ${c.rating.toFixed(1)}`}
          {c.review_count != null && ` (${c.review_count.toLocaleString()})`}
          {c.adjusted_rating != null && ` · adj ${c.adjusted_rating.toFixed(2)}`}
        </p>
        <p className="text-xs text-slate-500">
          {c.match_label} · score {c.match_score.toFixed(2)}
        </p>
      </div>
    </article>
  )
}
