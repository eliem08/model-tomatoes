# Architecture — model-tomatoes

## 1. Scope
Practitioner reviews of AI models aggregated into trustworthy scores per use case.
**MVP:** reviews with use-case tags and verified hours, integrity filters (one per reviewer,
near-duplicate text, review bursts), credibility-weighted Tomatometer and Audience scores,
Certified Fresh, per-use-case scores.
**Product:** usage-verified reviewers (API-key attestations), consensus summaries, embeddable badges.

## 2. Pipeline
```mermaid
flowchart LR
  Reviews --> Dedupe[One per reviewer per model]
  Dedupe --> NearDup[3-gram Jaccard > 0.8]
  NearDup --> Burst[Brigading: ≥5 same-polarity audience reviews within 1h]
  Burst --> Score[Weighted meters]
  Score --> Pages[Model pages + badges]
```

## 3. Scoring
- fresh = rating ≥ 3.5
- weight = `1 + ln(1 + verified_hours)`, so a 1,000-hour practitioner counts about 8× a drive-by,
  but no single reviewer dominates
- meter = weighted % fresh. Certified Fresh requires ≥ 75% and ≥ 20 critic reviews.
- the same meter is computed per use-case tag, which is the product's real value
  ("great at coding, rotten at writing")

## 4. Design decisions
- **Integrity filters run before scoring and are reported** (`rejected` count). Transparency is
  the moat against review gaming.
- **Log weighting, not linear.** It rewards expertise while resisting whales.
- **Critic vs. audience split** mirrors the Rotten Tomatoes mental model users already have.

## 5. Production architecture
Postgres (reviews, reviewers, attestations), a scoring job on write (incremental per model),
MinHash-LSH for near-duplicate detection at scale, and a CDN-cached read API for badges.

## 6. Risks
Labs astroturfing (verification tied to real API usage, burst detection, reviewer reputation).
Model versioning: reviews attach to `model@version`, and pages show the version trend.
