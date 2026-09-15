#!/usr/bin/env python3
"""SciFact run for the coverage decision-value experiment (issue #12).

Follows PREREGISTRATION.md in this directory. Requires the data fetched and
verified by fetch_scifact.py. Retrieval is stdlib BM25 and sentence-level
TF-IDF; decisions, coverage states, and scoring come from
tests/run_coverage_scifact_v0.py.
"""
import json
import math
import pathlib
import platform
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(HERE))

from fetch_scifact import EXTRACTED, SHA256, URL  # noqa: E402
from fetch_scifact import main as fetch  # noqa: E402
from run_coverage_scifact_v0 import (  # noqa: E402
    BOOTSTRAP_RESAMPLES,
    BOOTSTRAP_SEED,
    KS,
    PRIMARY_K,
    RESULTS,
    WEIGHTS,
    analyze,
    collection_truth,
    normalize,
)

BM25_K1 = 0.9
BM25_B = 0.4
TOP_N = max(KS)
STOPWORDS = frozenset(
    """a about above after again against all am an and any are as at be because been
    before being below between both but by can could did do does doing down during each
    few for from further had has have having he her here hers herself him himself his
    how i if in into is it its itself just me more most my myself no nor not now of off
    on once only or other our ours ourselves out over own same she should so some such
    than that the their theirs them themselves then there these they this those through
    to too under until up very was we were what when where which while who whom why will
    with you your yours yourself yourselves""".split()
)


def tokenize(text):
    return [token for token in re.findall(r"[a-z0-9]+", text.lower()) if token not in STOPWORDS]


class BM25:
    def __init__(self, documents):
        self.doc_ids = [doc_id for doc_id, _ in documents]
        self.lengths = [len(tokens) for _, tokens in documents]
        self.avgdl = sum(self.lengths) / len(documents)
        self.postings = defaultdict(list)
        for index, (_, tokens) in enumerate(documents):
            for term, tf in Counter(tokens).items():
                self.postings[term].append((index, tf))
        n = len(documents)
        self.idf = {
            term: math.log(1 + (n - len(postings) + 0.5) / (len(postings) + 0.5))
            for term, postings in self.postings.items()
        }

    def search(self, tokens, n):
        scores = defaultdict(float)
        for term, qtf in Counter(tokens).items():
            for index, tf in self.postings.get(term, ()):
                norm = tf + BM25_K1 * (1 - BM25_B + BM25_B * self.lengths[index] / self.avgdl)
                scores[index] += qtf * self.idf[term] * tf * (BM25_K1 + 1) / norm
        ranked = sorted(scores.items(), key=lambda item: (-item[1], self.doc_ids[item[0]]))[:n]
        return [[self.doc_ids[index], round(score, 4)] for index, score in ranked]


class SentenceTfidf:
    def __init__(self, corpus):
        sentences = []
        for doc in corpus:
            for text in [doc["title"]] + list(doc["abstract"]):
                tokens = tokenize(text)
                if tokens:
                    sentences.append((doc["doc_id"], Counter(tokens)))
        df = Counter()
        for _, tf in sentences:
            df.update(tf.keys())
        total = len(sentences)
        self.idf = {term: math.log((1 + total) / (1 + count)) + 1 for term, count in df.items()}
        self.sentence_doc = []
        self.postings = defaultdict(list)
        for index, (doc_id, tf) in enumerate(sentences):
            weights = {term: count * self.idf[term] for term, count in tf.items()}
            norm = math.sqrt(sum(value * value for value in weights.values()))
            self.sentence_doc.append(doc_id)
            for term, value in weights.items():
                self.postings[term].append((index, value / norm))

    def search(self, tokens, n):
        weights = {term: count * self.idf[term] for term, count in Counter(tokens).items() if term in self.idf}
        norm = math.sqrt(sum(value * value for value in weights.values())) or 1.0
        sentence_scores = defaultdict(float)
        for term, value in weights.items():
            for index, weight in self.postings[term]:
                sentence_scores[index] += (value / norm) * weight
        doc_scores = {}
        for index, score in sentence_scores.items():
            doc_id = self.sentence_doc[index]
            if score > doc_scores.get(doc_id, 0.0):
                doc_scores[doc_id] = score
        ranked = sorted(doc_scores.items(), key=lambda item: (-item[1], item[0]))[:n]
        return [[doc_id, round(score, 4)] for doc_id, score in ranked]


