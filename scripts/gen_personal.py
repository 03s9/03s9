"""Gera anilist.svg e music.svg (seção "Pessoal & gostos"). Só biblioteca padrão.

Uso: LASTFM_API_KEY=... python3 scripts/gen_personal.py <anilist_user> <lastfm_user> <pasta_saida>
Sem LASTFM_API_KEY a parte de música é pulada (exit 0). Dados são um snapshot (não é "ao vivo").
"""
import base64, json, os, sys, time, urllib.parse, urllib.request
from html import escape

BLUE, CREAM, PINK, NAVY = "#0032A8", "#FEF1CF", "#FC3B7F", "#061A63"
W = 1000
CSS = f""".h{{font:900 22px 'Courier New',ui-monospace,monospace;fill:{BLUE};letter-spacing:2px}}
.t{{font:700 13px 'Courier New',ui-monospace,monospace;fill:{BLUE}}}.s{{font-size:11px;font-weight:400}}
.n{{font:900 34px 'Courier New',ui-monospace,monospace;fill:{BLUE}}}.l{{font:700 12px 'Courier New',ui-monospace,monospace;fill:{BLUE}}}
.cv{{animation:fl 4.5s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
@keyframes fl{{0%,100%{{transform:translateY(0) rotate(0)}}50%{{transform:translateY(-5px) rotate(1.5deg)}}}}
.disc{{animation:sp 9s linear infinite;transform-box:fill-box;transform-origin:center}}
@keyframes sp{{to{{transform:rotate(360deg)}}}}
.bar{{animation:eq 1s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:bottom}}
@keyframes eq{{from{{transform:scaleY(.25)}}to{{transform:scaleY(1)}}}}
@media (prefers-reduced-motion:reduce){{.cv,.disc,.bar{{animation:none}}}}"""


