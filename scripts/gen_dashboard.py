"""Gera dashboard.svg com dados PÚBLICOS do GitHub (stdlib only).

Uso: GH_TOKEN=... python3 scripts/gen_dashboard.py <user> <saida.svg>
"""
import json, os, sys, urllib.request
from html import escape

USER, OUT = sys.argv[1], sys.argv[2]
TOKEN = os.environ.get("GH_TOKEN", "")
BLUE, CREAM, PINK = "#0032A8", "#FEF1CF", "#FC3B7F"


def api(path):
    req = urllib.request.Request("https://api.github.com" + path, headers={
        "Accept": "application/vnd.github+json", "User-Agent": "profile-dashboard",
        **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def contributions():
    if not TOKEN:
        return None
    q = '{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions}}}}' % USER
    req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": q}).encode(),
                                 headers={"Authorization": f"Bearer {TOKEN}", "User-Agent": "profile-dashboard"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)["data"]["user"]["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    except Exception:
        return None


user = api(f"/users/{USER}")
repos = [r for r in api(f"/users/{USER}/repos?per_page=100&type=owner") if not r["fork"] and not r["private"]]
langs = {}
for r in repos:
    for k, v in api(f"/repos/{USER}/{r['name']}/languages").items():
        langs[k] = langs.get(k, 0) + v
total = sum(langs.values()) or 1
top = sorted(langs.items(), key=lambda kv: -kv[1])[:5]
stars_recv = sum(r["stargazers_count"] for r in repos)
starred = [s for s in api(f"/users/{USER}/starred?per_page=30")
           if s["owner"]["login"].lower() != USER.lower() and not s["private"]][:5]
contrib = contributions()
nums = [("REPOS PÚBLICOS", len(repos)), ("ESTRELAS RECEBIDAS", stars_recv),
        ("SEGUIDORES", user["followers"]), ("CONTRIBUIÇÕES (12M)", "—" if contrib is None else contrib)]


def card(x, y, w, h, title, body):
    return (f'<rect x="{x+8}" y="{y+8}" width="{w}" height="{h}" rx="10" fill="{BLUE}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{CREAM}" stroke="{BLUE}" stroke-width="3"/>'
            f'<text x="{x+24}" y="{y+40}" class="h">{title}</text>'
            f'<rect x="{x+24}" y="{y+52}" width="48" height="4" fill="{BLUE}"/>{body}')


b1 = ""
for i, (name, v) in enumerate(top):
    yy = 100 + i * 42; pct = v / total * 100; bw = max(4, round(pct / 100 * 250))
    b1 += (f'<text x="44" y="{yy+14}" class="t">{escape(name)}</text>'
           f'<rect x="170" y="{yy}" width="250" height="18" rx="4" fill="{BLUE}" fill-opacity=".15"/>'
           f'<rect x="170" y="{yy}" width="{bw}" height="18" rx="4" fill="{PINK if i % 2 else BLUE}"/>'
           f'<text x="432" y="{yy+14}" class="t">{pct:.0f}%</text>')
b2 = ""
for i, (lab, v) in enumerate(nums):
    cx, cy = 534 + (i % 2) * 220, 100 + (i // 2) * 90
    b2 += f'<text x="{cx}" y="{cy+34}" class="n">{escape(str(v))}</text><text x="{cx}" y="{cy+58}" class="t s">{lab}</text>'
b3 = ""
for i, s in enumerate(starred):
    yy = 438 + i * 30
    b3 += (f'<text x="44" y="{yy}" class="t">★ {escape(s["full_name"][:44])}</text>'
           f'<text x="600" y="{yy}" class="t">{escape(s["language"] or "—")}</text>'
           f'<text x="860" y="{yy}" class="t">{s["stargazers_count"]:,} ★</text>')
H = 438 + max(len(starred), 1) * 30 + 30
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{H}" viewBox="0 0 1000 {H}" role="img" aria-label="Dashboard: linguagens mais usadas, números do GitHub e repositórios salvos">
<title>Dashboard de status</title>
<style>.h{{font:900 24px 'Courier New',ui-monospace,monospace;fill:{BLUE};letter-spacing:2px}}.t{{font:700 15px 'Courier New',ui-monospace,monospace;fill:{BLUE}}}.s{{font-size:13px}}.n{{font:900 40px 'Courier New',ui-monospace,monospace;fill:{BLUE}}}</style>
<rect width="1000" height="{H}" rx="12" fill="{PINK}"/>
{card(20, 20, 470, 300, "LINGUAGENS", b1)}
{card(510, 20, 470, 300, "NÚMEROS", b2)}
{card(20, 340, 960, H - 372, "SALVOS", b3)}
</svg>
'''
open(OUT, "w", encoding="utf-8").write(svg)
print("ok", OUT, [k for k, _ in top], len(starred))
