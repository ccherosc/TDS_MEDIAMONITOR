# Setup guide

## 1. Open the dashboard

https://ccherosc.github.io/TDS_MEDIAMONITOR/ and sign in with the team username and password.

Anyone can view and export. To **edit** (add keywords, load results, mark conversations responded), each editor connects GitHub once (step 2).

## 2. Give an editor access (5 minutes, once per person)

1. The repo owner adds the person as a collaborator: GitHub repo > Settings > Collaborators > Add people. (Skip for the owner.)
2. The editor creates a token: GitHub > Settings > Developer settings > Personal access tokens > Fine-grained tokens > Generate new token.
   - Repository access: **Only select repositories** > `TDS_MEDIAMONITOR`
   - Permissions > Repository permissions > **Contents: Read and write**
   - Expiration: 90 days is a sensible default
3. In the dashboard: **Update data > Sync & export**, paste the token, click **Connect**.

The token stays in that browser only. It never goes into the page or the repo. Disconnect removes it.

## 3. Run research

1. Install the skill in the tool you use (see `kits/README.md`).
2. Dashboard > **Update data > Run research**, pick Claude, ChatGPT, or Copilot Cowork, and copy the prompt. It already includes your active keywords.
3. Paste it into the tool. When it gives you the JSON file, go to **Update data > Load results**, choose the file, check the preview, and import.

Same URL = same conversation, so loading overlapping results never double counts.

## 4. Daily routine (10 minutes)

| Step | Where |
|---|---|
| Check alerts and Needs attention (use the platform filter for a Reddit-only or YouTube-only view) | Overview |
| Work the reply queue: open source, copy suggested reply, post from your own account, Mark responded | Conversations > Status: Needs response |
| Work 3-5 Hunt list searches; paste good threads into the inbox | Sightings |
| Copy the executive brief into email or Teams | Advanced > Executive brief |
| Export conversations to Excel when needed | Update data > Sync & export > Download conversations (.csv) |

## 5. Reddit plan

Reddit closes its public API in March 2027. See `docs/REDDIT-PLAYBOOK.md` for the API request (due Oct 31), Reddit Pro setup, the Sightings routine, and the email to ask corporate about existing listening licenses.

## 6. Feed other AI agents

Advanced > **Agent feed** gives a stable JSON summary (keywords, sentiment, risk index, signals, alerts, response queue, buying signals). Your internal agents can also read `data/results.json` directly from the repo.

## 6. Claude-hosted preview

A copy of the dashboard also runs on Claude for quick demos. Viewers need a claude.ai account and must be shared in from the page's Share menu. Its edits are stored on Claude, separate from GitHub.

## 7. Moving to production later

| Need | Option |
|---|---|
| Real sign-in with company accounts | Azure Static Web Apps + Microsoft Entra ID, or Cloudflare Access in front of Pages |
| Private data | Private repo + host above (GitHub Pages on private repos stays reachable by URL unless you have Enterprise Cloud) |
| Scheduled refresh | Copilot Cowork Automations, or a GitHub Action running the collector |
| Licensed Reddit data | See the Upgrades tab |
