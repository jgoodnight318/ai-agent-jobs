#!/usr/bin/env python3
"""Build the AI Agent Jobs static site from data/raw_jobs.json.
Stdlib only. Output -> docs/ for GitHub Pages.
"""
from __future__ import annotations

import html
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "raw_jobs.json"
DOCS = ROOT / "docs"
SITE_NAME = "AI Agent Jobs"
SITE_URL = "https://jgoodnight318.github.io/ai-agent-jobs"
GUMROAD_POST_URL = "https://goodnightdreams32.gumroad.com/l/ai-agent-jobs-featured-post"

CSS = """
:root{--ink:#14181f;--sub:#5a6472;--line:#e4e7ec;--accent:#7c3aed;--bg:#fafbfc;--card:#fff}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;color:var(--ink);background:var(--bg);line-height:1.55}
.wrap{max-width:900px;margin:0 auto;padding:0 20px}
header.site{border-bottom:1px solid var(--line);background:var(--card)}
header.site .wrap{padding:18px 20px}
header.site a.brand{font-weight:700;text-decoration:none;color:var(--ink);font-size:18px}
header.site nav{margin-top:8px;font-size:14px}
header.site nav a{color:var(--sub);text-decoration:none;margin-right:14px}
header.site nav a:hover{color:var(--accent)}
main{padding:28px 0 60px}
h1{font-size:26px;margin:0 0 6px}
h2{font-size:18px;margin:24px 0 10px}
p.lede{color:var(--sub);margin:0 0 20px;font-size:15px}
.stat-row{display:flex;gap:14px;flex-wrap:wrap;margin:18px 0 22px}
.stat{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 16px;min-width:120px}
.stat b{display:block;font-size:22px}
.stat span{color:var(--sub);font-size:12.5px}
#q{width:100%;padding:12px 14px;font-size:15px;border:1px solid var(--line);border-radius:8px;margin:10px 0 10px}
.tabs{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:16px}
.tab{border:1px solid var(--line);background:var(--card);border-radius:999px;padding:6px 14px;font-size:13px;cursor:pointer;color:var(--sub)}
.tab.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.job{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px 16px;margin-bottom:10px}
.job h3{margin:0 0 3px;font-size:16px}
.job h3 a{color:var(--ink);text-decoration:none}
.job h3 a:hover{color:var(--accent)}
.job .meta{color:var(--sub);font-size:13px;margin-bottom:6px}
.job .tags{margin-bottom:6px}
.tagchip{display:inline-block;background:#f1eefe;color:var(--accent);border-radius:999px;padding:2px 9px;font-size:11.5px;margin:0 4px 4px 0}
.job .apply{font-size:13px}
.job .apply a{color:var(--accent);font-weight:600;text-decoration:none}
.job .apply a:hover{text-decoration:underline}
.job .via{color:var(--sub);font-size:12px}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:18px 20px;margin:18px 0}
.cta{display:inline-block;background:var(--accent);color:#fff;text-decoration:none;padding:10px 18px;border-radius:8px;font-weight:600;font-size:14px;margin-top:10px}
.cta:hover{opacity:.9}
footer{border-top:1px solid var(--line);color:var(--sub);font-size:13px;padding:22px 0 40px}
footer a{color:var(--sub)}
"""


