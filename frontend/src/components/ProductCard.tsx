// Owner: Stream D · Roadmap: Stage 5d
// Purpose: one candidate: image, title, price, listed + adjusted rating, store link, match label.
import type { Candidate } from '../types/api'

export function formatPrice(c: Candidate): string {
  if (c.price == null) return 'No price'

  try {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: c.currency }).format(c.price)
  } catch {
    return `${c.price.toFixed(2)} ${c.currency || ''}`.trim()
  }
}

const matchBadgeStyle: Record<Candidate['match_label'], string> = {
  identical: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300',
  similar: 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300',
  none: 'bg-slate-200 text-slate-800 dark:bg-slate-700 dark:text-slate-200',
}

const matchLabel: Record<Candidate['match_label'], string> = {
  identical: 'Identical',
  similar: 'Similar',
  none: 'None',
}

export default function ProductCard({ candidate: c }: { candidate: Candidate }) {
  return (
    <article className="flex gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm dark:border-slate-800 dark:bg-slate-900">
      {c.image_url && (
        <img src={c.image_url} alt="" className="h-24 w-24 flex-none rounded object-cover" loading="lazy" />
      )}
      <div className="min-w-0 space-y-2 text-sm">
        <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${matchBadgeStyle[c.match_label]}`}>
          {matchLabel[c.match_label]}
        </span>
        <h3 className="line-clamp-2 font-semibold">{c.title || 'Untitled product'}</h3>
        <p className="font-semibold">{formatPrice(c)}</p>
        <p className="text-slate-600 dark:text-slate-400">
          {c.rating == null ? 'No rating' : `★ ${c.rating.toFixed(1)}`}
          {' · '}
          {c.review_count == null ? 'No review count' : `${c.review_count.toLocaleString()} reviews`}
        </p>
        <p className="text-slate-600 dark:text-slate-400">
          Sold by <span className="font-medium">{c.source || 'Store unavailable'}</span>
        </p>
        {c.link ? (
          <a href={c.link} target="_blank" rel="noopener noreferrer" className="inline-block font-medium text-sky-700 underline dark:text-sky-400">
            Visit store
          </a>
        ) : (
          <p className="text-slate-500">Store link unavailable</p>
        )}
      </div>
    </article>
  )
}
