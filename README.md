# model-tomatoes

> **Rotten Tomatoes for AI models** — real reviews instead of benchmarks.

Benchmarks are saturated and gamed. What people actually want to know is
"is this model good at *my* thing?" `model-tomatoes` aggregates reviews from
practitioners — tagged by use case and weighted by verified usage — into a
Tomatometer (critics), an Audience Score, and per-use-case scores.

## What the MVP does

- **Reviews**: model, reviewer, `critic` (verified practitioner) or `audience`,
  rating 0–5, use-case tags (`coding`, `writing`, `agents`, `rag`…), text, timestamp,
  verified usage hours
- **Tomatometer** = % of critic reviews that are *fresh* (≥ 3.5), weighted by credibility
  (log of verified usage hours)
- **Audience Score** the same over audience reviews
- **Certified Fresh**: Tomatometer ≥ 75% with ≥ 20 critic reviews
- **Per-use-case** scores ("great at coding, rotten at long-form writing")
- **Integrity filters**: duplicate / near-duplicate text, review bursts
  (brigading: many reviews within an hour with the same polarity), one review
  per reviewer per model

## Quickstart

```bash
pip install -e .
model-tomatoes scores examples/reviews.json
model-tomatoes model examples/reviews.json "Nova-3"
```

## Roadmap

- Verified usage via API-key-signed attestations (proof you actually used it)
- Side-by-side "critics consensus" summaries generated from review text
- Embeddable badges for model cards
