# Media Monitor Results Schema (media-monitor.v1)

One JSON file. Every agent (Claude, ChatGPT, Copilot Cowork, scripts) writes this shape.
The dashboard imports it, de-duplicates items by URL, and computes all charts itself.
Agents supply evidence and judgment. The dashboard does the math.

## Top level

| Field | Required | Type | Notes |
|---|---|---|---|
| schema | yes | string | Always "media-monitor.v1" |
| workspace | yes | string | Default "tdsynnex-internal". Vendor workspaces later use their own id. |
| run | yes | object | Who ran it, when, what was covered |
| keywords | yes | array | One entry per keyword researched (analyst summary + themes) |
| items | yes | array | Every piece of evidence (post, thread, video, review, article) |
| insights | no | object | Cross-keyword summary, alerts, trends, actions |

## run

```json
{
  "id": "run-2026-10-28-claude-01",
  "agent": "claude",
  "started_at": "2026-10-28T14:00:00Z",
  "finished_at": "2026-10-28T15:10:00Z",
  "window_days": 90,
  "platform_focus": "all",
  "mode": "sweep",
  "sources_used": ["reddit", "youtube", "hackernews", "forum", "review", "news"],
  "coverage": { "reddit": "full", "youtube": "partial", "hackernews": "full", "forum": "partial", "review": "partial", "news": "partial", "x": "none" },
  "notes": "Reddit collected via public JSON. YouTube via Data API (key present)."
}
```

agent: claude | chatgpt | cowork | script | other
mode: sweep (keyword search, default) | inbox (only the sightings and watched threads you were given) | revisit
platform_focus: all (default) | reddit | youtube | others. "others" means every platform except Reddit and YouTube (forums, review sites, Hacker News, news, X, LinkedIn). A focused run should only contain items from that platform group, mark the rest "none" in coverage, and write keyword summaries about that platform only. The dashboard stores focused summaries separately and shows them when its platform filter matches, so a Reddit-only run never overwrites the all-platform read-out.
coverage values: full | partial | limited | none

## keywords[]

```json
{
  "id": "td-synnex",
  "term": "TD SYNNEX",
  "group": "Brand",
  "query": "\"TD SYNNEX\" OR TDSYNNEX OR SYNNEX OR \"StreamOne\"",
  "summary": "Two to three sentences an exec can read in 10 seconds.",
  "themes": [
    { "name": "Partner support responsiveness", "sentiment": -0.4, "mentions": 6, "momentum": "rising", "description": "One sentence.", "evidence_item_ids": ["a1b2c3d4e5f6"] }
  ],
  "risks": ["One line each"],
  "opportunities": ["One line each"]
}
```

group: Brand | Distributor | Vendor | Security | Technology | Custom
id: lowercase slug of the term (letters, numbers, dashes)
momentum: rising | steady | fading
sentiment: -1.0 (very negative) to +1.0 (very positive)

## items[]

```json
{
  "id": "a1b2c3d4e5f6",
  "keyword_ids": ["td-synnex"],
  "platform": "reddit",
  "source_name": "r/msp",
  "url": "https://www.reddit.com/r/msp/comments/abc123/...",
  "title": "Thread or video title",
  "author": "u/handle or channel name (optional)",
  "published_at": "2026-09-14",
  "engagement": { "score": 120, "comments": 45, "views": null, "likes": null, "rating": null },
  "summary": "Paraphrased 1-2 sentences. What happened and why it matters.",
  "excerpt": "Short verbatim quote, 20 words max. Empty string if none.",
  "sentiment": { "label": "negative", "score": -0.6, "confidence": 0.8, "emotion": "frustration" },
  "keyword_sentiment": { "pax8": { "label": "negative", "score": -0.7 }, "td-synnex": { "label": "positive", "score": 0.5 } },
  "aspects": [ { "aspect": "support", "sentiment": -0.7 } ],
  "signals": ["partner_pain", "product_issue"],
  "intent_stage": "none",
  "entities": ["Microsoft CSP"],
  "influence": "medium",
  "response": { "recommended": true, "priority": "high", "draft": "Suggested reply text.", "rationale": "Why respond." },
  "vision": { "analyzed": false, "findings": "" },
  "company_reply": { "checked": true, "replied": false, "first_reply_at": null, "hours_to_reply": null },
  "collected_by": "reddit_api"
}
```

