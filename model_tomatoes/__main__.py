import argparse
import csv
import json
import os
import sys

from .core import load_reviews, scores


def _fmt(v):
    return "--" if v is None else f"{v}%"


def build_parser():
    ap = argparse.ArgumentParser(prog="model-tomatoes")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("scores")
    s.add_argument("reviews")
    m = sub.add_parser("model")
    m.add_argument("reviews")
    m.add_argument("name")
    return ap


def _run(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)
    with open(a.reviews, encoding="utf-8-sig") as fh:
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


def main(argv=None):
    """Run the CLI; a bad input file or argument exits 2 with a one-line error instead of a traceback.

    Set AGENT_ECONOMY_DEBUG=1 to see the full traceback.
    """
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    try:
        return _run(argv)
    except (OSError, ValueError, KeyError, csv.Error) as e:
        if os.environ.get("AGENT_ECONOMY_DEBUG"):
            raise
        msg = e.args[0] if isinstance(e, KeyError) and e.args else e
        print(f"error: {msg}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
