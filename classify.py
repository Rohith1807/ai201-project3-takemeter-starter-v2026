#!/usr/bin/env python3
"""
classify.py — Capstone extension: Gemini as a second classifier.

Runs posts through two classifiers side by side:
  1. Gemini (Google AI API, taxonomy definitions as the prompt — no training)
  2. Fine-tuned DistilBERT (from takemeter_out/, if present)

Each post produces a structured JSON log record. Comparison summary is
printed at the end, including agreement rate, per-label accuracy, token
counts, and an estimated cost per run.

Usage:
    python classify.py                        # all posts in test_split.csv
    python classify.py --n 10                 # first 10 posts only
    python classify.py --data labels.csv      # different input file
    python classify.py --post "some text"     # single post, no ground truth
    python classify.py --no-distilbert        # Gemini only

Requires GOOGLE_API_KEY in the environment or in a .env file in this directory.
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except (AttributeError, OSError, ValueError):
        pass

LABELS = ["analysis", "hot_take", "reaction", "request"]
MODEL_DIR = "takemeter_out"
LOG_FILE = "classify_log.jsonl"

# Condensed definitions (improvement 2: reduced from ~90 to ~55 tokens per prompt).
# Original full definitions are preserved in README taxonomy section.
DEFINITIONS = {
    "analysis": (
        "a claim backed by a specific, verifiable fact (price, count, measured time, "
        "named comparison) where that fact directly supports the claim"
    ),
    "hot_take": (
        "a confident claim without supporting data — the writer is sure but doesn't "
        "show their work; a number in the post is credentialing, not evidence"
    ),
    "reaction": (
        "immediate personal response to something just experienced — present-tense, "
        "about the moment itself, not a considered evaluation"
    ),
    "request": (
        "asking the community for advice, a recommendation, or information "
        "the writer does not already have"
    ),
}

GEMINI_PROMPT_TEMPLATE = """\
You are a classifier for posts from r/travel. Apply exactly one of these four labels:

  analysis — {analysis}
  hot_take — {hot_take}
  reaction — {reaction}
  request  — {request}

Decision rule for analysis vs. hot_take: a number is evidence when it \
quantifies a measured difference between two things (e.g., "Grab averaged \
180 THB vs. InDrive at 140 THB"). A number is credentialing when it \
describes how often the writer did something before asserting a preference \
(e.g., "I took 50+ buses" before saying which country is best). The first \
is analysis; the second is hot_take.

Post to classify:
{text}

