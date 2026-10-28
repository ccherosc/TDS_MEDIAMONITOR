# TD SYNNEX Media Monitor

Internal pilot dashboard that tracks what partners, buyers, and IT pros say about TD SYNNEX, its vendors, competitors, and key technologies across Reddit, YouTube, Hacker News, forums, and review sites.

**Dashboard:** https://ccherosc.github.io/TDS_MEDIAMONITOR/

## How it works

```
Keywords (dashboard)  ->  Research skill (Claude, Cowork, ChatGPT)  ->  results file  ->  Dashboard
   data/keywords.json        reads keywords, researches, scores          media-monitor.v1    data/results.json
```

1. The team adds or removes keywords on the **Keywords** tab.
2. Someone runs the research skill in Claude, Copilot Cowork, or ChatGPT (the dashboard writes the prompt for you). Pick all platforms or a single focus: Reddit only, YouTube only, or Others.
3. The skill returns one JSON results file. Load it with **Update data > Load results**, or let Claude Code push it to GitHub.
4. The dashboard recalculates everything: sentiment by platform, alerts, response queue, competitive map, pain-point matrix.

## Tabs

| Tab | For |
|---|---|
| All analysis tabs | Filter by keyword, time window (30, 90 days, all), and platform (All, Reddit, YouTube, Others). The platform filter sticks between visits. |
| Overview | Net sentiment, conversation count, replies needed, alerts, sentiment by platform, keyword table |
| Conversations | Every conversation with filters, source links, suggested replies, and Mark responded / Dismiss |
| Advanced | Narrative risk index, competitive position map, pain-point matrix, signal matrix, conquest opportunities, theme momentum, weekly sentiment, emotion profile, earned voice, vision findings, executive brief, agent feed |
| Keywords | Add, pause, or remove keywords; run research; load results; export to Excel |
| Upgrades | Paid data feeds ranked by impact, with costs |

## Repo layout

| Path | What it is |
|---|---|
| index.html | The whole dashboard (one file) |
| data/keywords.json | Tracked keywords |
| data/results.json | All conversations, keyword summaries, and run history |
| data/state.json | Responded / dismissed status per conversation |
| data/upgrades.json | Upgrades tab content |
| skill/media-monitor-research/ | The research skill source (SKILL.md, references, scripts) |
| kits/ | Ready-to-install packages for Claude, Copilot Cowork, and ChatGPT |
| SETUP.md | Editing access, sharing, and the skill setup |

## Pilot limits (read this)

- **Access:** the sign-in screen is a light gate, not security. This repo is public, so anyone with the URL can read the data files. Move to a private host with real sign-in (for example Azure Static Web Apps with Microsoft Entra ID) before adding sensitive notes.
- **Reddit coverage:** the first data pull came from web search and is thin on Reddit and YouTube. The skill's collector fills those in when run from a computer with internet access.
- **Data terms:** Reddit's free API bars commercial use, and internal business use may still count. Check with legal before scaling, and see the Upgrades tab for licensed options.