def get(url, data=None, headers=None, raw=False):
    req = urllib.request.Request(url, data=data, headers={"User-Agent": "profile-personal", **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        b = r.read()
    return b if raw else json.loads(b)


def img64(url):
    try:
        b = get(url, raw=True)
        if len(b) > 100_000:
            return None
        mime = "image/png" if b[:4] == b"\x89PNG" else "image/jpeg"
        return f"data:{mime};base64," + base64.b64encode(b).decode()
    except Exception:
        return None


def trunc(s, n):
    return s if len(s) <= n else s[:n - 1] + "…"


def card(x, y, w, h, title, inner):
    return (f'<rect x="{x+8}" y="{y+8}" width="{w}" height="{h}" rx="10" fill="{BLUE}"/>'
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{CREAM}" stroke="{BLUE}" stroke-width="3"/>'
            f'<text x="{x+24}" y="{y+36}" class="h">{escape(title)}</text>'
            f'<rect x="{x+24}" y="{y+46}" width="48" height="4" fill="{BLUE}"/>{inner}')


def covers(items, x0, y0, cw, ch, gap, uid):
    """Linha de capas animadas. items: [{title, sub, img}]"""
    out = ""
    for i, it in enumerate(items):
        x = x0 + i * (cw + gap)
        cid = f"{uid}{i}"
        art = (f'<image href="{it["img"]}" width="{cw}" height="{ch}" preserveAspectRatio="xMidYMid slice" clip-path="url(#{cid})"/>'
               if it["img"] else f'<rect width="{cw}" height="{ch}" rx="6" fill="{PINK}"/>')
        out += (f'<g transform="translate({x} {y0})"><clipPath id="{cid}"><rect width="{cw}" height="{ch}" rx="6"/></clipPath>'
                f'<g class="cv" style="animation-delay:-{i*0.8:.1f}s;animation-duration:{4+i%3*0.5}s">'
                f'<rect x="4" y="4" width="{cw}" height="{ch}" rx="6" fill="{BLUE}"/>{art}'
                f'<rect width="{cw}" height="{ch}" rx="6" fill="none" stroke="{BLUE}" stroke-width="2.5"/></g>'
                f'<text x="0" y="{ch+22}" class="t">{escape(trunc(it["title"], max(8, cw // 8)))}</text>'
                f'<text x="0" y="{ch+38}" class="t s">{escape(it["sub"])}</text></g>')
    return out


def wrap(h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" viewBox="0 0 {W} {h}" role="img" aria-label="{escape(label)}">'
            f'<title>{escape(label)}</title><style>{CSS}</style><rect width="{W}" height="{h}" rx="12" fill="{PINK}"/>{body}</svg>\n')


def render_anilist(d):
    u = d["User"]; a, m = u["statistics"]["anime"], u["statistics"]["manga"]
    nums = [("ANIMES", a["count"]), ("EPISÓDIOS", a["episodesWatched"]), ("HORAS", round(a["minutesWatched"] / 60)),
            ("NOTA ANIME", f'{a["meanScore"] / 10:.1f}' if a["meanScore"] else "—"), ("MANGÁS", m["count"]),
            ("CAPÍTULOS", m["chaptersRead"]), ("NOTA MANGÁ", f'{m["meanScore"] / 10:.1f}' if m["meanScore"] else "—")]
    st = "".join(f'<text x="{44+i*134}" y="108" class="n">{escape(str(v))}</text><text x="{44+i*134}" y="130" class="l">{lab}</text>'
                 for i, (lab, v) in enumerate(nums))
    body, y = card(20, 20, 960, 130, "ESTATÍSTICAS", st), 170

    def item(media, sub, uid):
        return {"title": media["title"]["romaji"] or "?", "sub": sub, "img": img64(media["coverImage"]["medium"])}

    sections = [
        ("ASSISTINDO", [item(e["media"], f'ep {e["progress"]}', "w") for e in d["cur"]["mediaList"]][:5]),
        ("LENDO", [item(e["media"], f'cap {e["progress"]}', "r") for e in d["curm"]["mediaList"]][:5]),
        ("FAVORITOS · ANIME", [item(n, "favorito", "fa") for n in u["favourites"]["anime"]["nodes"]][:5]),
        ("FAVORITOS · MANGÁ", [item(n, "favorito", "fm") for n in u["favourites"]["manga"]["nodes"]][:5]),
    ]
    for k, (title, its) in enumerate(sections):
        if not its:
            continue
        h = 70 + 156 + 56
        body += card(20, y, 960, h, title, covers(its, 44, y + 66, 110, 156, 54, f"c{k}_"))
        y += h + 24
    return wrap(y + 4, body, f'AniList de {u["name"]}: {a["count"]} animes, {m["count"]} mangás'
                f', {len(d["cur"]["mediaList"])} assistindo agora')


def ago(uts):
    s = max(0, int(time.time()) - int(uts))
    return "recente" if s < 3600 else f"há {s // 3600} h" if s < 86400 else f"há {s // 86400} d"


def render_music(user, tracks, artists):
    first = tracks[0] if tracks else None
    disc = (f'<g transform="translate(40 80)"><g class="disc"><circle cx="100" cy="100" r="98" fill="#111"/>'
            + "".join(f'<circle cx="100" cy="100" r="{r}" fill="none" stroke="#333" stroke-width="1"/>' for r in (86, 74, 62, 50))
            + '<clipPath id="lbl"><circle cx="100" cy="100" r="38"/></clipPath>'
            + (f'<image href="{first["img"]}" x="62" y="62" width="76" height="76" preserveAspectRatio="xMidYMid slice" clip-path="url(#lbl)"/>'
               if first and first["img"] else f'<circle cx="100" cy="100" r="38" fill="{PINK}"/>')
            + f'<circle cx="100" cy="100" r="4" fill="{CREAM}"/></g></g>')
    bars = "".join(f'<rect class="bar" aria-hidden="true" x="{44 + i * 10}" y="300" width="6" height="40" fill="{BLUE}" '
                   f'style="animation-duration:{0.5 + (i * 37 % 7) / 10:.1f}s;animation-delay:-{(i * 13 % 9) / 10:.1f}s"/>' for i in range(20))
    rows = f'<text x="270" y="96" class="t">#  ARTISTA — FAIXA</text><text x="760" y="96" class="t">ÁLBUM · QUANDO</text>'
    rows += f'<rect x="270" y="104" width="680" height="2" fill="{BLUE}"/>'
    for i, t in enumerate(tracks[:5]):
        yy = 134 + i * 40
        rows += (f'<text x="270" y="{yy}" class="t">{i+1:02d} {escape(trunc(t["artist"] + " — " + t["name"], 52))}</text>'
                 f'<text x="760" y="{yy}" class="t s">{escape(trunc(t["album"], 16))} · {escape(t["when"])}</text>')
    top = max((a["plays"] for a in artists), default=1) or 1
    tb = ""
    for i, a in enumerate(artists[:5]):
        yy = 462 + i * 34
        tb += (f'<text x="44" y="{yy+14}" class="t">{escape(trunc(a["name"], 22))}</text>'
               f'<rect x="300" y="{yy}" width="560" height="16" rx="4" fill="{BLUE}" fill-opacity=".15"/>'
               f'<rect x="300" y="{yy}" width="{max(6, round(a["plays"] / top * 560))}" height="16" rx="4" fill="{PINK if i % 2 else BLUE}"/>'
               f'<text x="872" y="{yy+13}" class="t s">{a["plays"]:,}</text>')
    n = max(len(artists[:5]), 1)
    H = 390 + 76 + n * 34 + 30
    body = (card(20, 20, 960, 350, "ÚLTIMAS OUVIDAS", disc + bars + rows)
            + card(20, 390, 960, 76 + n * 34 + 10, "TOP ARTISTAS (GERAL)", tb))
    return wrap(H, body, f"Last.fm de {user}: últimas ouvidas e top artistas")


def lastfm(user, key, method, **kw):
    q = urllib.parse.urlencode({"method": method, "user": user, "api_key": key, "format": "json", **kw})
    return get("https://ws.audioscrobbler.com/2.0/?" + q)


def main(al_user, lf_user, out):
    os.makedirs(out, exist_ok=True)
    Q = ('query($u:String){User(name:$u){name statistics{anime{count minutesWatched meanScore episodesWatched}manga{count chaptersRead meanScore}}'
         'favourites{anime(perPage:5){nodes{title{romaji}coverImage{medium}}}manga(perPage:5){nodes{title{romaji}coverImage{medium}}}}}'
         'cur:Page(perPage:5){mediaList(userName:$u,status:CURRENT,type:ANIME,sort:UPDATED_TIME_DESC){progress media{title{romaji}coverImage{medium}}}}'
         'curm:Page(perPage:5){mediaList(userName:$u,status:CURRENT,type:MANGA,sort:UPDATED_TIME_DESC){progress media{title{romaji}coverImage{medium}}}}}')
    d = get("https://graphql.anilist.co", json.dumps({"query": Q, "variables": {"u": al_user}}).encode(),
            {"Content-Type": "application/json"})["data"]
    open(os.path.join(out, "anilist.svg"), "w", encoding="utf-8").write(render_anilist(d))
    print("ok anilist.svg")
    key = os.environ.get("LASTFM_API_KEY")
    if not key:
        print("skip music: LASTFM_API_KEY ausente"); return
    rec = lastfm(lf_user, key, "user.getrecenttracks", limit=5)["recenttracks"]["track"]
    tracks = []
    for t in rec[:5]:
        art = next((i["#text"] for i in reversed(t.get("image", [])) if i["#text"] and "2a96cbd8b46e442fc41c2b86b821562f" not in i["#text"]), None)
        when = "recente" if t.get("@attr", {}).get("nowplaying") else ago(t["date"]["uts"])
        tracks.append({"artist": t["artist"]["#text"], "name": t["name"], "album": t["album"]["#text"] or "—",
                       "img": img64(art) if art else None, "when": when})
    ta = lastfm(lf_user, key, "user.gettopartists", period="overall", limit=5)["topartists"]["artist"]
    artists = [{"name": a["name"], "plays": int(a["playcount"])} for a in ta]
    open(os.path.join(out, "music.svg"), "w", encoding="utf-8").write(render_music(lf_user, tracks, artists))
    print("ok music.svg", len(tracks), len(artists))


if __name__ == "__main__":
    main(*sys.argv[1:4])
