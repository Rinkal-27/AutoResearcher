"""CLI entrypoint: `python -m autoresearcher.cli "your question"`."""
from __future__ import annotations

import argparse
import sys

from .graph import run_research


def main() -> int:
    parser = argparse.ArgumentParser(description="AutoResearcher CLI")
    parser.add_argument("query", help="Research question")
    parser.add_argument("--max-iterations", type=int, default=3)
    parser.add_argument("--output", "-o", help="Write report to this file")
    args = parser.parse_args()

    result = run_research(args.query, max_iterations=args.max_iterations)
    report = result["report"]

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(report)
        print(
            f"Wrote report to {args.output} "
            f"(iterations={result['iterations']}, approved={result['approved']})"
        )
    else:
        print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
