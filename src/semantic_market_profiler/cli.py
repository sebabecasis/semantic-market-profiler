from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import query_evidence
from .models import Evidence
from .pipeline import build_plan, run_profile


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description="Operator-controlled semantic market profiler")
    commands = root.add_subparsers(dest="command", required=True)

    plan = commands.add_parser("plan", help="Write a source and enrichment plan for review")
    plan.add_argument("--config", type=Path, required=True)
    plan.add_argument("--out", type=Path, required=True)

    run = commands.add_parser("run", help="Run an explicitly approved plan over a corpus")
    run.add_argument("--config", type=Path, required=True)
    run.add_argument("--corpus", type=Path, required=True)
    run.add_argument("--out", type=Path, required=True)
    run.add_argument("--approve-plan", action="store_true")

    query = commands.add_parser("query", help="Query retained evidence from a completed run")
    query.add_argument("--run-dir", type=Path, required=True)
    query.add_argument("--query", required=True)
    query.add_argument("--top", type=int, default=5)
    return root


def main() -> int:
    args = parser().parse_args()
    if args.command == "plan":
        result = build_plan(args.config, args.out)
    elif args.command == "run":
        result = run_profile(
            args.config,
            args.corpus,
            args.out,
            operator_approved=args.approve_plan,
        )
    else:
        values = json.loads((args.run_dir / "evidence.json").read_text(encoding="utf-8"))
        evidence = [Evidence(**row) for row in values]
        result = query_evidence(evidence, args.query, top=args.top)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
