"""Collect reviews into a store: one per reviewer per model, critic status granted by the operator only."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone

from .core import load_reviews


def _norm(name: str) -> str:
    return " ".join(str(name).split()).casefold()


class Store:
    def __init__(self, path: str):
        self.path = path
        try:
            with open(path, encoding="utf-8-sig") as fh:
                doc = json.load(fh)
        except FileNotFoundError:
            doc = {"reviews": [], "critics": []}
        if not isinstance(doc, dict) or not isinstance(doc.get("reviews"), list):
            raise ValueError(f"{path}: not a review store")
        doc.setdefault("critics", [])
        self.doc = doc

    def add_critic(self, name: str) -> bool:
        name = _norm(name)
        if not name:
            raise ValueError("critic name is required")
        if name in self.doc["critics"]:
            return False
        self.doc["critics"].append(name)
        return True

    def add_review(self, model: str, reviewer: str, rating: float, text: str = "", tags=(), hours: float = 0) -> str:
        """Validate and store a review; a second review by the same person replaces their first."""
        model, who = " ".join(str(model).split()), _norm(reviewer)
        if not model or not who:
            raise ValueError("model and reviewer are required")
        item = {
            "model": model,
            "reviewer": who,
            # self-declared critics would let anyone swing the tomatometer
            "kind": "critic" if who in self.doc["critics"] else "audience",
            "rating": rating,
            "tags": [t.strip().lower() for t in tags if t.strip()],
            "hours": hours,
            "text": " ".join(str(text).split())[:2000],
            "ts": datetime.now(timezone.utc).replace(tzinfo=None).isoformat(timespec="seconds"),
        }
        load_reviews([item])  # same validation as imported review files
        rest = [r for r in self.doc["reviews"] if not (r["model"] == model and _norm(r["reviewer"]) == who)]
        replaced = len(rest) != len(self.doc["reviews"])
        self.doc["reviews"] = [*rest, item]
        return f"{'updated' if replaced else 'added'} {item['kind']} review of {model}: {rating}/5"

    def save(self):
        tmp = f"{self.path}.tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(self.doc, fh, indent=2)
        os.replace(tmp, self.path)
