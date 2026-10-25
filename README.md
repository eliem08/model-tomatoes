<!-- sell-kit:start -->
# Model Tomatoes

[![CI](https://github.com/eliem08/model-tomatoes/actions/workflows/ci.yml/badge.svg)](https://github.com/eliem08/model-tomatoes/actions/workflows/ci.yml)

> **Real reviews of AI models from real users, not benchmarks.**

**Who it's for:** Teams choosing between AI models, and the communities that review them.

**The problem:** Benchmarks don't predict how a model performs on your use case, and open reviews get brigaded.

**What you get:** A credibility-weighted fresh/rotten meter per use case, with filters for duplicate reviewers, copied text, review bursts and inflated usage claims.

## Quickstart

Customers receive a release archive with the wheel and the examples. Python 3.10+ and no other dependencies.

```bash
pip install model_tomatoes-0.1.0-py3-none-any.whl
model-tomatoes scores examples/reviews.json
model-tomatoes model examples/reviews.json Nova-3
```

## Pricing

Every plan starts with a 14-day free trial. Prices in USD, billed monthly unless noted.

| Plan | Price | Includes |
|---|---|---|
| **Community** | $29 per month | Run your own review board; Integrity filters; Use-case scores |
| **Pro** | $149 per month | Embeddable meters; Reviewer credibility tuning; Exports |
| **Vendor Insights** | $999 per month | Competitive review analytics; Alerts; Priority support |

To start a trial or buy a plan, email **sales@YOUR-DOMAIN.com**.

## Licence

Proprietary. Copyright (c) 2026 eliem08. All rights reserved. Use requires a paid plan or an active trial; see [LICENSE](LICENSE).
<!-- sell-kit:end -->

## What it does

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

## Development

Zero runtime dependencies; Python 3.10+.

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python -m unittest discover -s tests -t .           # unit + CLI smoke tests
ruff check . && ruff format --check .               # lint + format
```

```
model_tomatoes/core.py       domain logic (pure, importable, fully tested)
model_tomatoes/__main__.py   CLI (`model-tomatoes ...` / `python -m model_tomatoes ...`)
tests/                unit tests + generated CLI smoke tests
examples/             sample inputs used by the docs and smoke tests
```

CI runs lint and tests on Ubuntu and Windows across Python 3.10, 3.12 and 3.13.
Design, data model, trade-offs and production path: **[ARCHITECTURE.md](ARCHITECTURE.md)**.

Part of the [agent-economy](https://github.com/eliem08/agent-economy) portfolio (idea #20).
