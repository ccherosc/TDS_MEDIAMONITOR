# Sources and search playbook

## Query expansion

For each keyword, build several short queries instead of one long one.

| Pattern | Example for "TD SYNNEX" |
|---|---|
| Brand + community | `TD SYNNEX reddit`, `TD SYNNEX r/msp` |
| Brand + pain | `TD SYNNEX support`, `TD SYNNEX portal problems`, `TD SYNNEX backorder`, `TD SYNNEX credit` |
| Brand + switching | `TD SYNNEX vs Ingram Micro`, `alternative to TD SYNNEX`, `switched distributor` |
| Brand + program | `StreamOne ION review`, `TD SYNNEX partner program` |
| Brand + review sites | `TD SYNNEX G2`, `TD SYNNEX Trustpilot`, `TD SYNNEX Gartner Peer Insights` |
| Brand + video | `TD SYNNEX youtube`, `<product> review`, `<product> vs` |

Pain words that work in the IT channel: problem, issue, broken, outage, support, ticket, refund, price increase, renewal, license, margin, rebate, backorder, shipping, portal, quote, switch, alternative, vs, worth it, regret.

Buying words: recommend, which should I buy, quote, budget, refresh, rollout, pilot, POC, RFP, evaluating, shortlist.

Disambiguation examples: Pax8 (exclude gene, biology), Arrow (exclude TV series, archery), Apple (enterprise and device management only), Microsoft (exclude Xbox and consumer gaming), HP vs HPE (separate companies).

## Reddit (heaviest focus)

Collector (scripts/collect.py) handles search and comments when it can reach Reddit. Otherwise search the web for reddit.com threads and open them.

| Keyword group | Default subreddits |
|---|---|
| Brand, Distributor | msp, sysadmin, ITManagers, k12sysadmin, sales, Office365 |
| Vendor (PCs, servers) | sysadmin, ITManagers, Dell, Lenovo, thinkpad, homelab, macsysadmin, Intune |
| Vendor (networking) | networking, Cisco, meraki, Juniper, ArubaNetworks |
| Security | cybersecurity, sysadmin, msp, fortinet, paloaltonetworks, crowdstrike, netsec |
| Technology | ITManagers, sysadmin, msp, artificial, LocalLLaMA, AZURE, aws |

How to read a thread: the post, then the top 15-20 comments by score, plus any reply from a vendor or distributor employee. Capture score, comment count, and post date. Note whether anyone from the company has replied.

Rules: respect Reddit's rate limits and terms; use approved API credentials when you have them. Store only public usernames.

## YouTube

- Queries: `<term> review`, `<term> problems`, `<term> vs <competitor>`, `<term> 2026`, `<product> unboxing`, `<term> partner`.
- With an API key the collector returns views, likes, comment counts, and top comments. Read comments; that is where buyers argue.
- Useful IT channels to check for vendor and tech themes: Lawrence Systems, John Savill's Technical Training, NetworkChuck, ServeTheHome, Level1Techs, CBT Nuggets, Linus Tech Tips.
- Thumbnails go to vision (methodology.md).

## Hacker News

- Algolia API: `https://hn.algolia.com/api/v1/search_by_date?query=<term>&tags=(story,comment)`
- Strong for security incidents, AI, developer tooling, and big-vendor reputation. Weak for distribution.

## Community forums

Spiceworks Community, Microsoft Tech Community (CSP and partner boards), Cisco Community, Dell Community, HP Support Community, Lenovo Forums, Fortinet Community, Palo Alto Networks LIVEcommunity, MSPGeek, ChannelPro Network, Tek-Tips. Look for unanswered threads; those are reply opportunities.

## Review communities

G2, TrustRadius, Gartner Peer Insights, PeerSpot, Trustpilot, Capterra. Glassdoor and Indeed only for employer-brand context, and keep those to a few items. Capture the star rating in `engagement.rating`.

## News and trade press (context only)

CRN, ChannelE2E, Channel Futures, MSSP Alert, Channel Dive, The Register, BleepingComputer, SDxCentral, Computer Weekly, ITPro. Prefer articles that quote partners or customers. Keep news under 40% of items when community sources exist.

## X and LinkedIn

Only when web search surfaces a specific post, or when a paid feed is connected (see the dashboard's Upgrades tab). Do not log in or scrape behind logins.
