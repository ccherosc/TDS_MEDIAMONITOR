#!/usr/bin/env python3
"""
Media Monitor: validate, combine, and merge research results.

Plain-English summary
  - "check"   : validate one results file against the media-monitor.v1 rules and print problems.
  - "combine" : join several partial results files (for example one per keyword group) into ONE payload.
  - "merge"   : add a payload into the dashboard's data store (data/results.json). Same URL = same item,
                so nothing is double counted. Keeps run history and the newest keyword summaries.

Examples
  python merge_results.py check results.json
  python merge_results.py combine part1.json part2.json -o payload.json --agent claude --window-days 30
  python merge_results.py merge payload.json --store ../site/data/results.json

Only uses the Python standard library.
"""
import argparse
import datetime as dt
import hashlib
import json
import sys
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode

SCHEMA = "media-monitor.v1"
STORE_SCHEMA = "media-monitor.store.v1"
WORKSPACE = "tdsynnex-internal"
PLATFORMS = {"reddit", "youtube", "hackernews", "forum", "review", "news", "x", "linkedin", "podcast", "other"}
LABELS = {"positive", "neutral", "negative", "mixed"}
SIGNALS = {"brand_sentiment", "praise", "product_issue", "product_feedback", "buying_signal", "partner_pain",
           "competitor_switch", "trend", "crisis", "influencer"}
ASPECTS = {"pricing", "margins", "support", "portal", "logistics", "licensing", "product_quality", "security",
           "performance", "partner_program", "credit_terms", "communication", "other"}
STAGES = {"none", "research", "evaluating", "ready_to_buy"}
INFLUENCE = {"low", "medium", "high"}
DROP_PARAMS = ("utm_", "ref", "ref_source")
FOCUS = {"all", "reddit", "youtube", "others"}


def norm_focus(v):
    """Platform focus of a run: all (default), reddit, youtube, or others (everything else)."""
    if isinstance(v, list):
        v = v[0] if len(v) == 1 else "all"
    v = str(v or "all").lower()
    v = "others" if v == "other" else v
    return v if v in FOCUS else "all"


def now_iso():
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_url(url: str) -> str:
    """Match the dashboard: drop #fragment, utm_*/ref params, lowercase scheme+host, no trailing slash."""
    url = (url or "").strip()
    try:
        p = urlsplit(url)
        q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
             if not (k.lower().startswith("utm_") or k in ("ref", "ref_source"))]
        out = urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path or "/", urlencode(q), ""))
    except ValueError:
        out = url
    return out[:-1] if out.endswith("/") else out


def item_id(url: str) -> str:
    return hashlib.sha1(canonical_url(url).encode("utf-8")).hexdigest()[:12]


def _date(s):
    try:
        return dt.date.fromisoformat(str(s)[:10]).isoformat()
    except (ValueError, TypeError):
        return None


def _num(v):
    if v is None or v == "":
        return None
    try:
        f = float(v)
        return int(f) if f.is_integer() else f
    except (ValueError, TypeError):
        return None


