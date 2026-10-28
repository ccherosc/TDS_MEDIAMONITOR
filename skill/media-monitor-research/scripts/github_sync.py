#!/usr/bin/env python3
"""
Media Monitor GitHub sync: read the keyword list and publish results to the dashboard repo.

  python github_sync.py pull-keywords [--out keywords.json]
  python github_sync.py pull-queue [--out queue.json]  # pending sightings + watched threads
  python github_sync.py push results.json            # merges into data/results.json and commits

Settings (flags or environment variables)
  --repo   / MM_REPO       default ccherosc/TDS_MEDIAMONITOR
  --branch / MM_BRANCH     default main
  GITHUB_TOKEN             fine-grained token, Contents: read and write on that repo only.
                           Needed for push; optional for pull on a public repo.

Standard library only.
"""
import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import merge_results as mr  # noqa: E402

API = "https://api.github.com"


def _req(method, url, token=None, body=None, accept="application/vnd.github+json"):
    headers = {"Accept": accept, "X-GitHub-Api-Version": "2022-11-28", "User-Agent": "media-monitor-sync"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = json.dumps(body).encode() if body is not None else None
    if data:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
            return r.status, raw
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def read_file(repo, branch, path, token):
    """Returns (parsed_json_or_None, sha_or_None)."""
    st, raw = _req("GET", f"{API}/repos/{repo}/contents/{path}?ref={branch}", token)
    if st == 404:
        return None, None
    if st != 200:
        raise SystemExit(f"GitHub read of {path} failed ({st}): {raw[:200]!r}")
    meta = json.loads(raw)
    if meta.get("content"):
        text = base64.b64decode(meta["content"]).decode("utf-8")
    else:  # files over 1 MB: fetch raw
        st2, raw2 = _req("GET", f"{API}/repos/{repo}/contents/{path}?ref={branch}", token, accept="application/vnd.github.raw+json")
        if st2 != 200:
            raise SystemExit(f"GitHub raw read of {path} failed ({st2})")
        text = raw2.decode("utf-8")
    return json.loads(text), meta.get("sha")


def write_file(repo, branch, path, obj, sha, token, message):
    body = {"message": message, "branch": branch,
            "content": base64.b64encode((json.dumps(obj, indent=1, ensure_ascii=False) + "\n").encode("utf-8")).decode()}
    if sha:
        body["sha"] = sha
    return _req("PUT", f"{API}/repos/{repo}/contents/{path}", token, body)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=os.environ.get("MM_REPO", "ccherosc/TDS_MEDIAMONITOR"))
    ap.add_argument("--branch", default=os.environ.get("MM_BRANCH", "main"))
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("pull-keywords")
    p.add_argument("--out", default="keywords.json")
    p.add_argument("--all", action="store_true", help="include paused keywords")
    qp = sub.add_parser("pull-queue", help="pending sightings + watched threads -> queue.json")
    qp.add_argument("--out", default="queue.json")
    u = sub.add_parser("push")
    u.add_argument("file")
    u.add_argument("--message", default=None)
    a = ap.parse_args(argv)
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

    if a.cmd == "pull-keywords":
        data, _ = read_file(a.repo, a.branch, "data/keywords.json", token)
        if not data:
            raise SystemExit("data/keywords.json not found in " + a.repo)
        kws = data.get("keywords", [])
        if not a.all:
            kws = [k for k in kws if k.get("status", "active") == "active"]
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump({"schema": "media-monitor.keywords.v1", "workspace": data.get("workspace"), "keywords": kws}, f, indent=1, ensure_ascii=False)
        print(f"Saved {len(kws)} active keywords to {a.out}")
        for k in kws:
            print(f"  {k['id']:<22} {k['term']}  ({k.get('group', '')})")
        return

    if a.cmd == "pull-queue":
        sightings, _ = read_file(a.repo, a.branch, "data/sightings.json", token)
        state, _ = read_file(a.repo, a.branch, "data/state.json", token)
        results, _ = read_file(a.repo, a.branch, "data/results.json", token)
        analyzed = {i["id"] for i in (results or {}).get("items", [])}
        by_id = {i["id"]: i for i in (results or {}).get("items", [])}
        pend = [{"url": s["url"], "keyword_ids": s.get("keyword_ids", []), "note": s.get("note", "")}
                for s in ((sightings or {}).get("items") or {}).values()
                if s.get("status", "pending") == "pending" and s.get("id") not in analyzed]
        watch = [{"url": by_id[i]["url"], "id": i, "keyword_ids": by_id[i].get("keyword_ids", [])}
                 for i, st in ((state or {}).get("items") or {}).items() if st.get("watch") and i in by_id]
        with open(a.out, "w", encoding="utf-8") as f:
            json.dump({"sightings": pend, "watch": watch}, f, indent=1, ensure_ascii=False)
        print(f"Saved {len(pend)} pending sightings and {len(watch)} watched threads to {a.out}")
        return

    if a.cmd == "push":
        if not token:
            raise SystemExit("Set GITHUB_TOKEN (fine-grained, Contents read/write on the repo) to push.")
        problems = []
        payload = mr.normalize_payload(mr.load(a.file), problems)
        if not payload["items"]:
            raise SystemExit("No valid items in the file. Run merge_results.py check first.")
        for attempt in range(2):
            store, sha = read_file(a.repo, a.branch, "data/results.json", token)
            store = mr.merge_into_store(store or {}, payload)
            msg = a.message or f"Research run {payload['run']['id']}: {len(payload['items'])} items"
            st, raw = write_file(a.repo, a.branch, "data/results.json", store, sha, token, msg)
            if st in (200, 201):
                mr.report(payload, problems)
                print(f"Committed to {a.repo}/data/results.json ({len(store['items'])} items on file). Pages updates in about a minute.")
                return
            if st == 409 and attempt == 0:
                print("Someone else updated the file; retrying with the latest version...")
                continue
            raise SystemExit(f"GitHub write failed ({st}): {raw[:300]!r}")


if __name__ == "__main__":
    main()
