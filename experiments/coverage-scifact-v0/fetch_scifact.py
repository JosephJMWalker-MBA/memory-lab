#!/usr/bin/env python3
"""Fetch and verify the SciFact release used by coverage-scifact-v0.

Source: https://github.com/allenai/scifact (LICENSE.md).
Claims and evidence annotations: CC BY 4.0. Corpus abstracts (S2ORC): ODC-By 1.0.
Wadden et al., "Fact or Fiction: Verifying Scientific Claims", EMNLP 2020.

The data is downloaded into ./data (gitignored) and is not redistributed.
"""
import hashlib
import pathlib
import sys
import tarfile
import urllib.request


URL = "https://scifact.s3-us-west-2.amazonaws.com/release/latest/data.tar.gz"
SIZE = 3115079
SHA256 = "11c621288d41ac144d29b13b0f8503b3820b7d6e8b1f6ff24dff335c196d76be"
HERE = pathlib.Path(__file__).resolve().parent
DATA = HERE / "data"
ARCHIVE = DATA / "data.tar.gz"
EXTRACTED = DATA / "data"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    DATA.mkdir(exist_ok=True)
    if not ARCHIVE.exists():
        urllib.request.urlretrieve(URL, ARCHIVE)
    if ARCHIVE.stat().st_size != SIZE or sha256(ARCHIVE) != SHA256:
        raise SystemExit(f"checksum mismatch for {ARCHIVE}; delete it and fetch again")
    if not (EXTRACTED / "corpus.jsonl").exists():
        with tarfile.open(ARCHIVE) as tar:
            tar.extractall(DATA, filter="data")
    print(f"SciFact verified at {EXTRACTED} (sha256 {SHA256})")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FETCH_SCIFACT_FAIL: {exc}", file=sys.stderr)
        raise