def load_jsonl(path):
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle]


def rank_claims(claims, bm25, tfidf):
    records = []
    for claim in claims:
        evidence = {}
        for doc_id, entries in claim["evidence"].items():
            labels = {entry["label"] for entry in entries}
            assert len(labels) == 1, (claim["id"], doc_id)
            evidence[int(doc_id)] = labels.pop()
        tokens = tokenize(claim["claim"])
        records.append(
            {
                "id": claim["id"],
                "truth": collection_truth(evidence),
                "evidence": {str(doc_id): label for doc_id, label in sorted(evidence.items())},
                "p1": bm25.search(tokens, TOP_N),
                "p2": tfidf.search(tokens, TOP_N),
            }
        )
    return records


def memory_lab_commit():
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    dirty = subprocess.run(["git", "status", "--porcelain"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    return {"head": head, "working_tree_dirty": bool(dirty)}


def main():
    fetch()
    corpus = load_jsonl(EXTRACTED / "corpus.jsonl")
    train_raw = load_jsonl(EXTRACTED / "claims_train.jsonl")
    dev_raw = load_jsonl(EXTRACTED / "claims_dev.jsonl")
    commit = memory_lab_commit()

    bm25 = BM25([(doc["doc_id"], tokenize(doc["title"] + " " + " ".join(doc["abstract"]))) for doc in corpus])
    tfidf = SentenceTfidf(corpus)
    train = rank_claims(train_raw, bm25, tfidf)
    dev = rank_claims(dev_raw, bm25, tfidf)
    universe_size = len(corpus)

    analysis = analyze([normalize(c) for c in train], [normalize(c) for c in dev], universe_size)
    truth_counts = {
        split: dict(sorted(Counter(record["truth"] for record in records).items()))
        for split, records in (("train", train), ("dev", dev))
    }
    result = {
        "experiment": "coverage-scifact-v0",
        "status": "executed",
        "preregistration": "experiments/coverage-scifact-v0/PREREGISTRATION.md",
        "run_at": datetime.now(timezone.utc).isoformat(),
        "environment": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "memory_lab_commit": commit,
        },
        "data": {
            "url": URL,
            "sha256": SHA256,
            "licenses": {
                "claims_and_evidence_annotations": "CC BY 4.0",
                "corpus_abstracts": "ODC-By 1.0 (S2ORC)",
            },
            "attribution": "Wadden et al., Fact or Fiction: Verifying Scientific Claims, EMNLP 2020",
            "recorded_here": "claim ids, collection truth, evidence document ids with labels, and top-20 ranked document ids with scores; no claim or abstract text",
            "truth_counts": truth_counts,
        },
        "parameters": {
            "bm25": {"k1": BM25_K1, "b": BM25_B, "fields": "title + abstract"},
            "audit": "TF-IDF cosine at sentence level (title as a sentence), smooth IDF over sentences, document score = best sentence",
            "tokenizer": "lowercase alphanumeric runs, fixed English stopword list, no stemming",
            "top_n_recorded": TOP_N,
            "ks": list(KS),
            "primary_k": PRIMARY_K,
            "weights": list(WEIGHTS),
            "universe_size": universe_size,
            "bootstrap": {"resamples": BOOTSTRAP_RESAMPLES, "seed": BOOTSTRAP_SEED},
        },
        **analysis,
        "claims": {"train": train, "dev": dev},
    }
    RESULTS.parent.mkdir(parents=True, exist_ok=True)
    RESULTS.write_text(json.dumps(result, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    summary = {
        "truth_counts": truth_counts,
        "by_k": {
            k: {
                "tau": block["tau"],
                "recall": block["recall"],
                "U3": {arm: values["utility"]["U3"] for arm, values in block["arms"].items()},
                "coverage": block["coverage"],
            }
            for k, block in analysis["by_k"].items()
        },
        "primary_counts": {arm: values["counts"] for arm, values in analysis["by_k"][str(PRIMARY_K)]["arms"].items()},
        "ceiling": analysis["ceiling"],
        "predictions": {name: item["held"] for name, item in analysis["predictions"].items()},
        "bootstrap_U3": analysis["bootstrap_U3"],
        "memory_lab_commit": commit,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
