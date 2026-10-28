#!/usr/bin/env python3
"""
Media Monitor collector: pulls raw candidates from Reddit, Hacker News, and YouTube.

What it does
  For each active keyword it searches the platforms, keeps posts inside the time window,
  fetches top comments, and saves everything to <out>/candidates.json. It also downloads
  post images and video thumbnails to <out>/images/ so the agent can read them with vision.
  The agent then reads candidates.json, opens pages as needed, and writes results.json.

Credentials (environment variables, all optional)
  REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET   Reddit app credentials (approved under Reddit's
                                           Responsible Builder Policy). Uses app-only OAuth.
  REDDIT_USER_AGENT                        e.g. "tdsynnex-media-monitor/1.0 by u/yourname"
  YOUTUBE_API_KEY                          YouTube Data API v3 key (free quota 10,000 units/day)
  Without Reddit credentials the script tries Reddit's public JSON endpoints, which are
  slow (rate limited), may be blocked from cloud servers, and may be withdrawn by Reddit.

Examples
  python collect.py --keywords keywords.json --days 30 --out raw
  python collect.py --keywords https://raw.githubusercontent.com/ccherosc/TDS_MEDIAMONITOR/main/data/keywords.json
  python collect.py --keywords keywords.json --sources reddit,hn --only td-synnex,pax8

Standard library only. Python 3.9+.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

UA = os.environ.get("REDDIT_USER_AGENT") or "tdsynnex-media-monitor/1.0 (research collector)"
DEFAULT_SUBS = {
    "Brand": ["msp", "sysadmin", "ITManagers"],
    "Distributor": ["msp", "sysadmin"],
    "Vendor": ["sysadmin", "ITManagers"],
    "Security": ["cybersecurity", "sysadmin", "msp"],
    "Technology": ["ITManagers", "sysadmin", "msp"],
    "Custom": ["sysadmin"],
}
IMG_RE = re.compile(r"https://(?:i\.redd\.it|preview\.redd\.it|i\.imgur\.com)/[^\s)\]\"']+", re.I)


def log(*a):
    print(*a, file=sys.stderr, flush=True)


class Http:
    """Tiny HTTP helper with retries and polite pacing. Replaceable in tests."""

    def __init__(self, min_interval=1.0):
        self.min_interval = min_interval
        self.last = {}

    def get(self, url, headers=None, data=None, host_interval=None):
        host = urllib.parse.urlsplit(url).netloc
        wait = (host_interval or self.min_interval) - (time.time() - self.last.get(host, 0))
        if wait > 0:
            time.sleep(wait)
        req = urllib.request.Request(url, data=data, headers={"User-Agent": UA, **(headers or {})})
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=30) as r:
                    self.last[host] = time.time()
                    body = r.read()
                    ctype = r.headers.get("Content-Type", "")
                    return json.loads(body) if "json" in ctype or body[:1] in (b"{", b"[") else body
            except urllib.error.HTTPError as e:
                self.last[host] = time.time()
                if e.code == 429 and attempt < 2:
                    time.sleep(10 * (attempt + 1))
                    continue
                raise
            except urllib.error.URLError:
                if attempt < 2:
                    time.sleep(3)
                    continue
                raise


def iso(ts):
    return dt.datetime.fromtimestamp(float(ts), dt.timezone.utc).date().isoformat()


def search_terms(kw):
    """Turn a keyword's boolean query into a few plain search strings."""
    q = kw.get("query") or kw["term"]
    parts = [p.strip() for p in re.split(r"\bOR\b", q) if p.strip()]
    terms = []
    for p in parts:
        p = re.sub(r"\s-\S+", "", " " + p).strip()  # drop exclusions for the API call; filter later
        if p and p not in terms:
            terms.append(p)
    if kw["term"] not in [t.strip('"') for t in terms]:
        terms.insert(0, '"%s"' % kw["term"])
    return terms[:4]


def excluded(kw, text):
    q = kw.get("query") or ""
    for neg in re.findall(r"\s-(\"[^\"]+\"|\S+)", " " + q):
        if neg.strip('"').lower() in (text or "").lower():
            return True
    return False


