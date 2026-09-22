from __future__ import annotations

import argparse
import json
from pathlib import Path

from .engine import query_evidence
from .models import Evidence
from .pipeline import build_plan, run_profile
from .pipeline import write_json
from .config import load_config
from .collect import collect
from .providers import OpenAIEncoder


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
    run.add_argument("--approved-plan-hash")
    run.add_argument("--encoder", choices=["demo", "openai"], default="demo")
    run.add_argument("--model", default="text-embedding-3-small")
    run.add_argument("--dimensions", type=int, default=1536)

    collection = commands.add_parser("collect", help="Fetch the reviewed source inventory (paid Firecrawl calls)")
    collection.add_argument("--config", type=Path, required=True)
    collection.add_argument("--approved-plan-hash", required=True)
    collection.add_argument("--out", type=Path, required=True)

    query = commands.add_parser("query", help="Query retained evidence from a completed run")
    query.add_argument("--run-dir", type=Path, required=True)
    query.add_argument("--query", required=True)
    query.add_argument("--top", type=int, default=5)
    return root


def main() -> int:
    args = parser().parse_args()
    if args.command == "plan":
        result = build_plan(args.config, args.out)
    elif args.command == "collect":
        result = collect(load_config(args.config), args.approved_plan_hash)
        write_json(args.out / "corpus.json", result["passages"])
        write_json(args.out / "collection.json", result)
        print(json.dumps(result, indent=2))
        return 1 if result["failures"] else 0
    elif args.command == "run":
        result = run_profile(
            args.config,
            args.corpus,
            args.out,
            operator_approved=args.approve_plan,
            approved_hash=args.approved_plan_hash,
            encoder=OpenAIEncoder(args.model, args.dimensions, args.out / "embedding-cache") if args.encoder == "openai" else None,
        )
    else:
        values = json.loads((args.run_dir / "evidence.json").read_text(encoding="utf-8"))
        evidence = [Evidence(**row) for row in values]
        manifest = json.loads((args.run_dir / "run.json").read_text())
        spec = manifest.get("embedding", {"provider": "demo"})
        encoder = OpenAIEncoder(spec["model"], spec["dimensions"], args.run_dir / "embedding-cache") if spec["provider"] == "openai" else None
        result = query_evidence(evidence, args.query, top=args.top, encoder=encoder)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
