"""Review aggregation with credibility weighting and integrity filters."""

from __future__ import annotations

import math
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta

__all__ = ["Review", "load_reviews", "filter_reviews", "scores", "FRESH_THRESHOLD"]

FRESH_THRESHOLD = 3.5
CERTIFIED = (0.75, 20)
MAX_HOURS = 2000  # self-reported usage; past ~a year of daily use more hours add no credibility
KINDS = {"critic", "audience"}


@dataclass
class Review:
    model: str
    reviewer: str
    kind: str
    rating: float
    tags: list
    hours: float
    text: str
    ts: datetime
    flags: list = field(default_factory=list)

    @property
    def fresh(self) -> bool:
        return self.rating >= FRESH_THRESHOLD

    @property
    def weight(self) -> float:
        return 1 + math.log1p(min(max(self.hours, 0), MAX_HOURS))  # capped: one claim can't swing a score


def load_reviews(items: list[dict]) -> list[Review]:
    if not isinstance(items, list) or not all(isinstance(i, dict) for i in items):
        raise ValueError("reviews must be a JSON list of review objects")
    out = []
    for i in items:
        rating, hours = float(i["rating"]), float(i.get("hours", 0))
        kind = str(i.get("kind", "audience")).strip().lower()
        if not (math.isfinite(rating) and 0 <= rating <= 5):
            raise ValueError(f"rating must be 0-5, got {i['rating']!r}")
        if not (math.isfinite(hours) and hours >= 0):
            raise ValueError(f"hours must be a finite number >= 0, got {i.get('hours')!r}")
        if kind not in KINDS:
            raise ValueError(f"kind must be one of {sorted(KINDS)}, got {i.get('kind')!r}")
        reviewer = " ".join(str(i["reviewer"]).split()).casefold()  # "Alice" and "alice " are one reviewer
        out.append(
            Review(
                i["model"],
                reviewer,
                kind,
                rating,
                i.get("tags", []),
                hours,
                i.get("text", ""),
                datetime.fromisoformat(i["ts"]),
            )
        )
    return out


def _shingles(text, k=3):
    words = re.findall(r"\w+", text.lower())
    return {tuple(words[i : i + k]) for i in range(max(1, len(words) - k + 1))}


def _jaccard(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


def filter_reviews(
    reviews: list[Review], burst_window=timedelta(hours=1), burst_size=5
) -> tuple[list[Review], list[Review]]:
    """Return (kept, rejected) after one-per-reviewer, near-duplicate and burst checks."""
    kept, rejected, seen = [], [], set()
    by_model = defaultdict(list)
    for r in sorted(reviews, key=lambda r: r.ts):
        key = (r.model, r.reviewer)
        if key in seen:
            r.flags.append("duplicate reviewer")
            rejected.append(r)
            continue
        seen.add(key)
        sh = _shingles(r.text)
        if len(r.text.split()) >= 4 and any(
            _jaccard(sh, _shingles(o.text)) > 0.8 for o in by_model[r.model] if o.reviewer != r.reviewer
        ):
            r.flags.append("near-duplicate text")
            rejected.append(r)
            continue
        by_model[r.model].append(r)
        kept.append(r)
    # brigading: >= burst_size same-polarity audience reviews inside the window
    final = []
    for _model, items in by_model.items():
        aud = [r for r in items if r.kind == "audience"]
        burst_ids = set()
        for i, r in enumerate(aud):
            window = [o for o in aud[i:] if o.ts - r.ts <= burst_window and o.fresh == r.fresh]
            if len(window) >= burst_size:
                burst_ids.update(id(o) for o in window)
        for r in items:
            if id(r) in burst_ids:
                r.flags.append("review burst")
                rejected.append(r)
            else:
                final.append(r)
    return final, rejected


def _meter(rs: list[Review]):
    if not rs:
        return None
    total = sum(r.weight for r in rs)
    return round(100 * sum(r.weight for r in rs if r.fresh) / total)


def scores(reviews: list[Review]) -> dict:
    kept, rejected = filter_reviews(reviews)
    out = {}
    for model in sorted({r.model for r in kept}):
        rs = [r for r in kept if r.model == model]
        critics = [r for r in rs if r.kind == "critic"]
        audience = [r for r in rs if r.kind == "audience"]
        tomato = _meter(critics)
        tags = defaultdict(list)
        for r in rs:
            for t in r.tags:
                tags[t].append(r)
        out[model] = {
            "tomatometer": tomato,
            "audience": _meter(audience),
            "critic_reviews": len(critics),
            "audience_reviews": len(audience),
            "certified_fresh": tomato is not None and tomato >= CERTIFIED[0] * 100 and len(critics) >= CERTIFIED[1],
            "label": None if tomato is None else ("fresh" if tomato >= 60 else "rotten"),
            "by_use_case": {t: {"score": _meter(v), "n": len(v)} for t, v in sorted(tags.items())},
            "rejected": sum(1 for r in rejected if r.model == model),
        }
    return out
