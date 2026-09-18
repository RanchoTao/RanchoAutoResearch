"""Resumable, byte-verified prefetch into the Hugging Face content cache."""

from __future__ import annotations

import argparse
import concurrent.futures
import os
import re
import time
from pathlib import Path

import requests


CACHE = Path.home() / ".cache" / "huggingface" / "hub"


def metadata(repo: str, revision: str) -> tuple[str, int, str]:
    url = f"https://huggingface.co/{repo}/resolve/{revision}/pytorch_model.bin"
    response = requests.head(url, allow_redirects=False, timeout=(15, 30))
    response.raise_for_status()
    etag = response.headers.get("X-Linked-ETag", "").strip('"')
    size = int(response.headers["X-Linked-Size"])
    commit = response.headers["X-Repo-Commit"]
    if not re.fullmatch(r"[0-9a-f]{64}", etag):
        raise RuntimeError(f"Invalid ETag for {repo}@{revision}: {etag!r}")
    return etag, size, commit


def download_one(repo: str, revision: str, attempts: int = 100) -> dict:
    etag, expected, commit = metadata(repo, revision)
    cache_repo = "models--" + repo.replace("/", "--")
    target = CACHE / cache_repo / "blobs" / f"{etag}.incomplete"
    final = target.with_suffix("")
    target.parent.mkdir(parents=True, exist_ok=True)
    if final.exists() and final.stat().st_size == expected:
        return {"repo": repo, "revision": revision, "commit": commit, "etag": etag, "bytes": expected, "status": "already-complete"}

    last_report = -1
    for attempt in range(1, attempts + 1):
        current = target.stat().st_size if target.exists() else 0
        if current == expected:
            return {"repo": repo, "revision": revision, "commit": commit, "etag": etag, "bytes": current, "status": "prefetched"}
        if current > expected:
            raise RuntimeError(f"Oversized partial file {target}: {current}>{expected}")
        headers = {"Range": f"bytes={current}-"} if current else {}
        url = f"https://huggingface.co/{repo}/resolve/{revision}/pytorch_model.bin"
        try:
            with requests.get(url, headers=headers, stream=True, timeout=(15, 30)) as response:
                response.raise_for_status()
                if current and response.status_code != 206:
                    raise RuntimeError(f"Server ignored Range at {current}: HTTP {response.status_code}")
                mode = "ab" if current else "wb"
                with target.open(mode) as handle:
                    for chunk in response.iter_content(chunk_size=8 * 1024 * 1024):
                        if not chunk:
                            continue
                        handle.write(chunk)
                        handle.flush()
                        now = handle.tell()
                        bucket = now // (32 * 1024 * 1024)
                        if bucket != last_report:
                            print(f"PREFETCH {repo}@{revision} {now}/{expected} attempt={attempt}", flush=True)
                            last_report = bucket
        except (requests.RequestException, OSError, RuntimeError) as error:
            current = target.stat().st_size if target.exists() else 0
            print(f"RESUME {repo}@{revision} offset={current} error={type(error).__name__}: {error}", flush=True)
            time.sleep(min(attempt, 5))
            continue
    raise RuntimeError(f"Exceeded retry budget for {repo}@{revision}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", required=True, type=int)
    parser.add_argument("--steps", required=True, nargs="+", type=int)
    parser.add_argument("--workers", type=int, default=3)
    args = parser.parse_args()
    repo = f"EleutherAI/pythia-160m-seed{args.seed}"
    revisions = [f"step{step}" for step in args.steps]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(download_one, repo, revision) for revision in revisions]
        for future in concurrent.futures.as_completed(futures):
            print(f"COMPLETE {future.result()}", flush=True)


if __name__ == "__main__":
    main()

