// Owner: Stream D · Roadmap: Stage 5a (mocks), 5g (switch to live API)
// Purpose: the only place the frontend talks to the backend (contract C1).
// VITE_USE_MOCKS: "true" (or unset) → return the canonical @shared mock after 800 ms;
//                 "false" → POST /api/search (Vite proxies /api to :8000 in dev).
import mock from '@shared/mocks/search_response.json'
import type { SearchRequest, SearchResponse } from '../types/api'

export const USE_MOCKS = import.meta.env.VITE_USE_MOCKS !== 'false'
const MOCK_DELAY_MS = 800

export async function search(req: SearchRequest): Promise<SearchResponse> {
  if (USE_MOCKS) {
    await new Promise((resolve) => setTimeout(resolve, MOCK_DELAY_MS))
    return mock as SearchResponse
  }
  const res = await fetch('/api/search', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  })
  if (!res.ok) {
    throw new Error(`search failed: ${res.status} ${await res.text()}`)
  }
  return (await res.json()) as SearchResponse
}
