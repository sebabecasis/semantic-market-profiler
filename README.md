# Semantic Market Profiler

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

The repository demonstrates the generalised control and evidence loop over safe fixture passages. The deterministic local encoder is a demo adapter. Raw web collection, LLM passage extraction and a production embedding provider are explicit integration boundaries, not silently simulated capabilities.

See [`docs/architecture.md`](docs/architecture.md) for the design and provenance model.
