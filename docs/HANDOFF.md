# Media Monitor: handoff (Oct 28, 2026)

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

## Next steps

1. **From home:** open this same chat in the Claude desktop app and send "run the Reddit hunt". Claude works the Hunt list in the desktop browser, finds threads, and adds them to the Sightings inbox. Then Run research > Inbox only.
2. **By Fri Oct 31:** request Reddit API access (wording in the playbook).
3. **This week:** set up Reddit Pro; send the corporate email about Sprinklr / Brandwatch / Meltwater.
4. **Each editor:** create a fine-grained GitHub token (TDS_MEDIAMONITOR, Contents read/write) and connect it in Update data > Sync & export.

## Known limits

- The sign-in is a light gate; the repo is public, so data files are readable by URL.
- Reddit public API closes March 2027; plan on Reddit Pro, the Sightings inbox, the lens, or a licensed feed.
