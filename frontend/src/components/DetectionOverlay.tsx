// Owner: Stream D · Roadmap: Stage 5c
// Purpose: draw detection boxes over the image; tap a box to select it.
import type { Box } from '../types/api'

interface Props {
  imageSrc: string | null
  detections: Box[]
  selected: Box | null
  onSelectionChange: (selected: Box | null) => void
}

const same = (a: Box, b: Box | null) => !!b && a.x === b.x && a.y === b.y && a.w === b.w && a.h === b.h

export default function DetectionOverlay({ imageSrc, detections, selected, onSelectionChange }: Props) {
  return (
    <section className="space-y-2">
      <h2 className="text-lg font-semibold">Detections</h2>
      {imageSrc && (
        <div className="relative inline-block max-w-full">
          <img src={imageSrc} alt="query" className="max-h-64 rounded" />
          {detections.map((b, i) => (
            <button
              type="button"
              key={i}
              aria-label={`${same(b, selected) ? 'Deselect' : 'Select'} ${b.label} detection`}
              aria-pressed={same(b, selected)}
              onClick={() => onSelectionChange(same(b, selected) ? null : b)}
              className={`absolute cursor-pointer border-2 p-0 ${
                same(b, selected) ? 'border-sky-500 bg-sky-500/10' : 'border-slate-300 bg-transparent'
              }`}
              style={{ left: `${b.x * 100}%`, top: `${b.y * 100}%`, width: `${b.w * 100}%`, height: `${b.h * 100}%` }}
            />
          ))}
        </div>
      )}
      <ul className="text-sm">
        {detections.map((b, i) => (
          <li key={i}>
            {same(b, selected) ? '▶ ' : ''}
            {b.label} ({Math.round(b.score * 100)}%) at x={b.x.toFixed(2)}, y={b.y.toFixed(2)}, w={b.w.toFixed(2)}, h=
            {b.h.toFixed(2)}
          </li>
        ))}
      </ul>
    </section>
  )
}
