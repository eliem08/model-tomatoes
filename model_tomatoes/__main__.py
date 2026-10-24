import argparse
import json
import sys

from .core import load_reviews, scores


def _fmt(v):
    return "--" if v is None else f"{v}%"


def main(argv=None):
    ap = argparse.ArgumentParser(prog="model-tomatoes")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scores")
    s.add_argument("reviews")
    m = sub.add_parser("model")
    m.add_argument("reviews")
    m.add_argument("name")
    a = ap.parse_args(argv)
    with open(a.reviews, encoding="utf-8") as fh:
        sc = scores(load_reviews(json.load(fh)))
    if a.cmd == "scores":
        print(f"{'model':<14}{'tomatometer':>12}{'audience':>10}  label")
        for name, s in sorted(sc.items(), key=lambda kv: -(kv[1]["tomatometer"] or 0)):
            badge = "CERTIFIED FRESH" if s["certified_fresh"] else (s["label"] or "").upper()
            print(f"{name:<14}{_fmt(s['tomatometer']):>12}{_fmt(s['audience']):>10}  {badge}")
        return 0
    s = sc.get(a.name)
    if not s:
        print("no reviews", file=sys.stderr)
        return 1
    print(json.dumps(s, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
