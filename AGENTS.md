# Operating Semantic Market Profiler

Use this repository to turn a market question into a reviewed research configuration and evidence-backed company profiles. Read `README.md`, `docs/architecture.md`, and the example configuration before operating it. Commands below run from the repository root with Python 3.11+.

## What the agent owns

1. Establish the objective, company universe, relevant signals, exclusions and desired output. Reuse information already supplied; ask only for missing decisions that affect the research.
2. Propose sources and signals with reasons. You perform this reasoning: `planner.py` serializes an existing configuration; it does not discover companies or design a plan.
3. Create a run-specific configuration from an example. Required fields: `name`, `research_question`, `sources`, `signals`, `qualification`. Sources use `kind`, `locator`, `rationale`; signals use unique `id`, `name`, `query`, optional `source_kinds` and `threshold`. Qualification supports `minimum_signals`, `minimum_average_score`, and `require_any` signal IDs.
4. Present the plan for operator review. Edit the configuration itself after feedback. Editing generated `source-plan.json` alone has no effect: the runner regenerates it from the config. Record approval against the actual config used; the current boolean flag does not bind approval to a file hash.
5. Obtain passages from a supplied corpus or authorized research tools. The repo has no collector. If tools are unavailable, report the missing input. Never invent source text, URLs or companies. Preserve exact passages and keep interpretation separate.
6. Run the approved configuration, inspect the evidence, and present qualified companies plus review cases, coverage gaps and the paths to outputs. Treat scores as matching signals, not probabilities or verified buying intent.

## Input and execution

The corpus is a JSON array of passages, each with `entity_id`, `entity_name`, `domain`, `source_url`, `source_kind`, and `text`. Keep IDs stable and source kinds consistent with signal filters. Source locators are advisory; code filters by source kind, not by the approved URL list. Check provenance against the plan yourself.

Start with the bundled fixture without API credentials:

```bash
PYTHONPATH=src python -m semantic_market_profiler.cli plan --config examples/hiring-philosophy/config.json --out outputs/hiring-demo
```

After the operator has approved the plan (or explicitly authorized this fixture demonstration):

```bash
PYTHONPATH=src python -m semantic_market_profiler.cli run --config examples/hiring-philosophy/config.json --corpus examples/hiring-philosophy/corpus.json --out outputs/hiring-demo --approve-plan
PYTHONPATH=src python -m semantic_market_profiler.cli query --run-dir outputs/hiring-demo --query "teams that value ownership and fast learning"
PYTHONPATH=src python -m unittest discover -s tests -v
```

Use `examples/buyer-readiness/` for the second worked configuration. For real work use a fresh output directory and private inputs outside tracked example files. Reruns overwrite outputs. Retain the exact config, corpus and approval record alongside a run for reproducibility.

## Reading the output

- `source-plan.json`: config-derived plan and approval status.
- `evidence.json`: best passage per entity per signal, score and provenance.
- `profiles.json`: qualification status, matched signals and evidence. Ranking puts qualified profiles first, then signal count, then average score.
- `run.json`: counts and encoder name. It does not contain input hashes or collection history.

Entities with no matching evidence are omitted, not explicitly rejected. Compare the input universe with output IDs before reporting coverage. Inspect strong and borderline matches, check quotations against sources, and explain why rules qualified each recommendation. Revise signals from actual errors; retain prior runs for comparison.

## Capability boundary and development

`ConceptHashEncoder` is a deterministic demonstration encoder, not a production language embedding model. Raw web collection, LLM passage extraction and provider selection are not implemented. Lower-level engine functions accept an encoder, but the pipeline/CLI does not yet expose that choice. Agent research can prepare inputs when tools are available; never describe that as an automated capability of this package.

Keep configuration, evidence provenance and approval separate. Before changing runtime behavior, state the missing capability and proposed change. Preserve the two fixture workflows and run the existing tests after changes. Completion means a readable shortlist with source evidence and explicit coverage/encoder limitations, not just a successful command.
