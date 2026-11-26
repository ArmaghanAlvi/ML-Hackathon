// Owner: Stream D · Roadmap: Stage 5f
// Purpose: box → crop zoom → "Searching the web…" → non-matches fade out.
// STUB: placeholder that lists the pipeline steps and backend timings.
interface Props {
  timings: Record<string, number>
  cached: boolean
}

export default function PipelineAnimation({ timings, cached }: Props) {
  return (
    <section className="rounded border border-dashed border-slate-400 p-3 text-sm">
      <p className="font-medium">
        Pipeline (placeholder animation){cached && <span className="ml-2 text-amber-600">served from cache</span>}
      </p>
      <ol className="mt-1 flex flex-wrap gap-2 text-slate-600 dark:text-slate-400">
        {Object.entries(timings).map(([step, ms]) => (
          <li key={step} className="rounded bg-slate-200 px-2 py-0.5 dark:bg-slate-800">
            {step}: {Math.round(ms)} ms
          </li>
        ))}
      </ol>
    </section>
  )
}
