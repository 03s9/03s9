"""Compõe assets/badges-sky.svg: céu animado + badges (lidos de assets/badges/*.svg).

Uso: python3 scripts/gen_sky_badges.py
"""
import pathlib, random, re

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC, OUT = ROOT / "assets/badges", ROOT / "assets/badges-sky.svg"
ORDER = ["python", "rust", "sql", "java", "typescript", "claude-code", "git-cicd",
         "polars", "pandas", "fastapi", "spring-boot"]
BLUE, CREAM, PINK, NAVY = "#0032A8", "#FEF1CF", "#FC3B7F", "#061A63"
W, GAP, PAD = 1000, 14, 40
rnd = random.Random(7)  # céu determinístico


def parse(fn):
    s = (SRC / f"{fn}.svg").read_text()
    return dict(fn=fn, w=int(re.search(r'width="(\d+)"', s).group(1)),
                label=re.search(r'aria-label="([^"]+)"', s).group(1),
                path=re.search(r'<g transform="translate\(24 24\)[^>]*><path d="([^"]+)"', s).group(1))


def badge(b, i, x, y):
    w, dur, cd, d = b["w"], 3.6 + (i % 4) * .5, 9 + (i % 3) * 2, -(i * .7)
    return f'''<g transform="translate({x} {y})" aria-label="{b['label']}">
<g class="c1" style="animation-duration:{cd}s;animation-delay:{d}s" fill="{CREAM}" stroke="{BLUE}" stroke-width="1.5"><path d="M6 24a5 5 0 0 1 4-8 6 6 0 0 1 11-1 5 5 0 0 1 3 9z"/></g>
<g class="c2" style="animation-duration:{cd+3}s;animation-delay:{d}s" fill="{CREAM}" stroke="{BLUE}" stroke-width="1.5"><path d="M{w-34} 68a4 4 0 0 1 3-7 5 5 0 0 1 9-1 4 4 0 0 1 3 8z"/></g>
<g class="fl" style="animation-duration:{dur}s;animation-delay:{d}s">
<rect x="11" y="19" width="{w-16}" height="38" rx="19" fill="{BLUE}"/>
<rect x="8" y="16" width="{w-16}" height="38" rx="19" fill="{CREAM}" stroke="{BLUE}" stroke-width="2.5"/>
<g transform="translate(24 24) scale(1.0833)" fill="{BLUE}"><path d="{b['path']}"/></g>
<text class="t" x="56" y="40">{b['label']}</text></g></g>'''


badges = [parse(f) for f in ORDER]
rows, cur, cw = [], [], 0
for b in badges:
    if cur and cw + GAP + b["w"] > W - 2 * PAD:
        rows.append(cur); cur, cw = [], 0
    cw += (GAP if cur else 0) + b["w"]; cur.append(b)
rows.append(cur)
RH = 84; TOP = 56; H = TOP + len(rows) * RH + 36

body, i, centers = "", 0, {}
for r in rows:
    tw = sum(b["w"] for b in r) + GAP * (len(r) - 1); x = (W - tw) / 2
    for b in r:
        centers[b["fn"]] = (round(x) + b["w"] / 2, TOP + rows.index(r) * RH + 35)
        body += badge(b, i, round(x), TOP + rows.index(r) * RH); x += b["w"] + GAP; i += 1


# Constelação: quais ferramentas se conectam no meu dia a dia (linhas + pulsos)
EDGES = [("python", "pandas"), ("python", "polars"), ("python", "fastapi"), ("python", "sql"), ("pandas", "polars"),
         ("fastapi", "sql"), ("polars", "rust"), ("java", "spring-boot"), ("spring-boot", "sql"), ("typescript", "fastapi"),
         ("claude-code", "python"), ("claude-code", "git-cicd"), ("git-cicd", "rust"), ("git-cicd", "spring-boot")]
const = ""
for n, (a, b) in enumerate(EDGES):
    (ax, ay), (bx, by) = centers[a], centers[b]
    const += f'<line x1="{ax:.0f}" y1="{ay:.0f}" x2="{bx:.0f}" y2="{by:.0f}" stroke="{CREAM}" stroke-opacity=".28" stroke-width="1.2" stroke-dasharray="3 5"/>'
    const += (f'<circle class="cp" cx="{ax:.0f}" cy="{ay:.0f}" r="2.6" fill="{CREAM}" '
              f'style="--dx:{bx - ax:.0f}px;--dy:{by - ay:.0f}px;animation-duration:{5 + n % 4}s;animation-delay:-{n * 1.3:.1f}s"/>')

