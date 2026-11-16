"""Gera graphs.svg: repos × linguagens, repos salvos por linguagem e mapa de gostos (AniList + Last.fm).

Uso: GH_TOKEN=... LASTFM_API_KEY=... python3 scripts/gen_graphs.py <github_user> <anilist_user> <lastfm_user> <saida.svg>
Dados públicos; Last.fm é pulado sem chave. Layout determinístico (seed fixa).
"""
import json, math, os, sys, urllib.parse, urllib.request
from collections import Counter
from html import escape

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import graphkit as gk

BLUE, CREAM, PINK = gk.BLUE, gk.CREAM, gk.PINK
W = 1000
TOKEN = os.environ.get("GH_TOKEN", "")


def get(url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "profile-graphs", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def gh(path):
    return get("https://api.github.com" + path, headers={"Accept": "application/vnd.github+json",
                                                         **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {})})


def trunc(s, n):
    return s if len(s) <= n else s[:n - 1] + "…"


def repos_graph(user):
    repos = [r for r in gh(f"/users/{user}/repos?per_page=100&type=owner") if not r["fork"] and not r["private"] and r["name"].lower() != user.lower()]
    nodes, edges, langs = [], [], Counter()
    for r in repos:
        l = gh(f"/repos/{user}/{r['name']}/languages")
        if not l:
            continue
        tot = sum(l.values())
        nodes.append({"id": "r:" + r["name"], "label": trunc(r["name"], 16), "kind": "a", "r": 7 + min(6, math.log10(tot + 1))})
        for k, v in l.items():
            edges.append(("r:" + r["name"], "l:" + k, v / tot)); langs[k] += v
    nodes += [{"id": "l:" + k, "label": k, "kind": "b", "r": 10 + min(8, math.log10(v + 1))} for k, v in langs.items()]
    return nodes, edges


def saved_graph(user):
    st = [s for s in gh(f"/users/{user}/starred?per_page=30")
          if s["owner"]["login"].lower() != user.lower() and not s["private"]][:14]
    nodes, edges, langs = [], [], Counter()
    for s in st:
        lang = s["language"] or "outros"
        nodes.append({"id": "s:" + s["full_name"], "label": trunc(s["name"], 14), "kind": "a",
                      "r": 5 + min(4, math.log10(s["stargazers_count"] + 1) / 1.5)})
        edges.append(("s:" + s["full_name"], "l:" + lang, .3)); langs[lang] += 1
    nodes += [{"id": "l:" + k, "label": k, "kind": "b", "r": 9 + 2 * v} for k, v in langs.items()]
    return nodes, edges


def anilist_graph(user):
    Q = ('query($u:String){User(name:$u){favourites{anime(perPage:5){nodes{title{romaji}genres}}manga(perPage:5){nodes{title{romaji}genres}}}}'
         'a:Page(perPage:5){mediaList(userName:$u,status:CURRENT,type:ANIME){media{title{romaji}genres}}}'
         'm:Page(perPage:5){mediaList(userName:$u,status:CURRENT,type:MANGA){media{title{romaji}genres}}}}')
    d = get("https://graphql.anilist.co", json.dumps({"query": Q, "variables": {"u": user}}).encode(),
            {"Content-Type": "application/json"})["data"]
    items = [e["media"] for e in d["a"]["mediaList"] + d["m"]["mediaList"]]
    items += d["User"]["favourites"]["anime"]["nodes"] + d["User"]["favourites"]["manga"]["nodes"]
    seen, titles = set(), []
    for m in items:
        t = m["title"]["romaji"]
        if t and t not in seen:
            seen.add(t); titles.append(m)
    titles = titles[:6]
    gc = Counter(g for m in titles for g in m["genres"])
    keep = {g for g, _ in gc.most_common(6)}
    nodes = [{"id": "t:" + m["title"]["romaji"], "label": trunc(m["title"]["romaji"], 14), "kind": "a", "r": 7} for m in titles]
    nodes += [{"id": "g:" + g, "label": g, "kind": "b", "r": 8 + 2 * gc[g]} for g in keep]
    edges = [("t:" + m["title"]["romaji"], "g:" + g, .3) for m in titles for g in m["genres"] if g in keep]
    return nodes, edges


