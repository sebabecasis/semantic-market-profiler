# Architecture

```text
open-ended market question
          │
          ▼
proposed source plan + signal model
          │
          ▼
     operator review ───────────────┐
          │ approve / edit          │
          ▼                         │
first-party passages with provenance
          │                         │
          ▼                         │
semantic evidence per entity × signal
          │                         │
          ▼                         │
editable post-qualification rules ◄─┘
          │
          ▼
ranked profiles + exact evidence + query interface
```

## What was generalised

The source implementation asked which London technology companies hire for particular behaviours. Its reusable idea is broader: define a market attribute, identify the text most likely to contain evidence, extract attributable passages, search semantically and post-qualify with rules the operator can inspect.

Hiring philosophy is now one configuration. The second example looks for evidence of governed-workflow readiness across jobs, operations and trust pages.

## Provider boundaries

The safe demo starts from fixture passages and uses a deterministic local encoder. Production adapters can replace collection, LLM extraction and embeddings without changing the plan, evidence, qualification or query contracts.

The system deliberately requires explicit plan approval. Source selection and enrichment logic are proposed working objects, not hidden model behaviour.