def normalize_item(it: dict, problems: list, idx: int):
    where = f"items[{idx}]"
    if not isinstance(it, dict):
        problems.append(f"{where}: not an object, skipped")
        return None
    url = it.get("url", "")
    if not str(url).startswith(("http://", "https://")):
        problems.append(f"{where}: missing or invalid url, skipped")
        return None
    pub = _date(it.get("published_at"))
    if not pub:
        problems.append(f"{where} ({url}): missing published_at date, skipped")
        return None
    if not it.get("title"):
        problems.append(f"{where} ({url}): missing title, skipped")
        return None
    x = dict(it)
    x["url"] = url.strip()
    x["id"] = item_id(url)
    x["published_at"] = pub
    plat = str(x.get("platform", "other")).lower()
    x["platform"] = "hackernews" if plat in ("hn", "hacker news") else (plat if plat in PLATFORMS else "other")
    kws = x.get("keyword_ids") or ([x["keyword_id"]] if x.get("keyword_id") else [])
    x["keyword_ids"] = sorted(set(str(k) for k in kws))
    x.pop("keyword_id", None)
    if not x["keyword_ids"]:
        problems.append(f"{where} ({url}): no keyword_ids; it will not show on the dashboard")
    s = dict(x.get("sentiment") or {})
    label = str(s.get("label", "neutral")).lower()
    if label not in LABELS:
        problems.append(f"{where}: sentiment.label '{label}' unknown, set to neutral")
        label = "neutral"
    score = _num(s.get("score")) or 0
    s["label"], s["score"] = label, max(-1.0, min(1.0, float(score)))
    if s.get("confidence") is not None:
        s["confidence"] = max(0.0, min(1.0, float(_num(s.get("confidence")) or 0)))
    x["sentiment"] = s
    ks_out = {}
    for kid, ks in (x.get("keyword_sentiment") or {}).items():
        if isinstance(ks, dict) and str(ks.get("label", "")).lower() in LABELS:
            ks_out[str(kid)] = {"label": str(ks["label"]).lower(), "score": max(-1.0, min(1.0, float(_num(ks.get("score")) or 0)))}
    if ks_out:
        x["keyword_sentiment"] = ks_out
    else:
        x.pop("keyword_sentiment", None)
    eng = dict(x.get("engagement") or {})
    x["engagement"] = {k: _num(eng.get(k)) for k in ("score", "comments", "views", "likes", "rating")}
    x["signals"] = [g for g in (x.get("signals") or []) if g in SIGNALS]
    asp = []
    for a in x.get("aspects") or []:
        if isinstance(a, dict) and a.get("aspect") in ASPECTS:
            asp.append({"aspect": a["aspect"], "sentiment": max(-1.0, min(1.0, float(_num(a.get("sentiment")) or 0)))})
    x["aspects"] = asp
    x["intent_stage"] = x.get("intent_stage") if x.get("intent_stage") in STAGES else "none"
    x["influence"] = x.get("influence") if x.get("influence") in INFLUENCE else "low"
    words = str(x.get("excerpt") or "").split()
    if len(words) > 25:
        problems.append(f"{where}: excerpt longer than 25 words, trimmed")
        x["excerpt"] = " ".join(words[:25]) + "..."
    r = dict(x.get("response") or {})
    x["response"] = {"recommended": bool(r.get("recommended")), "priority": r.get("priority") if r.get("priority") in ("high", "medium", "low") else "low",
                     "draft": r.get("draft") or "", "rationale": r.get("rationale") or ""}
    if x["response"]["recommended"] and not x["response"]["draft"]:
        x["response"]["recommended"] = False
        problems.append(f"{where}: response recommended without a draft, turned off")
    v = dict(x.get("vision") or {})
    x["vision"] = {"analyzed": bool(v.get("analyzed")), "findings": v.get("findings") or ""}
    return x


