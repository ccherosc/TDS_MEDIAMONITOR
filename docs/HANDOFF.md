# Media Monitor: handoff (updated Oct 29, 2026)

## Where things stand

| Piece | Status |
|---|---|
| Live dashboard | https://ccherosc.github.io/TDS_MEDIAMONITOR/ (GitHub Pages on, deploying from `main`) |
| Repo | ccherosc/TDS_MEDIAMONITOR |
| Claude preview | Claude-hosted copy of the same dashboard, for demos |
| Data on file | 179 sourced conversations across 20 keywords (first pull, web search only, thin on Reddit and YouTube) |
| Keywords | 23: TD SYNNEX, 5 distributors, 7 vendors, 3 security, 4 tech themes, 3 new unbranded category keywords. All have slang aliases. |

## Built today

- Platform filter (All / Reddit / YouTube / Others) and platform-focused research runs
- Sightings tab: paste box, bookmarks-bar button, Teams + Cowork prompt, Hunt list (37 ready-made Reddit and Google searches)
- Watch thread and Response performance (TD SYNNEX reply rate, time to reply)
- Keyword aliases with an Edit form; Category keyword group
- Skill: aliases in search, search-engine lens (`BRAVE_API_KEY`), queue links (`pull-queue`, `--queue`, `--inbox-only`), `company_reply`, `run.mode`
- docs/REDDIT-PLAYBOOK.md: API request wording, Reddit Pro keywords, AMA, corporate email

## Hunt run (Oct 29, 2026)

- Reddit is blocked by policy for Claude's browser and web search. Claude cannot run the Reddit Hunt list. A person works it with the "+ Media Monitor" bookmark button.
- Claude swept non-Reddit sources instead and added 19 items to the Sightings inbox: 7 Trustpilot reviews, 5 Spiceworks threads, 7 YouTube videos.
- Trustpilot: TD SYNNEX scores 1.8 of 5 on 17 reviews. All 7 reviews from the last 12 months are 1-star. The profile was claimed in May 2026 and no review has a company reply.
- Hacker News had nothing relevant in 12 months. YouTube is mostly TD SYNNEX's own channels.

## Next steps

1. **Now:** Dashboard > Sightings > Research the inbox > Get research prompt. Run it, then Load results.
2. **By Fri Oct 31:** request Reddit API access (wording in the playbook).
3. **Daily, by hand:** work 5 to 6 Reddit searches from the Hunt list; add threads with the bookmark button.
4. **This week:** set up Reddit Pro; send the corporate email about Sprinklr / Brandwatch / Meltwater; ask who owns the Trustpilot profile.
5. **Each editor:** create a fine-grained GitHub token (TDS_MEDIAMONITOR, Contents read/write) and connect it in Update data > Sync & export.

## Known limits

- The sign-in is a light gate; the repo is public, so data files are readable by URL.
- Reddit public API closes March 2027; plan on Reddit Pro, the Sightings inbox, the lens, or a licensed feed.
