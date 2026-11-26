"""spike_serp.py

Owner: Stream C · Roadmap: Stage 1a (feasibility test)
Purpose: throwaway SerpApi test. Run Google Lens on an image URL (and the upload flow), then
Google Shopping on the top match title. Record latency, rating/review coverage, result counts and
searches per user query; save raw JSON to the cache (C4).

Usage: python backend/scripts/spike_serp.py --image-url https://... [--query "..."]
Reads SERPAPI_KEY from the environment. Uses real quota: run by hand only, never in tests.

STUB: not implemented yet.
"""
from __future__ import annotations

import argparse
import os


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="SerpApi feasibility spike (Stage 1a)")
    parser.add_argument("--image-url", help="Image URL for Google Lens")
    parser.add_argument("--query", help="Google Shopping query (defaults to the top Lens title)")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    parse_args(argv)
    api_key = os.environ.get("SERPAPI_KEY", "")
    if not api_key:
        raise SystemExit("SERPAPI_KEY is not set (copy .env.example to .env and fill it in)")
    raise NotImplementedError("TODO: Stage 1a (spike_serp)")


if __name__ == "__main__":
    main()