# ---------------- Reddit ----------------
class Reddit:
    def __init__(self, http):
        self.http = http
        self.token = None
        cid, sec = os.environ.get("REDDIT_CLIENT_ID"), os.environ.get("REDDIT_CLIENT_SECRET")
        if cid and sec:
            import base64
            auth = base64.b64encode(f"{cid}:{sec}".encode()).decode()
            try:
                r = http.get("https://www.reddit.com/api/v1/access_token", headers={"Authorization": "Basic " + auth},
                             data=b"grant_type=client_credentials")
                self.token = r.get("access_token")
                log("Reddit: using OAuth")
            except Exception as e:  # noqa: BLE001
                log("Reddit OAuth failed, falling back to public JSON:", e)
        self.base = "https://oauth.reddit.com" if self.token else "https://www.reddit.com"
        self.interval = 0.7 if self.token else 6.5  # stay under 100 QPM (OAuth) / 10 QPM (public)

    def _get(self, path, params):
        suffix = "" if self.token else ".json"
        url = f"{self.base}{path}{suffix}?{urllib.parse.urlencode(params)}"
        headers = {"Authorization": "Bearer " + self.token} if self.token else {}
        return self.http.get(url, headers=headers, host_interval=self.interval)

    def search(self, term, sub=None, t="month", limit=50):
        path = f"/r/{sub}/search" if sub else "/search"
        params = {"q": term, "sort": "relevance", "t": t, "limit": limit, "raw_json": 1}
        if sub:
            params["restrict_sr"] = 1
        data = self._get(path, params)
        return [c["data"] for c in (data or {}).get("data", {}).get("children", []) if c.get("kind") == "t3"]

    def comments(self, post_id, limit=20):
        data = self._get(f"/comments/{post_id}", {"limit": limit, "sort": "top", "depth": 2, "raw_json": 1})
        out = []
        if isinstance(data, list) and len(data) > 1:
            for c in data[1].get("data", {}).get("children", []):
                d = c.get("data", {})
                if c.get("kind") == "t1" and d.get("body"):
                    out.append({"author": "u/" + str(d.get("author")), "score": d.get("score"), "text": d["body"][:1500],
                                "is_submitter": d.get("is_submitter", False)})
        return sorted(out, key=lambda x: x.get("score") or 0, reverse=True)[:limit]


def collect_reddit(http, kw, since, max_items, n_comments):
    rd = Reddit(http) if not hasattr(collect_reddit, "rd") else collect_reddit.rd
    collect_reddit.rd = rd
    t = "week" if (dt.date.today() - since).days <= 7 else "month" if (dt.date.today() - since).days <= 31 else "year"
    subs = (kw.get("subreddits") or [])[:6] or DEFAULT_SUBS.get(kw.get("group"), [])
    seen, out = set(), []
    for term in search_terms(kw):
        for sub in [None] + subs:
            try:
                posts = rd.search(term, sub=sub, t=t)
            except Exception as e:  # noqa: BLE001
                log(f"  reddit search failed ({term} in {sub or 'all'}): {e}")
                if isinstance(e, urllib.error.HTTPError) and e.code in (401, 403):
                    log("  Reddit refused the request. Use approved API credentials or a paid feed (see Upgrades tab).")
                    return out
                continue
            for p in posts:
                if p["id"] in seen:
                    continue
                created = dt.datetime.fromtimestamp(p.get("created_utc", 0), dt.timezone.utc).date()
                text = (p.get("title", "") + " " + p.get("selftext", ""))
                if created < since or excluded(kw, text):
                    continue
                seen.add(p["id"])
                imgs = []
                if str(p.get("url", "")).lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".gif")):
                    imgs.append(p["url"])
                imgs += IMG_RE.findall(p.get("selftext", ""))
                out.append({"platform": "reddit", "source_name": "r/" + p.get("subreddit", ""), "id_hint": p["id"],
                            "url": "https://www.reddit.com" + p.get("permalink", ""), "title": p.get("title", ""),
                            "text": p.get("selftext", "")[:4000], "author": "u/" + str(p.get("author")),
                            "published_at": created.isoformat(),
                            "engagement": {"score": p.get("score"), "comments": p.get("num_comments"), "views": None, "likes": None},
                            "images": imgs[:4], "link_url": p.get("url")})
            if len(out) >= max_items * 2:
                break
    out.sort(key=lambda x: (x["engagement"]["score"] or 0) + 2 * (x["engagement"]["comments"] or 0), reverse=True)
    out = out[:max_items]
    for c in out:
        try:
            c["comments"] = rd.comments(c["id_hint"], n_comments)
        except Exception as e:  # noqa: BLE001
            c["comments"] = []
            log("  comments failed:", e)
    return out


