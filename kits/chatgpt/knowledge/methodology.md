# Methodology

How to judge each item and roll items up into insights. Consistency matters more than precision: two agents scoring the same thread should land close to each other.

## 1. Sentiment toward the keyword

Score sentiment toward the tracked keyword, not the overall mood of the post. A furious post about Microsoft licensing that praises how TD SYNNEX handled the change is negative for Microsoft and positive for TD SYNNEX.

| Score | Label | IT-channel example |
|---|---|---|
| +0.6 to +1.0 | positive | "Our TD SYNNEX rep saved the renewal, best support we've had from a distributor." |
| +0.25 to +0.6 | positive | "Pax8 billing sync with Autotask works fine for us." |
| -0.25 to +0.25 | neutral | Questions, how-to threads, factual news with no stance. |
| -0.6 to -0.25 | negative | "Ordering through their portal is clunky and quotes take days." |
| -1.0 to -0.6 | negative | "Billed for overnight shipping, arrived a week late, no refund, nobody answers." Breaches, outages, legal trouble. |

- Use **mixed** when strong praise and strong criticism sit side by side (score near the balance of the two).
- **confidence** (0-1): lower it for sarcasm, short posts, or when the keyword is mentioned in passing.
- **keyword_sentiment**: when a post mentions two or more tracked keywords with different sentiment, add one entry per keyword. Typical cases: switching stories, comparisons, "X is better than Y".
- Read the replies. If the original post is neutral but the top replies pile on with complaints, the item is negative. If replies push back on a complaint ("works fine for us"), consider mixed.

### Emotion (pick the dominant one)
frustration, anger, anxiety, confusion, disappointment, satisfaction, excitement, trust, curiosity, neutral.
Anxiety is common around security incidents and price changes; confusion around licensing; trust shows up in "we rely on them" language.

## 2. Aspects (what the sentiment is about)

| Aspect | Covers |
|---|---|
| pricing | List price, price increases, quotes |
| margins | Partner margin, rebates, MDF, incentives |
| support | Support quality, response time, account management |
| portal | Ordering portals, marketplaces, quoting tools, UX |
| logistics | Shipping, backorders, stock, returns, RMA |
| licensing | License terms, renewals, NCE, subscription rules |
| product_quality | Defects, firmware bugs, reliability |
| security | Vulnerabilities, breaches, patching |
| performance | Speed, outages, uptime |
| partner_program | Tiers, requirements, certifications, program changes |
| credit_terms | Credit lines, payment terms, financing |
| communication | Announcements, transparency, notice periods |
| other | Anything else |

Give each aspect its own sentiment (-1 to +1). The dashboard turns these into the pain-point matrix, so be specific: a shipping complaint is logistics, not support, unless the complaint is about nobody answering.

## 3. Signals

Tag every signal that applies.

| Signal | Tag when |
|---|---|
| brand_sentiment | The post expresses an opinion about the brand itself |
| praise | Clear positive endorsement or recommendation |
| product_issue | Bug, outage, defect, failed update, breach impact |
| product_feedback | Feature request or suggestion |
| buying_signal | Someone is choosing, comparing, budgeting, requesting quotes, or planning a refresh |
| partner_pain | A reseller, MSP, or partner describes friction with a vendor or distributor |
| competitor_switch | Moving from one vendor or distributor to another, or asking for alternatives |
| trend | Evidence of an emerging technology need or market shift |
| crisis | Security incident, outage, legal or regulatory action, layoffs, reputational event |
| influencer | Author or venue has outsized reach (see influence) |

### Intent stage (buying signals)
- **none**: no buying context.
- **research**: learning, "anyone using X?"
- **evaluating**: comparing named options, asking about pricing, running a pilot.
- **ready_to_buy**: asking where to buy, requesting quotes, budget approved, deadline mentioned.

## 4. Influence

| Level | Reddit | YouTube | Forums and reviews | News |
|---|---|---|---|---|
| high | 200+ upvotes or 100+ comments, or a top post in a large subreddit | 50K+ views or a channel with 100K+ subscribers | Accepted solution, pinned thread, 5K+ views | Tier-one trade press (CRN, The Register, BleepingComputer) or mainstream outlets |
| medium | 30-200 upvotes or 20-100 comments | 5K-50K views | 500-5K views or 10+ replies | Mid-size trade outlets |
| low | Below that | Below that | Below that | Blogs, small sites |

## 5. Themes and momentum

- A theme is a recurring story across at least two items (for example "Unanswered fulfillment and billing complaints").
- `mentions` = number of items in this run supporting it.
- Momentum compares with the previous run's themes for the same keyword (match by meaning, not exact name):
  - **rising**: new this run, or mentions up by 50% or more, or sentiment moved 0.3+ in either direction.
  - **fading**: mentions down by 50% or more.
  - **steady**: otherwise.
  - With no previous run, use dates: mostly in the last 14 days = rising.

## 6. Alerts

Raise an alert only with evidence ids. Severity:

| Type | High | Medium |
|---|---|---|
| crisis | Active exploitation, breach, outage, lawsuit, or regulator action involving the keyword | Credible report not yet confirmed |
| sentiment_drop | Net sentiment down 40+ points versus previous run (5+ items each run) | Down 25-40 points |
| volume_spike | 3x the previous run's items for the keyword | 2x |
| competitor_move | A competitor launches something that targets TD SYNNEX partners | Partnership, acquisition, or program change |
| opportunity | Clear demand TD SYNNEX can serve now | Emerging demand |

Net sentiment = (% positive) - (% negative), from -100 to +100.

## 7. Vision

When you can view images, check:

| Image type | What to record | Signal effect |
|---|---|---|
| Error dialogs, failed updates, crash screens | Product, version, error text | product_issue |
| Quotes, invoices, price lists, renewal notices | Price change, SKU, percentage | aspect pricing or licensing |
| Portal or marketplace screenshots | Which screen, what is broken or confusing | aspect portal, partner_pain |
| Vendor slides, event photos, roadmaps | The announcement or claim | trend |
| YouTube thumbnails | Framing: warnings, "worst", angry faces, comparisons, "vs" | adjusts emotion and confidence |
| Memes | The joke's target and stance | sentiment and emotion |

Write findings as one or two plain sentences ("Screenshot shows FortiOS 7.4.13 upgrade failing with error code -2 on a FortiGate 200F"). Never transcribe personal data visible in screenshots.

## 8. Synthesis checklist per keyword

1. What are people saying right now, in one sentence?
2. Which aspect hurts most and which is a strength?
3. Is anything new versus last run?
4. Who is loudest (communities, creators, outlets)?
5. Where can TD SYNNEX act this week?
