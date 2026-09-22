# Semantic Market Profiler

For agent-assisted operation, start with [AGENTS.md](AGENTS.md). Claude Code loads the same guide through [CLAUDE.md](CLAUDE.md).

Turn an open-ended market question into an operator-reviewed source plan, evidence-backed semantic profiles and inspectable post-qualification.

This is a generalisation of a working Hiring Philosophy Profiler. Hiring philosophy remains one supplied configuration rather than the product boundary.

```text
research question
→ proposed sources and semantic signals
→ operator review and explicit approval
→ evidence extraction with provenance
→ semantic matching
→ editable post-qualification
→ ranked, queryable profiles
```

## Run the examples

Requires Python 3.11+ and no API credentials.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .

semantic-profiler plan \
  --config examples/hiring-philosophy/config.json \
  --out outputs/hiring

semantic-profiler run \
  --config examples/hiring-philosophy/config.json \
  --corpus examples/hiring-philosophy/corpus.json \
  --out outputs/hiring \
  --approve-plan

semantic-profiler query \
  --run-dir outputs/hiring \
  --query "teams that value ownership and fast learning"
```

Change both paths to `examples/buyer-readiness/...` to run the non-hiring example.

Each run writes the reviewed source plan, exact evidence, entity profiles and a reproducibility manifest. Without `--approve-plan`, profiling stops before processing.

## Honest boundary

The safe fixtures use a deterministic demo encoder. The [live workflow](docs/live-workflow.md) implements reviewed Firecrawl collection, optional verbatim LLM extraction, OpenAI embeddings, hash-bound approval and explicit missing-evidence coverage. Provider contracts are mock-tested; real account acceptance and threshold calibration remain necessary. The agent designs the source inventory and signals, rather than an autonomous discovery crawler.

See [`docs/architecture.md`](docs/architecture.md) for the design and provenance model.