# ---------------- Hacker News ----------------
def collect_hn(http, kw, since, max_items, n_comments):
    out, seen = [], set()
    ts = int(dt.datetime.combine(since, dt.time(), dt.timezone.utc).timestamp())
    for term in search_terms(kw)[:2]:
        q = urllib.parse.urlencode({"query": term.strip('"'), "tags": "story", "numericFilters": f"created_at_i>{ts}", "hitsPerPage": 30})
        try:
            data = http.get("https://hn.algolia.com/api/v1/search?" + q)
        except Exception as e:  # noqa: BLE001
            log("  hn failed:", e)
            continue
        for h in data.get("hits", []):
            if h["objectID"] in seen or excluded(kw, h.get("title", "")):
                continue
            seen.add(h["objectID"])
            out.append({"platform": "hackernews", "source_name": "Hacker News", "url": f"https://news.ycombinator.com/item?id={h['objectID']}",
                        "title": h.get("title") or "", "text": (h.get("story_text") or "")[:3000], "author": h.get("author"),
                        "published_at": iso(h["created_at_i"]), "link_url": h.get("url"),
                        "engagement": {"score": h.get("points"), "comments": h.get("num_comments"), "views": None, "likes": None},
                        "images": [], "id_hint": h["objectID"]})
    out.sort(key=lambda x: (x["engagement"]["score"] or 0), reverse=True)
    out = out[:max_items]
    for c in out:
        try:
            item = http.get(f"https://hn.algolia.com/api/v1/items/{c['id_hint']}")
            kids = sorted(item.get("children", []), key=lambda k: len(k.get("children", [])), reverse=True)
            c["comments"] = [{"author": k.get("author"), "score": None, "text": re.sub("<[^>]+>", " ", k.get("text") or "")[:1500]}
                             for k in kids[:n_comments] if k.get("text")]
        except Exception:  # noqa: BLE001
            c["comments"] = []
    return out


# ---------------- YouTube ----------------
def collect_youtube(http, kw, since, max_items, n_comments):
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        return []
    out, ids = [], []
    for term in search_terms(kw)[:2]:
        q = urllib.parse.urlencode({"part": "snippet", "q": term.strip('"'), "type": "video", "order": "relevance", "maxResults": 15,
                                    "publishedAfter": since.isoformat() + "T00:00:00Z", "key": key, "relevanceLanguage": "en"})
        try:
            data = http.get("https://www.googleapis.com/youtube/v3/search?" + q)
        except Exception as e:  # noqa: BLE001
            log("  youtube search failed:", e)
            continue
        for it in data.get("items", []):
            vid = it["id"].get("videoId")
            if vid and vid not in ids:
                ids.append(vid)
    if not ids:
        return []
    stats = {}
    for i in range(0, len(ids), 50):
        q = urllib.parse.urlencode({"part": "snippet,statistics", "id": ",".join(ids[i:i + 50]), "key": key})
        for v in http.get("https://www.googleapis.com/youtube/v3/videos?" + q).get("items", []):
            stats[v["id"]] = v
    for vid in ids:
        v = stats.get(vid)
        if not v:
            continue
        sn, st = v["snippet"], v.get("statistics", {})
        if excluded(kw, sn.get("title", "") + " " + sn.get("description", "")):
            continue
        thumbs = sn.get("thumbnails", {})
        thumb = (thumbs.get("maxres") or thumbs.get("high") or thumbs.get("medium") or {}).get("url")
        out.append({"platform": "youtube", "source_name": sn.get("channelTitle", "YouTube"), "url": f"https://www.youtube.com/watch?v={vid}",
                    "title": sn.get("title", ""), "text": sn.get("description", "")[:2000], "author": sn.get("channelTitle"),
                    "published_at": sn.get("publishedAt", "")[:10], "id_hint": vid,
                    "engagement": {"score": None, "comments": _int(st.get("commentCount")), "views": _int(st.get("viewCount")), "likes": _int(st.get("likeCount"))},
                    "images": [thumb] if thumb else []})
    out.sort(key=lambda x: x["engagement"]["views"] or 0, reverse=True)
    out = out[:max_items]
    for c in out:
        try:
            q = urllib.parse.urlencode({"part": "snippet", "videoId": c["id_hint"], "order": "relevance", "maxResults": n_comments, "textFormat": "plainText", "key": key})
            data = http.get("https://www.googleapis.com/youtube/v3/commentThreads?" + q)
            c["comments"] = [{"author": t["snippet"]["topLevelComment"]["snippet"].get("authorDisplayName"),
                              "score": t["snippet"]["topLevelComment"]["snippet"].get("likeCount"),
                              "text": t["snippet"]["topLevelComment"]["snippet"].get("textDisplay", "")[:1500]} for t in data.get("items", [])]
        except Exception:  # noqa: BLE001
            c["comments"] = []
    return out


