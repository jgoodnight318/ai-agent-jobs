# AI Agent Jobs

A curated, filtered remote job board for AI agent / LLM / applied-ML
roles, refreshed daily.

Live: https://jgoodnight318.github.io/ai-agent-jobs/

## What it is

Remote OK's public API returns everything tagged `ai` or `machine-learning`
— which includes a lot of noise (crypto traders, customer-support roles,
compliance analysts that happen to share a tag with a real ML posting at
the same company). `tools/fetch.py` pulls that raw feed and re-filters on
the job title itself against an AI/ML/agent keyword set, cutting ~92 raw
matches down to the ones that are actually AI/ML/agent work. Every listing
links back to its original Remote OK post with a followed link, per Remote
OK's own API terms ("please link back with follow, and without nofollow,
to the URL on Remote OK and mention Remote OK as a source" — returned in
the API payload itself).

This is the validated "niche job board aggregator" pattern from
`RESEARCH_K_LAPTOP_PLAYBOOKS_2026-09-02.md`: RemoteOK+NomadList
($83K/mo by year 4, Pieter Levels), RanchWork ($87.6K/2023, $95/post),
MoAIJobs ($1K+ revenue, built in 2 hours) all monetize a narrow vertical
with paid featured posts on top of a free aggregated base. Ours is
narrower than any of those (AI-agent/LLM specifically, not "remote" or
"ranching" broadly) and the base listings cost nothing to source.

## Build / refresh

```
python3 tools/fetch.py    # pulls Remote OK, filters, writes data/raw_jobs.json
python3 tools/build.py    # renders docs/ from data/raw_jobs.json
```

`tools/run_all.py` does both and commits+pushes if anything changed.
Installed as a daily launchd job (7:15am):

```
cp launchd/com.james.ai-agent-jobs.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.james.ai-agent-jobs.plist
```

## Monetization

`/post-a-job.html` links a $49/30-day "Featured Post" Gumroad product
(`goodnightdreams32.gumroad.com/l/ai-agent-jobs-featured-post`) — **needs
James**: create it (5 min, existing Gumroad account). Undercuts Remote
OK's own posting price significantly while reaching a laser-focused
subset of their audience.

**Gumroad product to create:**
- Name: AI Agent Jobs — Featured Post (30 days)
- Price: $49
- URL slug: `ai-agent-jobs-featured-post`
- Description: "Pin your AI agent / LLM / applied-ML job at the top of
  the relevant category on AI Agent Jobs (jgoodnight318.github.io/ai-agent-jobs)
  for 30 days, with a direct apply link. Reply to your receipt email with
  the job title, company, location/remote policy, salary range
  (optional), and an apply link or email."

## 30-day growth plan

- **Week 1**: verify the daily launchd refresh is actually running (check
  `logs/launchd.out.log`); submit the sitemap to Google Search Console
  (needs James's Google login, ~2 min).
- **Week 1-2**: widen sourcing beyond Remote OK's `ai`/`machine-learning`
  tags — Remote OK's `llm`, `nlp`, `genai`, `prompt-engineering` tags
  currently return only 1 job each (the taxonomy is thin right now but
  growing); re-check monthly, and evaluate adding We Work Remotely's
  public RSS feeds (`weworkremotely.com/categories/remote-programming-jobs.rss`)
  filtered the same way, as a second free source.
- **Week 2-4**: if traffic materializes, add a lightweight "AI Agent
  Engineer" vs "ML/Data Science" vs "Applied AI" landing page each, for
  a little internal link structure — skipped in v1 because 23 jobs is too
  thin to split without making each category page look empty.
- **Ongoing**: watch which category gets the most outbound clicks (would
  need simple click tracking — not wired up in v1) to decide where to
  double down on sourcing.

## Kill criterion

If 60 days after the daily refresh has been running with Search Console
connected, organic traffic is under 20 clicks/month AND zero featured
posts have sold, kill it — the vertical may be too thin (RemoteOK's own
AI-tagged supply is only ~90 raw jobs before filtering) to support a
standalone board versus just being a filter view on RemoteOK itself.

## Needs James

1. Create the $49 Gumroad "Featured Post" product above (5 min).
2. Install the launchd job (2 commands above, or ask the operator to do
   it — this repo can do it unattended, listed here for visibility).
3. Optional, free: Google Search Console + Bing Webmaster Tools sitemap
   submission for faster indexing.
