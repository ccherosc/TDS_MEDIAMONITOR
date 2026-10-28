---
name: media-monitor-research
description: Deep social-listening research that feeds the TD SYNNEX Media Monitor dashboard. Use when asked to research, monitor, refresh, or update sentiment for tracked keywords (TD SYNNEX, distributors, vendors, competitors, technologies) across Reddit, YouTube, Hacker News, forums, and review sites, to find buying signals, partner pain points, or reply opportunities, or to produce a media-monitor results file for the dashboard.
---

# Media Monitor Research

Turns a keyword list into one evidence-backed results file (`media-monitor.v1`) that the Media Monitor dashboard loads. It goes deeper than a quick "what is everyone saying" sweep: it reads comment threads, scores sentiment per brand and per business aspect, tags buying signals and partner pain, tracks theme momentum against the last run, reads images with vision, and drafts replies a TD SYNNEX rep could post.

Works in any agent that can read this file: Claude (claude.ai, Claude Code), Microsoft Copilot Cowork, ChatGPT (via the ChatGPT kit), Codex, Cursor, and other Agent Skills hosts. Steps marked **[code]** need the ability to run Python with internet access; skip them if you cannot, and lean harder on web search.

## Running in Microsoft Copilot Cowork

- Cowork follows these instructions with its own web research and Deep Research. Skip every step marked **[code]**; the Python scripts in `scripts/` are for hosts that can run code.
- Deliver with Route B in references/delivery.md: save `media-monitor-results-YYYY-MM-DD.json` (add `-reddit`, `-youtube`, or `-others` for a focused run) to OneDrive in `Media Monitor/results/`, then tell the user it is ready to load in the dashboard (Update data > Load results).
- Never send email, post in Teams, or reply on any website as part of this skill. Reply drafts stay in the results file for a human to review.
- To run it on a schedule, the user can add a prompt in Cowork's Automations tab, for example: "Run the media-monitor-research skill, Reddit only, for the keywords in OneDrive Media Monitor/keywords.json for the last 7 days and save the results file."

## Reference files (read when the step says so)

| File | Read it for |
|---|---|
| references/schema.md | The exact output format. Read before writing any output. |
| references/methodology.md | Sentiment rubric, signals, intent stages, influence, themes, alerts, vision. |
| references/sources.md | Where to look per platform, query patterns, communities per keyword group. |
| references/response-playbook.md | When and how to draft replies. |
| references/delivery.md | How to get results into the dashboard (GitHub, file import, Claude preview, OneDrive). |

## Inputs

1. **Keywords.** Use the first that exists:
   - A keyword list the user pasted or attached (JSON or plain list).
   - The dashboard's list: `https://raw.githubusercontent.com/ccherosc/TDS_MEDIAMONITOR/main/data/keywords.json`
     **[code]** `python scripts/github_sync.py pull-keywords --out keywords.json`
   Research only keywords with `"status": "active"`. Each keyword has `id`, `term`, `group`, `query` (search string), `subreddits`, and `notes` (what the team cares about). Keep the `id` values exactly; the dashboard matches on them.
2. **Window.** Default the last 30 days. The user may say otherwise. Older items only as context (under 20%).
3. **Platform focus.** Default `all`. The user (or the dashboard prompt) may ask for `reddit`, `youtube`, or `others` (everything except Reddit and YouTube: forums, review sites, Hacker News, news, X, LinkedIn). For a focused run: collect only from that platform group, set `run.platform_focus`, mark the other platforms `none` in `run.coverage`, and write keyword summaries, themes, and alerts about that platform only. The dashboard keeps focused summaries separate, so a Reddit-only run never replaces the all-platform read-out.
4. **Inbox and revisits (optional).** Teammates flag links in the dashboard's Sightings inbox and mark threads to watch. The prompt may list them under SIGHTINGS and REVISIT. **[code]** `python scripts/github_sync.py pull-queue --out queue.json`. Analyze every listed link even if it is outside the platform focus. In **inbox mode** (`run.mode = "inbox"`) analyze only those links and skip the keyword sweep.
5. **Previous results (optional, for momentum).** `https://raw.githubusercontent.com/ccherosc/TDS_MEDIAMONITOR/main/data/results.json` holds earlier runs. Use it to label themes rising, steady, or fading and to detect sentiment shifts.

## Workflow

These steps run in order. Track progress with a checklist if your host supports one.

