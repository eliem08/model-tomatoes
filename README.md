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

## Web app and API

Every command is also a JSON API endpoint and a browser form, served by the built-in web app.

```bash
model-tomatoes-web --port 8000          # then open http://127.0.0.1:8000
model-tomatoes-web keys create --label "first customer"   # prints an API key (stored hashed)
docker build -t model-tomatoes . && docker run -p 8000:8000 -e API_KEYS=sk_... -v model-tomatoes-data:/data model-tomatoes
```

Every API call needs `Authorization: Bearer <key>` once any key exists; a server on a public address refuses to start without one. Calls are rate-limited per key (60/min, `--rate`) and metered: `model-tomatoes-web usage` prints calls per key for billing.

Endpoints: `POST /api/scores`, `POST /api/model`, plus `GET /healthz` and `GET /api/spec` (machine-readable field list).
Files are sent as `{"name": ..., "content": ...}`, folders as `{"files": [...]}` or a base64 zip.

## Deploy and sell

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/eliem08/model-tomatoes)

`render.yaml` (one click, above) and `fly.toml` (`fly launch --copy-config`) both run the Dockerfile with a persistent `/data` volume and a `/healthz` check.
To sell self-serve, set four variables and point a Stripe webhook at `https://<your-host>/billing/webhook` (events `checkout.session.completed` and `customer.subscription.deleted`):

| Variable | Example |
|---|---|
| `STRIPE_SECRET_KEY` | `sk_live_...` |
| `STRIPE_WEBHOOK_SECRET` | `whsec_...` |
| `STRIPE_PRICES` | `community=price_123,pro=price_456,vendor-insights=price_789` |
| `PUBLIC_URL` | `https://model-tomatoes.example.com` |

Buyers pick a plan on `/pricing`, pay on Stripe Checkout and see their API key once on the success page. Cancelling the subscription revokes the key. A selling server always requires a key.

## Pricing

Every plan starts with a 14-day free trial. Prices in USD, billed monthly unless noted.

| Plan | Price | Includes |
|---|---|---|
| **Community** | $29 per month | Run your own review board; Integrity filters; Use-case scores |
| **Pro** | $149 per month | Everything in Community; Commercial use |
| **Vendor Insights** | $999 per month | Everything in Pro; Competitive review analytics; Priority support |

To start a trial or buy a plan, [request access](https://github.com/eliem08/model-tomatoes/issues/new?title=Model%20Tomatoes%20trial&labels=sales).

Plan note, owner decision on merge: there is no feature gating by plan in the code — every API key unlocks the same software (scores, model detail). Pro's embeddable meters are not built — the web app sends `X-Frame-Options: DENY`, and embeddable badges are listed as roadmap — and reviewer credibility tuning is not built either (the weight is a fixed log-of-hours formula, capped at 2,000 hours, with no tuning parameter); both have been removed from the sales copy. Vendor Insights' alerts are not built and have been removed; competitive review analytics is real in the scores table, which ranks every model in the feed side by side.

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
python -m pip wheel . --no-deps -w dist            # customer wheel, as in Quickstart
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