stars = "".join(
    f'<circle class="tw" style="animation-delay:{rnd.uniform(0, 5):.1f}s;animation-duration:{rnd.uniform(3, 6):.1f}s" '
    f'cx="{rnd.randint(8, W-8)}" cy="{rnd.randint(6, int(H*.75))}" r="{rnd.choice([1, 1, 1.5, 2])}" fill="{CREAM}"/>' for _ in range(70))
shoot = "".join(
    f'<g class="sh" style="animation-delay:{d}s;animation-duration:{dur}s;--x:{x0}px;--y:{y0}px"><line x1="0" y1="0" x2="-70" y2="-28" stroke="url(#tail)" stroke-width="2.5" stroke-linecap="round"/><circle r="2.6" fill="{CREAM}"/></g>'
    for d, dur, x0, y0 in [(1, 11, 160, 40), (5.5, 13, 560, 20), (9, 12, 820, 60)])
bird = lambda dl, dur, y, sc: (f'<g class="bd" style="animation-delay:{dl}s;animation-duration:{dur}s;--y:{y}px"><g transform="scale({sc})">'
                               f'<path class="wing" d="M-9 0Q-4.5 -6 0 0Q4.5 -6 9 0" fill="none" stroke="{CREAM}" stroke-width="2" stroke-linecap="round"/></g></g>')
birds = bird(-2, 38, 34, 1.2) + bird(-9, 46, 70, 0.9) + bird(-15, 42, 120, 1.0) + bird(-24, 52, 52, 0.8) + bird(-31, 44, 150, 1.1)
label = "Stack: " + ", ".join(b["label"] for b in badges)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">
<title>{label}</title>
<defs>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{NAVY}"/><stop offset=".55" stop-color="{BLUE}"/><stop offset="1" stop-color="{PINK}"/></linearGradient>
<linearGradient id="tail" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CREAM}" stop-opacity="0"/><stop offset="1" stop-color="{CREAM}"/></linearGradient>
</defs>
<style>
.t{{font-family:'Courier New',ui-monospace,monospace;font-weight:900;font-size:14px;fill:{BLUE}}}
.fl{{animation:fl 4s ease-in-out infinite}}.c1{{animation:d1 10s ease-in-out infinite alternate}}.c2{{animation:d2 12s ease-in-out infinite alternate}}
.tw{{animation:tw 4s ease-in-out infinite}}
.sh{{opacity:0;animation:sh 11s linear infinite}}
.bd{{animation:bd 40s linear infinite;transform:translate(-40px,var(--y))}}
.wing{{animation:fp .9s ease-in-out infinite alternate;transform-origin:0 0}}
@keyframes fl{{50%{{transform:translateY(-6px)}}}}@keyframes d1{{to{{transform:translateX(7px)}}}}@keyframes d2{{to{{transform:translateX(-7px)}}}}
@keyframes tw{{50%{{opacity:.25}}}}
@keyframes sh{{0%{{opacity:0;transform:translate(var(--x),var(--y))}}2%{{opacity:1}}9%{{opacity:1}}12%,100%{{opacity:0;transform:translate(calc(var(--x) + 190px),calc(var(--y) + 76px))}}}}
.cp{{opacity:0;animation:cpl 6s ease-in-out infinite}}
@keyframes cpl{{0%{{opacity:0;transform:translate(0,0)}}15%,85%{{opacity:.9}}100%{{opacity:0;transform:translate(var(--dx),var(--dy))}}}}
@keyframes bd{{to{{transform:translate({W+40}px,var(--y))}}}}
@keyframes fp{{from{{transform:scaleY(1)}}to{{transform:scaleY(-.6)}}}}
@media (prefers-reduced-motion:reduce){{.fl,.c1,.c2,.tw,.sh,.bd,.wing,.cp{{animation:none}}.sh,.cp{{opacity:0}}}}
</style>
<rect width="{W}" height="{H}" rx="14" fill="url(#sky)"/>
{stars}
{const}
{shoot}
{birds}
{body}
</svg>
'''
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(svg)
print("ok", OUT, f"{W}x{H}", len(svg) // 1024, "KB", "rows", [len(r) for r in rows])
