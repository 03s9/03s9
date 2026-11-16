"""Gera activity.svg: últimas ações PÚBLICAS (PRs mergeados e commits). Só stdlib.

Uso: GH_TOKEN=... python3 scripts/gen_activity.py <user> <saida.svg>
"""
import json, os, sys, time, urllib.request
from datetime import datetime, timezone
from html import escape

USER, OUT = sys.argv[1], sys.argv[2]
TOKEN = os.environ.get("GH_TOKEN", "")
B, C, P = "#0032A8", "#FEF1CF", "#FC3B7F"
SKIP = ("chore: update generated assets",)


def api(path):
    req = urllib.request.Request("https://api.github.com" + path, headers={
        "Accept": "application/vnd.github+json", "User-Agent": "profile-activity",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def ago(iso):
    s = max(0, int(time.time() - datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp()))
    return "agora" if s < 120 else f"há {s // 60} min" if s < 3600 else f"há {s // 3600} h" if s < 86400 else f"há {s // 86400} d"


def trunc(s, n):
    return s if len(s) <= n else s[:n - 1] + "…"


rows, seen, fetched = [], set(), 0
for e in api(f"/users/{USER}/events/public?per_page=100"):
    repo, t = e["repo"]["name"].split("/")[-1], e["created_at"]
    p = e["payload"]
    if e["type"] == "PullRequestEvent" and (p.get("action") == "merged" or (p.get("action") == "closed" and p["pull_request"].get("merged"))):
        n, title = p["pull_request"]["number"], p["pull_request"].get("title")
        if not title and fetched < 15:
            try:
                title = api(f'/repos/{e["repo"]["name"]}/pulls/{n}')["title"]; fetched += 1
            except Exception:
                title = "(sem título)"
        key, row = ("pr", e["repo"]["name"], n), ("PR", f'#{n} {title or "(sem título)"}', repo, t)
    elif e["type"] == "PushEvent":
        msg = (p.get("commits") or [{}])[-1].get("message")
        if msg is None and p.get("head") and fetched < 15:
            try:
                msg = api(f'/repos/{e["repo"]["name"]}/commits/{p["head"]}')["commit"]["message"]; fetched += 1
            except Exception:
                continue
        if not msg:
            continue
        msg = msg.splitlines()[0]
        if msg.startswith(SKIP) or msg.startswith("Merge pull request"):
            continue
        key, row = ("c", p.get("head")), ("COMMIT", msg, repo, t)
    else:
        continue
    if key not in seen:
        seen.add(key); rows.append(row)
    if len(rows) >= 7:
        break

H = 96 + max(len(rows), 1) * 40 + 20
body = ""
for i, (kind, title, repo, t) in enumerate(rows):
    y = 100 + i * 40
    body += (f'<rect x="44" y="{y-15}" width="{70 if kind == "COMMIT" else 36}" height="22" rx="4" fill="{P if kind == "PR" else B}"/>'
             f'<text x="{49}" y="{y}" class="k">{kind}</text>'
             f'<text x="{128 if kind == "COMMIT" else 94}" y="{y}" class="t">{escape(trunc(title, 52))}</text>'
             f'<text x="716" y="{y}" class="t s">{escape(trunc(repo, 18))}</text><text x="880" y="{y}" class="t s">{ago(t)}</text>')
if not rows:
    body = f'<text x="44" y="110" class="t">Sem atividade pública recente.</text>'
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{H}" viewBox="0 0 1000 {H}" role="img" aria-label="Atividade recente no GitHub: PRs e commits públicos">
<title>Atividade recente</title>
<style>.h{{font:900 24px 'Courier New',ui-monospace,monospace;fill:{B};letter-spacing:2px}}.t{{font:700 16px 'Courier New',ui-monospace,monospace;fill:{B}}}.s{{font-size:14px}}.k{{font:900 12px 'Courier New',ui-monospace,monospace;fill:{C}}}</style>
<rect width="1000" height="{H}" rx="12" fill="{P}"/>
<rect x="28" y="28" width="960" height="{H-48}" rx="10" fill="{B}"/><rect x="20" y="20" width="960" height="{H-48}" rx="10" fill="{C}" stroke="{B}" stroke-width="3"/>
<text x="44" y="60" class="h">ATIVIDADE RECENTE</text><rect x="44" y="70" width="48" height="4" fill="{B}"/>{body}</svg>
'''
open(OUT, "w", encoding="utf-8").write(svg)
print("ok", OUT, len(rows), "rows")
