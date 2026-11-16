"""Gera heatmap.svg: contribuições dos últimos 12 meses na paleta OUTLOUD. Só stdlib.

Uso: GH_TOKEN=... python3 scripts/gen_heatmap.py <user> <saida.svg>   (token obrigatório: GraphQL)
"""
import json, os, sys, urllib.request
from datetime import date

USER, OUT, TOKEN = sys.argv[1], sys.argv[2], os.environ["GH_TOKEN"]
B, C, P = "#0032A8", "#FEF1CF", "#FC3B7F"
Q = '{user(login:"%s"){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}' % USER
req = urllib.request.Request("https://api.github.com/graphql", data=json.dumps({"query": Q}).encode(),
                             headers={"Authorization": f"Bearer {TOKEN}", "User-Agent": "profile-heatmap"})
cal = json.load(urllib.request.urlopen(req, timeout=30))["data"]["user"]["contributionsCollection"]["contributionCalendar"]
weeks, total = cal["weeks"], cal["totalContributions"]
mx = max((d["contributionCount"] for w in weeks for d in w["contributionDays"]), default=1) or 1
LV = ["#E9DFC0", "#9FB3E8", "#5C7CD6", B, P]


def level(n):
    return 0 if n == 0 else 1 if n <= mx * .25 else 2 if n <= mx * .5 else 3 if n <= mx * .8 else 4


CS, G, X0, Y0 = 13, 4, 44, 100
cells, months, last = "", "", None
for wi, w in enumerate(weeks):
    for d in w["contributionDays"]:
        dt = date.fromisoformat(d["date"]); y = Y0 + dt.weekday() * (CS + G) if False else Y0 + ((dt.weekday() + 1) % 7) * (CS + G)
        cells += f'<rect x="{X0 + wi * (CS + G)}" y="{y}" width="{CS}" height="{CS}" rx="3" fill="{LV[level(d["contributionCount"])]}"><title>{d["date"]}: {d["contributionCount"]}</title></rect>'
    m = date.fromisoformat(w["contributionDays"][0]["date"]).strftime("%b")
    if m != last:
        months += f'<text x="{X0 + wi * (CS + G)}" y="{Y0 - 10}" class="t s">{m}</text>'; last = m
H = Y0 + 7 * (CS + G) + 70
leg = "".join(f'<rect x="{760 + i * 20}" y="{H - 44}" width="{CS}" height="{CS}" rx="3" fill="{c}"/>' for i, c in enumerate(LV))
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="{H}" viewBox="0 0 1000 {H}" role="img" aria-label="Mapa de calor: {total} contribuições nos últimos 12 meses">
<title>Contribuições nos últimos 12 meses</title>
<style>.h{{font:900 24px 'Courier New',ui-monospace,monospace;fill:{B};letter-spacing:2px}}.t{{font:700 15px 'Courier New',ui-monospace,monospace;fill:{B}}}.s{{font-size:12px}}</style>
<rect width="1000" height="{H}" rx="12" fill="{P}"/>
<rect x="28" y="28" width="960" height="{H-48}" rx="10" fill="{B}"/><rect x="20" y="20" width="960" height="{H-48}" rx="10" fill="{C}" stroke="{B}" stroke-width="3"/>
<text x="44" y="60" class="h">CONTRIBUIÇÕES · {total} EM 12 MESES</text><rect x="44" y="70" width="48" height="4" fill="{B}"/>
{months}{cells}<text x="716" y="{H - 33}" class="t s">menos</text>{leg}<text x="872" y="{H - 33}" class="t s">mais</text></svg>
'''
open(OUT, "w", encoding="utf-8").write(svg)
print("ok", OUT, total, "contribs", len(weeks), "weeks")
