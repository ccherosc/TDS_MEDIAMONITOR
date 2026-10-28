# Reddit playbook

How the Media Monitor keeps getting Reddit data after Reddit closes its public API, and what to do this week.

## The clock

| Date | What closes |
|---|---|
| Oct 31, 2026 | New requests for public API access |
| Nov 13, 2026 | RSS feeds |
| Jan 12, 2027 | Access starts closing for apps that have not registered |
| March 2027 | Public Data API closes. Only partners with written agreements keep access. |

Source: PPC Land and WinBuzzer reports of Reddit's Sept 30, 2026 developer announcement.

## 1. Request API access before Oct 31 (30 minutes)

Use a Reddit account tied to your work identity. Describe the use honestly. Suggested wording:

> TD SYNNEX, an IT distributor, monitors public Reddit discussion about our company, the vendors we distribute, and our competitors for internal brand and customer-experience purposes. Expected volume: about 20 keywords, searched daily, roughly 10,000 requests per month. We do not resell data, train models, or store deleted content, and we honor deletions. We would also like to discuss a written agreement for continued access after the public API closes in March 2027.

When credentials arrive, set `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` and run a 12-month backfill from Claude Code:

```
python scripts/collect.py --keywords keywords.json --days 365 --platform-focus reddit --out raw-backfill
```

## 2. Set up Reddit Pro (free, 1 hour)

Reddit Pro gives a business profile, keyword tracking, trend volume, and community breakdowns. **Keywords chosen at setup cannot be removed later**, so start with durable ones:

| Keyword | Why it is safe to lock in |
|---|---|
| TD SYNNEX | The brand |
| Synnex | What most people actually type |
| Tech Data | Legacy name still in use |
| StreamOne | Flagship platform |
| disti | Channel slang for distributor; catches unbranded threads |

Add competitors and vendors later; adding is allowed, removing is not. Reddit Pro has no export or API, so move good threads into the dashboard with the Sightings inbox.

## 3. Run the Sightings inbox

| Channel | How |
|---|---|
| Dashboard | Sightings tab > paste the link > Add to inbox |
| Bookmarks bar | Drag the "+ Media Monitor" button from the Sightings tab to your bookmarks bar. Click it on any thread. |
| Teams | Create a channel named "Media Monitor Sightings". Schedule the Cowork prompt shown on the Sightings tab for weekdays. |
| Hunt list | Sightings tab > Hunt list: ready-made Reddit and Google searches built from your keywords and their aliases. Work a few each day. |

Then: Update data > Run research > Inbox only. Load the results file. Sightings flip to Analyzed.

## 4. Watch threads that matter

Click **Watch thread** on any conversation. The next research run re-opens it, updates the numbers, and records whether anyone from TD SYNNEX replied and how fast. Advanced > Response performance shows reply rate and median time to reply.

## 5. Earn the data

| Move | Notes |
|---|---|
| Reply from the Reddit Pro business account | Follow the response playbook in the skill: disclose, help, no hard sell. |
| AMA in r/msp | Message the moderators first; offer a product or program leader, not marketing. Pick a topic partners care about (pricing, StreamOne, AI programs). |
| Partner community | A subreddit TD SYNNEX moderates. Reddit's developer platform is allowed inside communities you moderate. Slow to build; only worth it with a community manager. |

## 6. Ask corporate before buying anything

Send to corporate communications or marketing operations:

> Subject: Do we already license a social listening platform?
>
> Hi [name], I'm piloting a Reddit and community monitoring dashboard for TD SYNNEX, our vendors, and competitors. Before we look at paid data, does TD SYNNEX already license Sprinklr, Brandwatch, Meltwater, or Talkwalker? If so, could we get read access or a scheduled export of Reddit and forum mentions for about 20 keywords? Sprinklr has a formal Reddit data partnership, which would keep us covered after Reddit closes its public API in March 2027. Happy to show the pilot. Thanks, [your name]

## What we do not do

Rotating proxies, fake accounts, large-scale bots, and leaked data dumps break Reddit's terms and can get TD SYNNEX accounts banned.
