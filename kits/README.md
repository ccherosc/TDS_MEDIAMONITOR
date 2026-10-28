# Media Monitor research skill: setup by platform

One skill, three ways to run it. All of them produce the same results file, and the dashboard loads it the same way.

| Platform | Package | Can run the Reddit/YouTube collector? | How results reach the dashboard |
|---|---|---|---|
| Claude Code (your computer) | `media-monitor-research.zip` | Yes | Commits straight to GitHub, or Load results |
| Claude (claude.ai) | `media-monitor-research.zip` | Partly (no Reddit from Claude's cloud) | Download file, then Load results |
| Microsoft Copilot Cowork | `media-monitor-research-cowork.zip` | No (web research only) | OneDrive file, then Load results |
| ChatGPT | `chatgpt-kit.zip` | No (web search and deep research) | Download file, then Load results |

Best depth: Claude Code on a computer with internet, because the collector reads Reddit threads with their top comments.

## Platform focus (all kits)

Every kit can research all platforms or one group: **Reddit only**, **YouTube only**, or **Others** (forums, review sites, Hacker News, news). Pick it in the dashboard under Update data > Run research and the prompt says so. Focused runs keep their own keyword summaries, which appear when you set the dashboard's platform filter to match. Claude Code collector: `python scripts/collect.py --keywords keywords.json --platform-focus reddit`.

## Claude Code

1. Unzip `media-monitor-research.zip` into `~/.claude/skills/` (so you have `~/.claude/skills/media-monitor-research/SKILL.md`).
2. Optional keys for deeper collection (set in your terminal profile):
   - `YOUTUBE_API_KEY` (free from Google Cloud Console, YouTube Data API v3)
   - `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` (Reddit app, approved under Reddit's developer policy)
   - `GITHUB_TOKEN` (fine-grained token, Contents read/write on the dashboard repo only) to publish results directly
3. Ask: "Run media-monitor-research for this week and push the results."

## Claude (claude.ai)

1. Settings > Capabilities: turn on code execution and file creation.
2. Customize > Skills > Add > Upload a skill: choose `media-monitor-research.zip`.
3. In the dashboard, open Update data > Run research > Claude, copy the prompt, and paste it into a new chat.
4. Download the JSON file Claude makes, then load it in the dashboard (Update data > Load results).

## Microsoft Copilot Cowork

1. In Cowork: Customize > Skills > Add > Upload skill, and choose `media-monitor-research-cowork.zip`.
2. In the dashboard, open Update data > Run research > Copilot Cowork, copy the prompt, and paste it into Cowork.
3. Cowork saves `media-monitor-results-YYYY-MM-DD.json` to OneDrive (Media Monitor/results). Load it in the dashboard.
4. Optional schedule: Cowork > Automations > new scheduled prompt, for example weekly on Monday at 7 AM: "Run the media-monitor-research skill on the keywords in OneDrive Media Monitor/keywords.json for the last 7 days and save the results file." (Download keywords.json from the dashboard into that folder first.)

## ChatGPT

1. Create a Project (or a custom GPT) named "Media Monitor Research".
2. Paste `project-instructions.md` into the project instructions.
3. Upload the files in the `knowledge` folder: schema.md, methodology.md, sources.md, response-playbook.md, example-results.json.
4. In the dashboard, open Update data > Run research > ChatGPT, copy the prompt, and paste it into the project.
5. Download the JSON file and load it in the dashboard.

## What "deeper than last30days" means here

| last30days | Media Monitor research |
|---|---|
| One topic, one brief | A tracked keyword list your team manages |
| Summary of what people said | Per-item sentiment toward each brand, emotion, confidence |
| | Aspect scoring (pricing, support, portal, licensing...) feeding a pain-point matrix |
| | Buying-signal stages and channel partner pain tags |
| | Theme momentum versus the previous run, plus alerts |
| | Vision reads of screenshots and video thumbnails |
| | Suggested replies with disclosure rules, and a response queue |
| Markdown file | Structured JSON that also feeds internal AI agents |