1. **Load keywords and the previous results** (Inputs above).
2. **Plan each keyword.** Search with the keyword's `aliases` too (slang, old names, product names such as Synnex, Tech Data, StreamOne, disti). Most people never type the official name. Add common misspellings. Add pain and intent variants (see sources.md, "Query expansion"). Pick communities: the keyword's `subreddits` plus the defaults for its group. Write down disambiguation rules (for example, Pax8 is also a gene; Arrow is also a TV show).
3. **Collect.**
   - **[code]** Run the collector first:
     `python scripts/collect.py --keywords keywords.json --days 30 --out raw`
     For a focused run add `--platform-focus reddit` (or `youtube`, `others`). Add `--queue queue.json` to fetch sightings and watched threads (with `--inbox-only` for inbox mode). With `BRAVE_API_KEY` set, the collector also runs the search-engine lens, which finds Reddit threads through a search index and keeps working after Reddit's public API closes.
     It pulls Reddit posts with their top comments, Hacker News stories and comments, and YouTube videos with stats and top comments (when `YOUTUBE_API_KEY` is set), and saves post images and thumbnails to `raw/images/` for vision. See the script header for credentials.
   - **Always** run web search sweeps too (sources.md), limited to the platform focus: community forums, review sites, YouTube, and Reddit threads the collector missed. Use several short queries per keyword rather than one long one.
   - Open every candidate page. Read the comments, not just the post: the top replies usually carry the real sentiment and the fixes or workarounds.
4. **Screen.** Keep an item only if it is really about the keyword, has a verifiable date, and adds signal. Drop vendor press releases unless the reaction to them is the story. One item per URL; if it matches two keywords, list both ids.
5. **Analyze each item** with methodology.md: sentiment toward each tracked keyword it mentions, emotion, aspects, signals, intent stage, influence. Write a paraphrased summary and at most one short verbatim excerpt (20 words max).
6. **Vision.** If you can view images, look at saved images, screenshots linked in posts, and video thumbnails for items that have them. Record what you see in `vision.findings` and adjust signals (methodology.md, "Vision"). If you cannot view images, leave `vision.analyzed` false.
7. **Synthesize per keyword.** Summary (2-3 sentences an executive can read in ten seconds), 3-6 themes with evidence ids and momentum versus the previous run, 2-4 risks, 2-4 opportunities framed for TD SYNNEX as the distributor.
8. **Cross-keyword insights.** Alerts (only evidence-backed; thresholds in methodology.md), trends, recommended actions with an owner, and a 3-6 bullet executive summary. Look for competitive moves and "conquest" openings: pain at a competitor or vendor that TD SYNNEX can genuinely help with.
9. **Draft replies** for items that warrant one (response-playbook.md). For revisited and newly opened threads, fill `company_reply` (methodology.md, section 8).
10. **Validate.** **[code]** `python scripts/merge_results.py check results.json` and fix what it reports. Without code, walk the checklist below.
11. **Deliver** per references/delivery.md, then give the user a short summary table: items per keyword and platform, top three findings, alerts, and coverage gaps.

## Non-negotiables

- Every item has a real URL you opened or received from an API. Never invent threads, quotes, numbers, authors, or dates.
- Engagement numbers only when you saw them. Unknown is `null`.
- Summaries are your own words. Excerpts are short and verbatim, one per item.
- Public handles are fine; never collect emails, phone numbers, or other personal data.
- Reply drafts disclose TD SYNNEX affiliation, never disparage competitors, and never pose as an independent customer.
- Report coverage honestly in `run.coverage` (full, partial, limited, none) so the dashboard can flag thin platforms.

## Depth targets

| Situation | Items per keyword | Community share |
|---|---|---|
| Collector available (Reddit/HN/YouTube APIs) | 15-40 | 60%+ community |
| Web search only | 8-15 | as high as you can find, note the gap |

Quality beats volume. Ten well-read threads with their comments beat forty headlines.

## Self-check before delivering

- [ ] `schema` is `media-monitor.v1`, `workspace` is `tdsynnex-internal`, `run.id` is unique (for example `run-2026-11-04-claude` or `run-2026-11-04-claude-reddit`).
- [ ] `run.platform_focus` matches what was asked, and every item belongs to that platform group.
- [ ] Every keyword id matches the dashboard list.
- [ ] Every item has url, title, published_at, platform, keyword_ids, summary, sentiment.
- [ ] Mixed-sentiment multi-brand items use `keyword_sentiment`.
- [ ] Every `evidence_item_ids` entry points to an item in the file.
- [ ] Coverage and notes describe what you could not reach.