def _int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def download_images(http, cands, folder, limit):
    os.makedirs(folder, exist_ok=True)
    n = 0
    for c in cands:
        c["local_images"] = []
        for u in c.get("images", []):
            if n >= limit:
                return
            ext = os.path.splitext(urllib.parse.urlsplit(u).path)[1].lower()
            ext = ext if ext in (".jpg", ".jpeg", ".png", ".webp", ".gif") else ".jpg"
            name = hashlib.sha1(u.encode()).hexdigest()[:12] + ext
            path = os.path.join(folder, name)
            try:
                body = http.get(u.replace("&amp;", "&"))
                if isinstance(body, (bytes, bytearray)) and len(body) < 8_000_000:
                    with open(path, "wb") as f:
                        f.write(body)
                    c["local_images"].append(path)
                    n += 1
            except Exception:  # noqa: BLE001
                pass


def load_keywords(src):
    if src.startswith(("http://", "https://")):
        data = Http().get(src)
    else:
        with open(src, encoding="utf-8") as f:
            data = json.load(f)
    kws = data.get("keywords", data) if isinstance(data, dict) else data
    return [k for k in kws if k.get("status", "active") == "active"]


def main(argv=None, http=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--keywords", required=True, help="keywords.json path or URL")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--out", default="raw")
    ap.add_argument("--sources", default="reddit,hn,youtube")
    ap.add_argument("--only", default="", help="comma-separated keyword ids")
    ap.add_argument("--max-per-keyword", type=int, default=25)
    ap.add_argument("--comments", type=int, default=15)
    ap.add_argument("--images", type=int, default=60, help="max images to download for vision (0 = none)")
    a = ap.parse_args(argv)
    http = http or Http()
    kws = load_keywords(a.keywords)
    if a.only:
        keep = set(a.only.split(","))
        kws = [k for k in kws if k["id"] in keep]
    since = dt.date.today() - dt.timedelta(days=a.days)
    srcs = set(a.sources.split(","))
    by_url = {}
    report = {}
    for kw in kws:
        log(f"Collecting {kw['term']} ...")
        got = []
        if "reddit" in srcs:
            got += collect_reddit(http, kw, since, a.max_per_keyword, a.comments)
        if "hn" in srcs:
            got += collect_hn(http, kw, since, max(5, a.max_per_keyword // 3), a.comments)
        if "youtube" in srcs:
            got += collect_youtube(http, kw, since, max(5, a.max_per_keyword // 2), a.comments)
        report[kw["id"]] = {}
        for c in got:
            report[kw["id"]][c["platform"]] = report[kw["id"]].get(c["platform"], 0) + 1
            if c["url"] in by_url:
                by_url[c["url"]]["keyword_ids"] = sorted(set(by_url[c["url"]]["keyword_ids"]) | {kw["id"]})
            else:
                c["keyword_ids"] = [kw["id"]]
                by_url[c["url"]] = c
    cands = list(by_url.values())
    for c in cands:
        c.pop("id_hint", None)
    if a.images:
        download_images(http, cands, os.path.join(a.out, "images"), a.images)
    os.makedirs(a.out, exist_ok=True)
    out = {"collected_at": dt.datetime.now(dt.timezone.utc).isoformat(), "window_days": a.days, "since": since.isoformat(),
           "sources": sorted(srcs), "per_keyword": report, "candidates": cands}
    path = os.path.join(a.out, "candidates.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    log(f"Saved {len(cands)} candidates to {path}")
    for k, v in report.items():
        log(f"  {k}: {v}")
    return out


if __name__ == "__main__":
    main()