Reply with exactly one of these four words: analysis, hot_take, reaction, request.
No punctuation, no explanation, nothing else.\
"""


def load_api_key():
    key = os.environ.get("GOOGLE_API_KEY")
    if key:
        return key
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("GOOGLE_API_KEY="):
                return line.split("=", 1)[1].strip()
    return None


def load_distilbert(model_dir):
    config = Path(model_dir) / "config.json"
    if not config.exists():
        print(f"[warn] {model_dir}/config.json not found — DistilBERT skipped.")
        print("       Re-run notebook sections 1–5 to generate the model.\n")
        return None
    try:
        from transformers import pipeline as hf_pipeline
        print(f"Loading DistilBERT from {model_dir}/…", flush=True)
        clf = hf_pipeline("text-classification", model=model_dir, top_k=None)
        print("DistilBERT ready.\n")
        return clf
    except Exception as exc:
        print(f"[warn] Could not load DistilBERT: {exc}\n", file=sys.stderr)
        return None


def run_distilbert(clf, text):
    """Returns (label, confidence, latency_ms)."""
    t0 = time.perf_counter()
    # top_k=None → list of {label, score} for every class
    scores = clf(text, truncation=True, max_length=128)[0]
    ms = (time.perf_counter() - t0) * 1000
    best = max(scores, key=lambda x: x["score"])
    return best["label"], round(best["score"], 4), round(ms, 1)


GEMINI_MODEL = "gemini-3.5-flash-lite"
# Free tier: 15 req/min → 1 request every 4.5 s to stay safely under the limit.
GEMINI_MIN_INTERVAL = 4.5
_last_gemini_call = 0.0


def run_gemini(client, text):
    """Returns (label, latency_ms, input_tokens, output_tokens)."""
    global _last_gemini_call
    wait = GEMINI_MIN_INTERVAL - (time.perf_counter() - _last_gemini_call)
    if wait > 0:
        time.sleep(wait)

    prompt = GEMINI_PROMPT_TEMPLATE.format(text=text, **DEFINITIONS)
    t0 = time.perf_counter()
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
    )
    _last_gemini_call = time.perf_counter()
    ms = (time.perf_counter() - t0) * 1000

    raw = response.text.strip().lower().replace("-", "_").replace(" ", "_")
    label = raw if raw in LABELS else f"[{raw[:30]}]"

    usage = response.usage_metadata
    in_tok = getattr(usage, "prompt_token_count", None)
    out_tok = getattr(usage, "candidates_token_count", None)
    return label, round(ms, 1), in_tok, out_tok


def classify_one(text, ground_truth, clf, gemini_client):
    record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "text": text,
        "ground_truth": ground_truth,
    }

    if clf is not None:
        try:
            db_label, db_conf, db_ms = run_distilbert(clf, text)
            record["distilbert"] = {
                "label": db_label,
                "confidence": db_conf,
                "latency_ms": db_ms,
            }
            record["distilbert_correct"] = (db_label == ground_truth)
        except Exception as exc:
            record["distilbert"] = {"error": str(exc)}
            record["distilbert_correct"] = None

    try:
        gem_label, gem_ms, in_tok, out_tok = run_gemini(gemini_client, text)
        record["gemini"] = {
            "label": gem_label,
            "latency_ms": gem_ms,
            "input_tokens": in_tok,
            "output_tokens": out_tok,
        }
        record["gemini_correct"] = (gem_label == ground_truth)
        if clf is not None and record.get("distilbert_correct") is not None:
            record["agreement"] = (db_label == gem_label)
    except Exception as exc:
        record["gemini"] = {
            "error": type(exc).__name__,
            "message": str(exc)[:300],
        }
        record["gemini_correct"] = None
        record["error"] = True

    return record


def print_summary(records, load_ms=0, total_ms=0):
    n = len(records)
    if n == 0:
        print("No records.")
        return

    errors = sum(1 for r in records if r.get("error"))
    if errors:
        print(f"[warn] {errors} record(s) logged an error — check classify_log.jsonl")

    has_db = any("distilbert" in r and "error" not in r["distilbert"] for r in records)
    gem_ok = sum(1 for r in records if r.get("gemini_correct"))

    print(f"\n{'─'*52}")
    print(f"Posts classified : {n}")
    print(f"Gemini accuracy  : {gem_ok/n:.3f}  ({gem_ok}/{n})")

    if has_db:
        db_ok = sum(1 for r in records if r.get("distilbert_correct"))
        agreed = sum(1 for r in records if r.get("agreement"))
        print(f"DistilBERT acc   : {db_ok/n:.3f}  ({db_ok}/{n})")
        print(f"Agreement rate   : {agreed/n:.3f}  ({agreed}/{n})")

    print("\nGemini per-label accuracy:")
    for label in LABELS:
        sub = [r for r in records if r["ground_truth"] == label]
        if not sub:
            continue
        ok = sum(1 for r in sub if r.get("gemini_correct"))
        print(f"  {label:<12} {ok/len(sub):.3f}  (n={len(sub)})")

    # Token cost — gemini-3.5-flash-lite: $0.10/1M input, $0.40/1M output
    in_total = sum(r["gemini"].get("input_tokens") or 0 for r in records)
    out_total = sum(r["gemini"].get("output_tokens") or 0 for r in records)
    cost = (in_total * 0.10 + out_total * 0.40) / 1_000_000
    lat_records = [r for r in records if "latency_ms" in r.get("gemini", {})]
    avg_lat = sum(r["gemini"]["latency_ms"] for r in lat_records) / len(lat_records) if lat_records else 0

    has_db = any("distilbert" in r and "error" not in r["distilbert"] for r in records)
    db_records = [r for r in records if "latency_ms" in r.get("distilbert", {})]
    avg_db_lat = sum(r["distilbert"]["latency_ms"] for r in db_records) / len(db_records) if db_records else 0
    throttle_ms = max(0, total_ms - sum(r["gemini"].get("latency_ms", 0) for r in lat_records)
                      - sum(r.get("distilbert", {}).get("latency_ms", 0) for r in db_records)
                      - load_ms) if total_ms else 0

    print(f"\nGemini tokens    : {in_total} in / {out_total} out")
    print(f"Cost (est.)      : ${cost:.6f}  (~${cost/n*1000:.4f} per 1 000 posts)")
    print(f"Avg latency      : {avg_lat:.0f} ms/post")
    if total_ms:
        print(f"\nLatency breakdown (total wall time: {total_ms/1000:.1f} s):")
        print(f"  Model load      : {load_ms:.0f} ms")
        print(f"  Gemini API      : {sum(r['gemini'].get('latency_ms',0) for r in lat_records):.0f} ms total  ({avg_lat:.0f} ms/post avg)")
        if has_db:
            print(f"  DistilBERT infer: {sum(r['distilbert']['latency_ms'] for r in db_records):.0f} ms total  ({avg_db_lat:.0f} ms/post avg)")
        print(f"  Rate-limit wait : {throttle_ms:.0f} ms  ({GEMINI_MIN_INTERVAL} s/post throttle)")
    print(f"{'─'*52}")


def main():
    parser = argparse.ArgumentParser(
        description="Gemini vs DistilBERT classifier comparison for TakeMeter.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--data", default="test_split.csv",
                        help="CSV with 'text' and 'label' columns (default: test_split.csv)")
    parser.add_argument("--post", default=None,
                        help="classify a single post text; skips --data")
    parser.add_argument("--n", type=int, default=None,
                        help="cap number of posts from --data")
    parser.add_argument("--log", default=LOG_FILE,
                        help=f"append log to this file (default: {LOG_FILE})")
    parser.add_argument("--no-distilbert", action="store_true",
                        help="skip DistilBERT, run Gemini only")
    parser.add_argument("--fast", action="store_true",
                        help="reduce rate-limit interval to 0.5 s (load test; may trigger 429)")
    args = parser.parse_args()

    api_key = load_api_key()
    if not api_key:
        print("GOOGLE_API_KEY not set. Add it to your environment or to .env",
              file=sys.stderr)
        sys.exit(1)

    try:
        from google import genai
    except ImportError:
        print("google-genai not installed. Run: pip install google-genai",
              file=sys.stderr)
        sys.exit(1)

    try:
        import pandas as pd
    except ImportError:
        print("pandas not installed. Run: pip install -r requirements.txt",
              file=sys.stderr)
        sys.exit(1)

    if args.fast:
        global GEMINI_MIN_INTERVAL
        GEMINI_MIN_INTERVAL = 0.5
        print("[load-test] Rate-limit interval reduced to 0.5 s (~120 req/min).")

    gemini_client = genai.Client(api_key=api_key)

    clf = None
    t_load_start = time.perf_counter()
    if not args.no_distilbert:
        clf = load_distilbert(MODEL_DIR)
    load_ms = (time.perf_counter() - t_load_start) * 1000

    if args.post:
        posts = [{"text": args.post, "label": "unknown"}]
    else:
        data_path = Path(args.data)
        if not data_path.exists():
            print(f"No file at {args.data}.", file=sys.stderr)
            sys.exit(1)
        df = pd.read_csv(data_path)
        if "text" not in df.columns:
            print(f"{args.data} has no 'text' column.", file=sys.stderr)
            sys.exit(1)
        if "label" not in df.columns:
            df["label"] = "unknown"
        if args.n:
            df = df.head(args.n)
        posts = df[["text", "label"]].to_dict("records")

    print(f"Classifying {len(posts)} post(s)"
          + (" [Gemini + DistilBERT]" if clf else " [Gemini only]") + "…\n")

    records = []
    log_path = Path(args.log)
    t_classify_start = time.perf_counter()
    with log_path.open("a", encoding="utf-8") as fh:
        for i, post in enumerate(posts, 1):
            print(f"  {i}/{len(posts)}", end="\r", flush=True)
            rec = classify_one(str(post["text"]), str(post["label"]), clf, gemini_client)
            records.append(rec)
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
            fh.flush()
    total_ms = (time.perf_counter() - t_classify_start) * 1000

    print(" " * 20, end="\r")
    print(f"Log appended to {log_path}  ({len(records)} new entries)")
    print_summary(records, load_ms=load_ms, total_ms=total_ms)


if __name__ == "__main__":
    main()