def music_graph(user, key):
    def lf(method, **kw):
        return get("https://ws.audioscrobbler.com/2.0/?" + urllib.parse.urlencode(
            {"method": method, "user": user, "api_key": key, "format": "json", **kw}))
    arts = lf("user.gettopartists", period="overall", limit=5)["topartists"]["artist"]
    nodes, edges, tc = [], [], Counter()
    for a in arts:
        nodes.append({"id": "a:" + a["name"], "label": trunc(a["name"], 14), "kind": "c", "r": 8})
        tags = get("https://ws.audioscrobbler.com/2.0/?" + urllib.parse.urlencode(
            {"method": "artist.gettoptags", "artist": a["name"], "api_key": key, "format": "json"}))["toptags"]["tag"][:3]
        for t in tags:
            edges.append(("a:" + a["name"], "g:" + t["name"].lower(), .3)); tc[t["name"].lower()] += 1
    nodes += [{"id": "g:" + k, "label": trunc(k, 14), "kind": "b", "r": 8 + 2 * v} for k, v in tc.items()]
    return nodes, edges


def card(y, h, title, body):
    return (f'<rect x="28" y="{y + 8}" width="960" height="{h}" rx="10" fill="{BLUE}"/>'
            f'<rect x="20" y="{y}" width="960" height="{h}" rx="10" fill="{CREAM}" stroke="{BLUE}" stroke-width="3"/>'
            f'<text x="44" y="{y + 36}" class="h">{escape(title)}</text><rect x="44" y="{y + 46}" width="48" height="4" fill="{BLUE}"/>{body}')


def main(gh_user, al_user, lf_user, out):
    key = os.environ.get("LASTFM_API_KEY")
    CH = 360
    r_n, r_e = repos_graph(gh_user)
    s_n, s_e = saved_graph(gh_user)
    a_n, a_e = anilist_graph(al_user)
    m_n, m_e = music_graph(lf_user, key) if key else ([], [])
    body = card(20, CH, "REPOS × LINGUAGENS", gk.render(r_n, r_e, 40, 70, 920, CH - 70, seed=3))
    body += card(20 + CH + 24, CH, "SALVOS POR LINGUAGEM", gk.render(s_n, s_e, 40, 70 + CH + 24, 920, CH - 70, seed=5, max_pulses=12))
    y3 = 20 + 2 * (CH + 24)
    body += card(y3, CH, "MAPA DE GOSTOS · ANIME/MANGÁ + MÚSICA",
                 gk.render(a_n, a_e, 40, y3 + 70, 440, CH - 70, seed=7)
                 + gk.render(m_n, m_e, 520, y3 + 70, 440, CH - 70, seed=11)
                 + f'<rect x="498" y="{y3 + 64}" width="2" height="{CH - 80}" fill="{BLUE}" fill-opacity=".25"/>')
    H = y3 + CH + 28
    label = "Grafos: repositórios e linguagens, repositórios salvos por linguagem e mapa de gostos de anime, mangá e música"
    css = gk.CSS + f".h{{font:900 22px 'Courier New',ui-monospace,monospace;fill:{BLUE};letter-spacing:2px}}"
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(label)}">'
           f'<title>{escape(label)}</title><style>{css}</style><rect width="{W}" height="{H}" rx="12" fill="{PINK}"/>{body}</svg>\n')
    open(out, "w", encoding="utf-8").write(svg)
    print("ok", out, f"{W}x{H}", len(svg) // 1024, "KB", {"repos": len(r_n), "saved": len(s_n), "anime": len(a_n), "music": len(m_n)})


if __name__ == "__main__":
    main(*sys.argv[1:5])
