import json
import pathlib
import unittest
from datetime import datetime, timedelta

from model_tomatoes import load_reviews, scores

EX = json.loads((pathlib.Path(__file__).resolve().parent.parent / "examples" / "reviews.json").read_text())


def rv(model="M", reviewer="r", kind="critic", rating=4, tags=("coding",), hours=10, text="solid", ts=None):
    return {
        "model": model,
        "reviewer": reviewer,
        "kind": kind,
        "rating": rating,
        "tags": list(tags),
        "hours": hours,
        "text": text,
        "ts": (ts or datetime(2026, 10, 1)).isoformat(),
    }


class Tests(unittest.TestCase):
    def test_example(self):
        s = scores(load_reviews(EX))["Nova-3"]
        self.assertEqual(s["critic_reviews"], 3)
        self.assertGreater(s["tomatometer"], 60)
        self.assertEqual(s["by_use_case"]["writing"]["score"], 0)
        self.assertEqual(s["by_use_case"]["coding"]["score"], 100)

    def test_certified_fresh(self):
        items = [
            rv(
                reviewer=f"r{i}",
                rating=4.5,
                text=f"unique review number {i} with details",
                ts=datetime(2026, 10, 1) + timedelta(days=i),
            )
            for i in range(20)
        ]
        self.assertTrue(scores(load_reviews(items))["M"]["certified_fresh"])

    def test_credibility_weighting(self):
        items = [
            rv(reviewer="pro", rating=5, hours=1000, text="great model overall here"),
            rv(reviewer="drive-by", rating=1, hours=0, text="terrible awful bad"),
        ]
        self.assertGreater(scores(load_reviews(items))["M"]["tomatometer"], 50)

    def test_integrity_filters(self):
        t = datetime(2026, 10, 1)
        items = [rv(reviewer="a", text="first one"), rv(reviewer="a", text="second one")]
        items += [
            rv(reviewer=f"bot{i}", kind="audience", rating=1, text=f"bad {i}", ts=t + timedelta(minutes=i))
            for i in range(6)
        ]
        items += [
            rv(reviewer="copy1", text="this model writes amazing python code daily"),
            rv(reviewer="copy2", text="this model writes amazing python code daily"),
        ]
        s = scores(load_reviews(items))["M"]
        self.assertEqual(s["rejected"], 1 + 6 + 1)
        self.assertIsNone(s["audience"])

    def test_one_inflated_hours_claim_cannot_swing_the_meter(self):
        honest = [rv(reviewer=f"c{i}", rating=5, hours=200, text=f"good model number {i} here") for i in range(4)]
        shill = rv(reviewer="shill", rating=1, hours=1e300, text="worst model ever made today")
        self.assertGreaterEqual(scores(load_reviews([*honest, shill]))["M"]["tomatometer"], 70)

    def test_reviewer_identity_is_normalised(self):
        items = [rv(reviewer="Alice", text="first take on it"), rv(reviewer=" alice ", text="second take on it")]
        self.assertEqual(scores(load_reviews(items))["M"]["rejected"], 1)

    def test_bad_ratings_hours_and_kinds_are_rejected(self):
        for bad in ({"rating": 50}, {"rating": float("nan")}, {"hours": -3}, {"kind": "influencer"}):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                load_reviews([{**rv(), **bad}])


if __name__ == "__main__":
    unittest.main()