def normalize_payload(p: dict, problems: list) -> dict:
    if isinstance(p, list):
        p = {"items": p}
    items, seen = [], {}
    for i, it in enumerate(p.get("items") or []):
        x = normalize_item(it, problems, i)
        if not x:
            continue
        if x["id"] in seen:  # same URL twice: merge keyword ids
            prev = seen[x["id"]]
            prev["keyword_ids"] = sorted(set(prev["keyword_ids"]) | set(x["keyword_ids"]))
            continue
        seen[x["id"]] = x
        items.append(x)
    ids = {x["id"] for x in items}
    old_to_new = {}
    for it in p.get("items") or []:
        if isinstance(it, dict) and it.get("url") and it.get("id"):
            old_to_new[it["id"]] = item_id(it["url"])

    def fix_ids(lst):
        out = []
        for e in lst or []:
            e = str(e)
            e2 = item_id(e) if e.startswith(("http://", "https://")) else old_to_new.get(e, e)
            if e2 in ids:
                out.append(e2)
        return sorted(set(out), key=out.index)

    kws = []
    for k in p.get("keywords") or []:
        if not isinstance(k, dict) or not k.get("id"):
            continue
        k = dict(k)
        k["themes"] = [dict(t, evidence_item_ids=fix_ids(t.get("evidence_item_ids"))) for t in (k.get("themes") or []) if isinstance(t, dict)]
        kws.append(k)
    ins = dict(p.get("insights") or {})
    for key in ("alerts", "trends", "recommended_actions"):
        ins[key] = [dict(e, evidence_item_ids=fix_ids(e.get("evidence_item_ids"))) for e in (ins.get(key) or []) if isinstance(e, dict)]
    ins["executive_summary"] = [str(b) for b in (ins.get("executive_summary") or [])]
    run = dict(p.get("run") or {})
    run.setdefault("id", "run-" + dt.date.today().isoformat() + "-" + hashlib.sha1(json.dumps(sorted(ids)).encode()).hexdigest()[:6])
    run.setdefault("agent", "other")
    run.setdefault("finished_at", now_iso())
    run["platform_focus"] = norm_focus(run.get("platform_focus"))
    focus = run["platform_focus"]
    if focus != "all":
        outside = [x for x in items if (x["platform"] if x["platform"] in ("reddit", "youtube") else "others") != focus]
        if outside:
            problems.append(f"{len(outside)} item(s) are outside the run's platform focus ({focus}); kept, but check the run")
    return {"schema": SCHEMA, "workspace": p.get("workspace") or WORKSPACE, "run": run, "keywords": kws, "items": items, "insights": ins}


def combine(payloads, agent, window_days, coverage, notes, run_id, platform_focus="all"):
    items, kws, ins = {}, {}, {"executive_summary": [], "alerts": [], "trends": [], "recommended_actions": []}
    for p in payloads:
        for it in p["items"]:
            if it["id"] in items:
                items[it["id"]]["keyword_ids"] = sorted(set(items[it["id"]]["keyword_ids"]) | set(it["keyword_ids"]))
            else:
                items[it["id"]] = it
        for k in p["keywords"]:
            kws[k["id"]] = k
        for key in ins:
            ins[key].extend(p["insights"].get(key) or [])
    for n, a in enumerate(ins["alerts"], 1):
        a["id"] = a.get("id") if a.get("id") and sum(1 for b in ins["alerts"] if b.get("id") == a.get("id")) == 1 else f"alert-{n}"
    started = now_iso()
    run = {"id": run_id or f"run-{dt.date.today().isoformat()}-{agent}", "agent": agent, "started_at": started, "finished_at": started,
           "window_days": window_days, "platform_focus": norm_focus(platform_focus),
           "sources_used": sorted({i["platform"] for i in items.values()}), "coverage": coverage, "notes": notes}
    return {"schema": SCHEMA, "workspace": WORKSPACE, "run": run, "keywords": list(kws.values()), "items": list(items.values()), "insights": ins}