def page(title: str, body: str, description: str, canonical: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{canonical}">
<style>{CSS}</style>
</head>
<body>
<header class="site">
  <div class="wrap">
    <a class="brand" href="index.html">{SITE_NAME}</a>
    <nav>
      <a href="index.html">Jobs</a>
      <a href="post-a-job.html">Post a job</a>
      <a href="about.html">About</a>
    </nav>
  </div>
</header>
<main class="wrap">
{body}
</main>
<footer class="wrap">
  <p>Job listings sourced from <a href="https://remoteok.com/" rel="follow">Remote OK</a>, filtered and curated for AI/ML/agent roles. Every listing links back to the original post on Remote OK. See <a href="about.html">About</a> for refresh cadence and sourcing.</p>
</footer>
</body>
</html>"""


def money(v) -> str:
    try:
        v = int(v)
    except (TypeError, ValueError):
        return ""
    if v <= 0:
        return ""
    return f"${v:,}"


def build():
    DOCS.mkdir(exist_ok=True)
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    jobs = data["jobs"]
    fetched_at = datetime.fromtimestamp(data["fetched_at"], tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    categories = sorted({j["_category"] for j in jobs})

    def job_card(j: dict) -> str:
        salary = ""
        smin, smax = money(j.get("salary_min")), money(j.get("salary_max"))
        if smin and smax and smin != smax:
            salary = f" &middot; {smin}&ndash;{smax}"
        elif smin:
            salary = f" &middot; {smin}+"
        tags = "".join(f'<span class="tagchip">{html.escape(t)}</span>' for t in j.get("tags", [])[:6])
        posted = datetime.fromtimestamp(j.get("epoch", 0), tz=timezone.utc).strftime("%Y-%m-%d") if j.get("epoch") else ""
        return f"""<div class="job" data-cat="{html.escape(j['_category'])}" data-text="{html.escape((j['position']+' '+j['company']+' '+j['location']+' '+' '.join(j.get('tags',[]))).lower())}">
<h3><a href="{html.escape(j['_url'])}" rel="follow noopener" target="_blank">{html.escape(j['position'])}</a></h3>
<div class="meta">{html.escape(j['company'])} &middot; {html.escape(j['location'])}{salary} &middot; posted {posted} &middot; <span class="tagchip" style="background:#eef2ff;color:#1a56db">{html.escape(j['_category'])}</span></div>
<div class="tags">{tags}</div>
<div class="apply"><a href="{html.escape(j['_url'])}" rel="follow noopener" target="_blank">Apply on Remote OK &rarr;</a> <span class="via">(via Remote OK)</span></div>
</div>"""

    cards = "\n".join(job_card(j) for j in jobs)
    tab_buttons = '<button class="tab active" data-cat="all">All</button>' + "".join(
        f'<button class="tab" data-cat="{html.escape(c)}">{html.escape(c)}</button>' for c in categories
    )
    cat_counts = {c: sum(1 for j in jobs if j["_category"] == c) for c in categories}
    stat_cards = "".join(
        f'<div class="stat"><b>{n}</b><span>{html.escape(c)}</span></div>' for c, n in cat_counts.items()
    )

    home_body = f"""<h1>AI Agent &amp; Machine Learning Jobs, Remote</h1>
<p class="lede">A curated, filtered feed of remote AI agent, LLM, and machine-learning roles &mdash; sourced from Remote OK and re-filtered to cut the noise (crypto, sales, support roles that share a tag but aren't AI jobs). Updated {fetched_at}.</p>
<div class="stat-row">
  <div class="stat"><b>{len(jobs)}</b><span>open roles</span></div>
  {stat_cards}
</div>
<input id="q" placeholder="Filter by title, company, or tag&hellip;">
<div class="tabs">{tab_buttons}</div>
<div id="list">
{cards}
</div>
<script>
const q=document.getElementById('q'),jobs=[...document.querySelectorAll('.job')],tabs=[...document.querySelectorAll('.tab')];
let cat='all';
function apply(){{
  const v=q.value.trim().toLowerCase();
  jobs.forEach(j=>{{
    const catOk = cat==='all' || j.dataset.cat===cat;
    const textOk = !v || j.dataset.text.includes(v);
    j.style.display = (catOk && textOk) ? '' : 'none';
  }});
}}
q.addEventListener('input', apply);
tabs.forEach(t=>t.addEventListener('click', ()=>{{
  tabs.forEach(x=>x.classList.remove('active')); t.classList.add('active');
  cat = t.dataset.cat; apply();
}}));
</script>"""

    (DOCS / "index.html").write_text(
        page(f"{SITE_NAME} &mdash; {len(jobs)} Remote AI/ML/Agent Roles",
             home_body,
             f"{len(jobs)} curated remote AI agent, LLM, and machine-learning jobs, refreshed daily.",
             SITE_URL + "/"),
        encoding="utf-8",
    )

    post_body = f"""<h1>Post a Job</h1>
<p class="lede">Reach a small, laser-focused audience of people specifically looking for AI agent, LLM, and applied-ML roles &mdash; not a generic tech job board.</p>
<div class="card">
<h2 style="margin-top:0">Featured Post &mdash; $49 / 30 days</h2>
<p>Your listing pinned at the top of the relevant category for 30 days, with a direct apply link (no third-party redirect).</p>
<a class="cta" href="{GUMROAD_POST_URL}">Post your job &rarr;</a>
<p style="color:var(--sub);font-size:13px;margin-top:10px">After checkout, reply to your Gumroad receipt with the job title, company, location/remote policy, salary range (optional), and an apply link or email. Listings go live within a few hours.</p>
</div>
<p>Free listings are pulled automatically from Remote OK's public feed and re-curated for relevance &mdash; no submission needed if you're already posted there.</p>"""
    (DOCS / "post-a-job.html").write_text(
        page(f"Post a Job — {SITE_NAME}", post_body,
             "Post a featured AI/ML/agent job listing for $49/30 days on a curated niche job board.",
             SITE_URL + "/post-a-job.html"),
        encoding="utf-8",
    )

    about_body = f"""<h1>About {SITE_NAME}</h1>
<p>{SITE_NAME} is a curated, filtered feed of remote AI agent, LLM, and machine-learning job listings. The raw feed comes from <a href="https://remoteok.com/">Remote OK</a>'s public API, which lists jobs across every category; we filter that down to roles that are actually AI/ML/agent work (Remote OK's own "ai" tag catches a lot of noise &mdash; crypto traders, customer support, compliance analysts &mdash; that happen to share a tag with a real ML posting at the same company).</p>
<h2>Refresh cadence</h2>
<p>Refreshed automatically once a day. Last refresh: {fetched_at}.</p>
<h2>Attribution</h2>
<p>Every listing links back to its original post on Remote OK, per Remote OK's API terms. If you're hiring and already have a listing there, it will appear here automatically if it matches our AI/ML filter &mdash; no need to also use the paid post option.</p>
<h2>Corrections</h2>
<p>Wrong category, stale listing, or a request to remove your posting? Email <a href="mailto:vividsupport2@gmail.com">vividsupport2@gmail.com</a>.</p>"""
    (DOCS / "about.html").write_text(
        page(f"About — {SITE_NAME}", about_body,
             "About the AI Agent Jobs board: sourcing, filtering, and refresh cadence.",
             SITE_URL + "/about.html"),
        encoding="utf-8",
    )

    (DOCS / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8")
    urls = [SITE_URL + "/", SITE_URL + "/post-a-job.html", SITE_URL + "/about.html"]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "\n".join(f"<url><loc>{u}</loc></url>" for u in urls)
    sm += "\n</urlset>\n"
    (DOCS / "sitemap.xml").write_text(sm, encoding="utf-8")
    (DOCS / ".nojekyll").write_text("", encoding="utf-8")

    print(f"Built {len(jobs)} job cards across {len(categories)} categories.")


if __name__ == "__main__":
    build()
