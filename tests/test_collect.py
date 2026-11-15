import contextlib
import io
import json
import os
import tempfile
import unittest

from model_tomatoes.__main__ import main
from model_tomatoes.collect import Store


def run(*argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
        code = main(list(argv))
    return code, out.getvalue()


class CollectTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.store = os.path.join(self.tmp.name, "store.json")

    def tearDown(self):
        self.tmp.cleanup()

    def test_only_the_operator_makes_critics(self):
        st = Store(self.store)
        self.assertIn("audience", st.add_review("Nova-3", "ana", 4.5, "great"))
        st.add_critic("Ana ")
        self.assertIn("critic", st.add_review("Nova-3", "ANA", 4.0, "still great"))
        self.assertEqual(len(st.doc["reviews"]), 1)  # same person, same model: updated, not added

    def test_invalid_reviews_are_rejected_and_not_stored(self):
        st = Store(self.store)
        for rating in (9, -1, float("nan")):
            with self.subTest(rating=rating), self.assertRaises(ValueError):
                st.add_review("Nova-3", "bo", rating)
        with self.assertRaises(ValueError):
            st.add_review("", "bo", 3)
        self.assertEqual(st.doc["reviews"], [])

    def test_cli_collects_then_scores_the_store(self):
        self.assertEqual(run("critic-add", "ana", "--store", self.store)[0], 0)
        run("review", "Nova-3", "--reviewer", "ana", "--rating", "4.5", "--text", "solid", "--store", self.store)
        run("review", "Nova-3", "--reviewer", "bo", "--rating", "2", "--store", self.store)
        code, out = run("scores", "--store", self.store)
        self.assertEqual(code, 0, out)
        self.assertIn("Nova-3", out)
        code, out = run("model", "Nova-3", "--store", self.store)
        self.assertEqual(json.loads(out)["tomatometer"], 100)

    def test_review_files_still_work(self):
        example = os.path.join(os.path.dirname(__file__), "..", "examples", "reviews.json")
        code, out = run("scores", example)
        self.assertEqual(code, 0)
        self.assertIn("Nova-3", out)


if __name__ == "__main__":
    unittest.main()
