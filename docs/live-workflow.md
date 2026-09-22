# Reviewed collection and production embeddings

The agent translates the objective into sources, semantic signals and qualification rules. planner.py serializes that decision; it does not autonomously invent a research plan.

Copy an example config into a private run directory and add a bounded collection inventory:

```json
{
  "collection": [
    {
      "entity_id": "example",
      "entity_name": "Example",
      "domain": "example.com",
      "source_url": "https://example.com/careers",
      "source_kind": "careers"
    }
  ],
  "extraction_model": "your-openrouter-model-id"
}
```

These fields extend the existing config; they are not a complete standalone config. Omit extraction_model to use exact contiguous text chunks without an LLM extraction call. Kind must match the reviewed sources list. The agent/operator supplies actual source URLs; no automatic company discovery is implied.

1. Run plan and review its config_hash, inventory, thresholds and likely cost.
2. With approval, collect via Firecrawl. An optional OpenRouter extraction call selects only verbatim source substrings.
3. Inspect collection.json. Failures are retained with source identity and a nonzero exit. Decide whether to fix them or explicitly accept incomplete coverage.
4. Run real embeddings with the same reviewed hash.
5. Query evidence using the provider/model/dimensions recorded in run.json.

```bash
PYTHONPATH=src python -m semantic_market_profiler.cli plan --config /private/run/config.json --out outputs/live
PYTHONPATH=src python -m semantic_market_profiler.cli collect --config /private/run/config.json --approved-plan-hash <reviewed-hash> --out outputs/live
PYTHONPATH=src python -m semantic_market_profiler.cli run --config /private/run/config.json --corpus outputs/live/corpus.json --out outputs/live --approve-plan --approved-plan-hash <reviewed-hash> --encoder openai
PYTHONPATH=src python -m semantic_market_profiler.cli query --run-dir outputs/live --query "the attribute to explore"
```

Environment: FIRECRAWL_API_KEY for collection; OPENROUTER_API_KEY only for model extraction; OPENAI_API_KEY for real embeddings. Embedding defaults are text-embedding-3-small, 1536 dimensions; --model and --dimensions are explicit overrides. Credentials are read from environment, not .env automatically.

Vectors are validated and normalized; content/model/dimension-addressed caches avoid repeated successful embedding requests. Queries use the saved embedding specification. Input hashes and full snapshots make the run auditable. Config/corpus snapshots and caches may contain sensitive text: do not publish run folders.

Profiles include no_evidence entities from the reviewed inventory even if collection yielded no passages. This is missing support, not disqualification. Qualification rules still determine the ranking; cosine values are not probabilities, and demo thresholds need calibration on real vectors.

These provider contracts have offline mocked tests. No paid collection or live-account acceptance test is performed by the test suite.