def merge_into_store(store: dict, payload: dict) -> dict:
    store = store or {}
    store.setdefault("schema", STORE_SCHEMA)
    store.setdefault("workspace", payload.get("workspace") or WORKSPACE)
    run_id = payload["run"]["id"]
    today = dt.date.today().isoformat()
    by_id = {i["id"]: i for i in store.get("items") or []}
    for it in payload["items"]:
        prev = by_id.get(it["id"])
        if prev:
            eng = dict(prev.get("engagement") or {})
            eng.update({k: v for k, v in (it.get("engagement") or {}).items() if v is not None})
            merged = {**prev, **it, "engagement": eng,
                      "keyword_ids": sorted(set(prev.get("keyword_ids") or []) | set(it.get("keyword_ids") or [])),
                      "first_seen": prev.get("first_seen") or today, "last_seen": today,
                      "run_ids": list(dict.fromkeys((prev.get("run_ids") or []) + [run_id]))}
            by_id[it["id"]] = merged
        else:
            by_id[it["id"]] = {**it, "first_seen": today, "last_seen": today, "run_ids": [run_id]}
    store["items"] = sorted(by_id.values(), key=lambda i: i.get("published_at", ""), reverse=True)
    stamp = now_iso()
    focus = norm_focus(payload["run"].get("platform_focus"))
    kwi = store.get("keyword_insights") or {}
    by_focus = store.get("keyword_insights_by_focus") or {}
    for k in payload["keywords"]:
        entry = {"keyword_id": k["id"], "term": k.get("term", k["id"]), "summary": k.get("summary", ""), "themes": k.get("themes") or [],
                 "risks": k.get("risks") or [], "opportunities": k.get("opportunities") or [], "focus": focus, "run_id": run_id, "updated_at": stamp}
        if focus == "all":
            kwi[k["id"]] = entry          # the main read-out
        else:
            by_focus.setdefault(focus, {})[k["id"]] = entry   # shown when the dashboard is filtered to that platform
    store["keyword_insights"] = kwi
    store["keyword_insights_by_focus"] = by_focus
    run = dict(payload["run"], keyword_ids=[k["id"] for k in payload["keywords"]], item_count=len(payload["items"]),
               insights=payload.get("insights") or {}, imported_at=stamp)
    store["runs"] = [run] + [r for r in store.get("runs") or [] if r.get("id") != run_id][:59]
    store["updated_at"] = stamp
    return store


def report(payload, problems):
    from collections import Counter
    plat = Counter(i["platform"] for i in payload["items"])
    sent = Counter(i["sentiment"]["label"] for i in payload["items"])
    kw = Counter(k for i in payload["items"] for k in i["keyword_ids"])
    print(f"Run: {payload['run']['id']}  Platform focus: {payload['run'].get('platform_focus', 'all')}")
    print(f"Items: {len(payload['items'])}  Keywords with summaries: {len(payload['keywords'])}")
    print("By platform:", dict(plat))
    print("By sentiment:", dict(sent))
    print("By keyword:", dict(kw))
    print("Responses suggested:", sum(1 for i in payload["items"] if i["response"]["recommended"]))
    if problems:
        print(f"\n{len(problems)} note(s):")
        for p in problems[:60]:
            print("  -", p)


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("file")
    cb = sub.add_parser("combine")
    cb.add_argument("files", nargs="+")
    cb.add_argument("-o", "--out", required=True)
    cb.add_argument("--agent", default="other")
    cb.add_argument("--window-days", type=int, default=30)
    cb.add_argument("--run-id")
    cb.add_argument("--coverage", default="", help="e.g. reddit=full,youtube=partial,news=partial")
    cb.add_argument("--notes", default="")
    cb.add_argument("--platform-focus", default="all", choices=sorted(FOCUS))
    m = sub.add_parser("merge")
    m.add_argument("file")
    m.add_argument("--store", required=True)
    a = ap.parse_args()

    if a.cmd == "check":
        probs = []
        p = normalize_payload(load(a.file), probs)
        report(p, probs)
        sys.exit(1 if not p["items"] else 0)
    if a.cmd == "combine":
        probs, parts = [], []
        for f in a.files:
            parts.append(normalize_payload(load(f), probs))
        cov = dict(kv.split("=", 1) for kv in a.coverage.split(",") if "=" in kv)
        p = combine(parts, a.agent, a.window_days, cov, a.notes, a.run_id, a.platform_focus)
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump(p, f, indent=1, ensure_ascii=False)
        report(p, probs)
        print("Wrote", a.out)
    if a.cmd == "merge":
        probs = []
        p = normalize_payload(load(a.file), probs)
        try:
            store = load(a.store)
        except FileNotFoundError:
            store = {}
        store = merge_into_store(store, p)
        with open(a.store, "w", encoding="utf-8") as f:
            json.dump(store, f, indent=1, ensure_ascii=False)
        report(p, probs)
        print(f"Store now has {len(store['items'])} items and {len(store['runs'])} runs: {a.store}")


if __name__ == "__main__":
    main()
