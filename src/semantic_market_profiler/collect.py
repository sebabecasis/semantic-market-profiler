"""Collect only the explicitly reviewed entity/source URL inventory."""
from .providers import chunks, digest, extract_passages, scrape


def collect(config, approved_hash, *, fetch=scrape, extractor=extract_passages):
    if digest(config) != approved_hash:
        raise PermissionError("Configuration changed since review; approve the new plan hash")
    sources = config.get("collection", [])
    if not sources:
        raise ValueError("Config collection must contain reviewed entity/source URL records")
    allowed = {source["kind"] for source in config["sources"]}
    required = {"entity_id", "entity_name", "domain", "source_url", "source_kind"}
    for row in sources:
        if not required.issubset(row) or row["source_kind"] not in allowed:
            raise ValueError("Collection row has missing identity fields or unplanned source kind")
    passages, failures = [], []
    for source in sources:
        try:
            page = fetch(source["source_url"])
            model = config.get("extraction_model")
            texts = extractor(page["text"], config["research_question"], model=model) if model else chunks(page["text"])
            for text in texts:
                passages.append({**{k: source[k] for k in required}, "text": text})
        except Exception as exc:
            failures.append({"entity_id": source["entity_id"], "source_url": source["source_url"], "error": type(exc).__name__})
    return {"config_hash": approved_hash, "passages": passages, "failures": failures,
            "sources_requested": len(sources), "sources_succeeded": len(sources) - len(failures)}
