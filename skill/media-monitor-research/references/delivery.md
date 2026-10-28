# Delivering results to the dashboard

The dashboard lives on GitHub Pages: `https://ccherosc.github.io/TDS_MEDIAMONITOR/`
Its data is in the repo `ccherosc/TDS_MEDIAMONITOR`, folder `data/`:

| File | What it holds |
|---|---|
| data/keywords.json | The keyword list the team manages in the dashboard |
| data/results.json | Every conversation, keyword summary, and research run |
| data/state.json | Which conversations were marked responded or dismissed |

Every route below ends with the same merge rules: same URL = same conversation, newest keyword summaries win, run history is kept. Runs with a `platform_focus` other than `all` keep their keyword summaries in `keyword_insights_by_focus`, so they never replace the all-platform summaries.

## Route A: you can run code and reach GitHub (Claude Code, Claude with code execution, Codex, Cursor)

```
export GITHUB_TOKEN=<fine-grained token with Contents: read and write on the repo only>
python scripts/github_sync.py pull-keywords --out keywords.json
# ... research, write results.json ...
python scripts/merge_results.py check results.json
python scripts/github_sync.py push results.json
```

`push` reads the current data/results.json from GitHub, merges your file into it, and commits it. GitHub Pages refreshes within about a minute. Never paste the token into chat output or files.

## Route B: no code or no GitHub access (ChatGPT, Copilot Cowork, claude.ai without a token)

1. Save the results as a file named `media-monitor-results-YYYY-MM-DD.json`.
   - ChatGPT: offer it as a downloadable file.
   - Copilot Cowork: save it to OneDrive under `Media Monitor/results/`.
   - claude.ai: create the file and share it.
2. The user opens the dashboard, clicks **Update data > Load results**, and picks the file. The dashboard validates it, shows a preview, and commits it to GitHub using the user's own token.

## Route C: Claude-hosted preview (optional)

If the user asks to update the Claude-hosted preview and you have Claude's artifact data tools, write to the preview's shared database:

| Collection | Document id | Content |
|---|---|---|
| items | item id | The full item object |
| kwins | keyword id | `{keyword_id, term, summary, themes, risks, opportunities, run_id, updated_at}` |
| runs | run id | The run object plus `insights`, `keyword_ids`, `item_count` |

Batch writes in groups of 50. Otherwise, use Route B on the preview: it has the same Load results button.

## Sightings and watched threads

- Pending sightings come from `data/sightings.json`; watched threads from `data/state.json` (`watch: true`). `github_sync.py pull-queue` writes both to queue.json.
- You do not need to change sightings.json. A sighting shows as Analyzed in the dashboard once results contain an item with the same URL.
- For a revisit, include the thread again as an item with fresh engagement and `company_reply`. The merge keeps the original first-seen date.

## Summary for the user (all routes)

End with a short table: items per keyword, items per platform, new alerts, and anything you could not reach.