| Field | Rules |
|---|---|
| id | First 12 hex chars of SHA-1 of the canonical URL. Optional; the dashboard computes it if missing. |
| platform | reddit, youtube, hackernews, forum, review, news, x, linkedin, podcast, other |
| published_at | YYYY-MM-DD. Required. Use the post date, not the crawl date. |
| engagement | Only numbers you actually saw. Use null when unknown. Never estimate. |
| sentiment.label | positive, neutral, negative, mixed |
| sentiment.score | -1.0 to +1.0. See methodology.md rubric. |
| keyword_sentiment | Optional. Use when one post mentions two tracked keywords with different sentiment ("switched from Pax8 to TD SYNNEX"). The dashboard scores each keyword from its own entry. sentiment stays the item's overall read toward its primary keyword. |
| sentiment.emotion | frustration, anger, anxiety, confusion, disappointment, satisfaction, excitement, trust, curiosity, neutral |
| aspects[].aspect | pricing, margins, support, portal, logistics, licensing, product_quality, security, performance, partner_program, credit_terms, communication, other |
| signals | brand_sentiment, praise, product_issue, product_feedback, buying_signal, partner_pain, competitor_switch, trend, crisis, influencer |
| intent_stage | none, research, evaluating, ready_to_buy |
| influence | low, medium, high (reach of the author or venue) |
| response.draft | Write as a TD SYNNEX representative. Disclose affiliation. Helpful, not salesy. Empty if not recommended. |
| vision | analyzed=true only if the agent actually looked at an image (screenshot, thumbnail, chart) and found something. |
| company_reply | Optional. Fill it when you revisit a watched thread or open any thread: did someone clearly from TD SYNNEX reply (official account, flair, or a stated affiliation)? hours_to_reply = first TD SYNNEX reply time minus post time. The dashboard turns this into reply rate and response time. |
| collected_by | reddit_api, youtube_api, hn_api, web_search, browser, manual, aggregator |

## insights (optional, cross-keyword)

```json
{
  "executive_summary": ["Bullet 1", "Bullet 2", "Bullet 3"],
  "alerts": [
    { "id": "alert-1", "severity": "high", "keyword_id": "ingram-micro", "type": "crisis", "title": "Short headline", "detail": "One or two sentences.", "evidence_item_ids": ["..."] }
  ],
  "trends": [
    { "name": "AI PC refresh hesitation", "description": "One sentence.", "momentum": "rising", "keyword_ids": ["ai-pcs"], "evidence_item_ids": ["..."] }
  ],
  "recommended_actions": [
    { "action": "Publish a partner FAQ on X", "owner": "PR", "priority": "high", "evidence_item_ids": ["..."] }
  ]
}
```

alert types: sentiment_drop, volume_spike, crisis, opportunity, competitor_move
owner: PR, Marketing, Product, Vendor Management, Sales, Partner Success, Executive

## Other dashboard files (read-only for agents unless told otherwise)

| File | Shape | Agents use it for |
|---|---|---|
| data/keywords.json | `{keywords: [{id, term, group, query, aliases[], subreddits[], notes, status}]}` | Which keywords to research. `aliases` are slang, old names, and product names people actually type. Groups include `Category` for unbranded topics such as "Choosing a distributor". |
| data/sightings.json | `{items: {id: {id, url, keyword_ids[], note, status, added_by, added_at}}}` | Links teammates flagged. Pending ones are the inbox. A sighting counts as analyzed once an item with the same URL exists in results. |
| data/state.json | `{items: {item_id: {status, watch, by, at}}}` | `watch: true` marks threads to revisit for late replies and company_reply. |

## Rules that keep the data trustworthy

1. Every item must have a real URL the agent opened or got from an API. No invented threads.
2. Never estimate engagement. Unknown is null.
3. Summaries are paraphrased. Excerpts stay short (20 words max) and in quotes only in the UI.
4. One item per URL. If a thread matches two keywords, list both ids in keyword_ids.
5. Dates are required. Items older than window_days are allowed only for context and should be few.
