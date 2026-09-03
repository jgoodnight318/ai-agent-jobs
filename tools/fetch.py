#!/usr/bin/env python3
"""Fetch AI/agent/ML remote job listings from Remote OK's public API.

Remote OK's API terms (returned in the response payload itself) require:
"Please link back (with follow, and without nofollow!) to the URL on
Remote OK and mention Remote OK as a source." Every job card we render
does exactly that. Stdlib only.
"""
from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RAW_PATH = DATA_DIR / "raw_jobs.json"
UA = "Mozilla/5.0 (compatible; ai-agent-jobs-board/1.0; +https://jgoodnight318.github.io/ai-agent-jobs/)"

TAGS = ["ai", "machine-learning"]

AGENT_KEYWORDS = re.compile(
    r"\b(ai agent|llm|large language model|prompt engineer|agentic|"
    r"generative ai|genai|rag |retrieval.augmented|langchain|autonomous agent|"
    r"copilot|chatbot|conversational ai)\b",
    re.I,
)
ML_KEYWORDS = re.compile(
    r"\b(machine learning|ml engineer|deep learning|nlp|computer vision|"
    r"data scientist|mlops|model training|neural network)\b",
    re.I,
)
# Title must plausibly be an AI/ML role. RemoteOK's "ai"/"machine-learning"
# tags catch a lot of noise (crypto trader, customer support, compliance
# analyst) that happen to share a tag with an actual ML posting somewhere
# in that company's job batch. Require the *position title itself* to
# carry an AI/ML/data signal, or fall back to a strict description check.
TITLE_RELEVANT = re.compile(
    r"\b(ai|a\.i\.|ml|machine learning|deep learning|llm|nlp|genai|"
    r"generative ai|artificial intelligence|data scientist|data science|"
    r"computer vision|prompt engineer|research engineer.*model|"
    r"applied scientist)\b",
    re.I,
)
EXCLUDE_IF_TITLE_HAS = re.compile(
    r"\b(crypto|trader|trading|compliance|customer support|sales|"
    r"recruiter|accountant|bookkeep|legal counsel|marketing manager)\b",
    re.I,
)


def fetch_tag(tag: str) -> list[dict]:
    url = f"https://remoteok.com/api?tags={tag}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"  fetch failed for tag={tag}: {e}")
        return []
    # first element is a legal/metadata blob, not a job
    return [d for d in data if isinstance(d, dict) and d.get("id")]


def categorize(job: dict) -> str:
    text = f"{job.get('position','')} {' '.join(job.get('tags', []))} {job.get('description','')[:500]}"
    if AGENT_KEYWORDS.search(text):
        return "AI Agent / LLM Engineering"
    if ML_KEYWORDS.search(text):
        return "ML / Data Science"
    return "Applied AI"


def is_relevant(job: dict) -> bool:
    title = job.get("position", "")
    if EXCLUDE_IF_TITLE_HAS.search(title):
        return False
    if TITLE_RELEVANT.search(title):
        return True
    # fall back to a strict description check only when tags plus
    # description both carry a real signal (not just a shared tag)
    desc = job.get("description", "")[:800]
    return bool(AGENT_KEYWORDS.search(desc) or ML_KEYWORDS.search(desc))


def clean_location(loc: str) -> str:
    if not loc or "Ø" in loc or "Ù" in loc:
        return "Remote / Worldwide"
    return loc


def main():
    DATA_DIR.mkdir(exist_ok=True)
    by_id: dict[str, dict] = {}
    for tag in TAGS:
        jobs = fetch_tag(tag)
        print(f"tag={tag}: {len(jobs)} jobs")
        for j in jobs:
            by_id[j["id"]] = j
        time.sleep(1)

    all_jobs = list(by_id.values())
    jobs = [j for j in all_jobs if is_relevant(j)]
    print(f"Relevance filter: {len(jobs)}/{len(all_jobs)} kept")
    for j in jobs:
        j["_category"] = categorize(j)
        j["_url"] = j.get("url") or f"https://remoteok.com/remote-jobs/{j.get('id')}"
        j["location"] = clean_location(j.get("location", ""))

    jobs.sort(key=lambda j: j.get("epoch", 0), reverse=True)

    RAW_PATH.write_text(
        json.dumps({"fetched_at": int(time.time()), "jobs": jobs}, indent=2),
        encoding="utf-8",
    )
    print(f"Saved {len(jobs)} unique jobs -> {RAW_PATH}")


if __name__ == "__main__":
    main()
