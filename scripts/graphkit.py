"""Mini toolkit de grafos em SVG: layout de forças (Fruchterman-Reingold, seed fixa) + render. Só stdlib."""
import math, random, zlib
from html import escape

BLUE, CREAM, PINK = "#0032A8", "#FEF1CF", "#FC3B7F"
CSS = f""".gl{{font:700 11px 'Courier New',ui-monospace,monospace;fill:{BLUE}}}
.pu{{opacity:0;animation:pl 4s ease-in-out infinite}}
@keyframes pl{{0%{{opacity:0;transform:translate(0,0)}}12%,88%{{opacity:1}}100%{{opacity:0;transform:translate(var(--dx),var(--dy))}}}}
.nd{{animation:nb 5s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:center}}
@keyframes nb{{to{{transform:translateY(-3px)}}}}
@media (prefers-reduced-motion:reduce){{.pu,.nd{{animation:none}}.pu{{opacity:0}}}}"""
FILL = {"a": BLUE, "b": PINK, "c": CREAM}


def layout(ids, edges, w, h, seed=3, iters=300, margin=46):
    rnd = random.Random(seed)
    pos = {i: [rnd.uniform(.25 * w, .75 * w), rnd.uniform(.25 * h, .75 * h)] for i in ids}
    n = max(len(ids), 1)
    k = math.sqrt(w * h / n) * 1.0
    t = w / 8
    cx, cy = w / 2, h / 2
    for _ in range(iters):
        disp = {i: [0.0, 0.0] for i in ids}
        for ai, a in enumerate(ids):
            for b in ids[ai + 1:]:
                dx, dy = pos[a][0] - pos[b][0], pos[a][1] - pos[b][1]
                d = max(math.hypot(dx, dy), .01); f = k * k / d
                disp[a][0] += dx / d * f; disp[a][1] += dy / d * f
                disp[b][0] -= dx / d * f; disp[b][1] -= dy / d * f
        for a, b, _w in edges:
            dx, dy = pos[a][0] - pos[b][0], pos[a][1] - pos[b][1]
            d = max(math.hypot(dx, dy), .01); f = d * d / k
            disp[a][0] -= dx / d * f; disp[a][1] -= dy / d * f
            disp[b][0] += dx / d * f; disp[b][1] += dy / d * f
        for i in ids:
            disp[i][0] -= (pos[i][0] - cx) * .3; disp[i][1] -= (pos[i][1] - cy) * .3
            L = max(math.hypot(*disp[i]), .01); s = min(L, t) / L
            pos[i][0] = min(w - margin, max(margin, pos[i][0] + disp[i][0] * s))
            pos[i][1] = min(h - margin, max(margin, pos[i][1] + disp[i][1] * s))
        t *= .975
    return pos


def render(nodes, edges, x0, y0, w, h, seed=3, max_pulses=10):
    """nodes: [{id,label,kind('a'|'b'|'c'),r}], edges: [(a,b,weight 0..1)]. Retorna fragmento SVG."""
    if not nodes:
        return f'<text x="{x0 + w / 2}" y="{y0 + h / 2}" text-anchor="middle" class="gl">sem dados</text>'
    ids = [n["id"] for n in nodes]
    pos = layout(ids, edges, w, h, seed)
    P = {i: (x0 + p[0], y0 + p[1]) for i, p in pos.items()}
    out = ""
    for a, b, wt in edges:
        out += (f'<line x1="{P[a][0]:.1f}" y1="{P[a][1]:.1f}" x2="{P[b][0]:.1f}" y2="{P[b][1]:.1f}" '
                f'stroke="{BLUE}" stroke-opacity=".35" stroke-width="{1 + 2.5 * wt:.1f}" stroke-linecap="round"/>')
    for i, (a, b, wt) in enumerate(sorted(edges, key=lambda e: -e[2])[:max_pulses]):
        (ax, ay), (bx, by) = P[a], P[b]
        out += (f'<circle class="pu" cx="{ax:.1f}" cy="{ay:.1f}" r="3.2" fill="{PINK}" '
                f'style="--dx:{bx - ax:.1f}px;--dy:{by - ay:.1f}px;animation-duration:{3 + i % 4}s;animation-delay:-{i * 0.9:.1f}s"/>')
    for n in nodes:
        x, y = P[n["id"]]; r = n["r"]
        out += (f'<g class="nd" style="animation-delay:-{(zlib.crc32(n["id"].encode()) % 50) / 10:.1f}s">'
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{FILL[n["kind"]]}" stroke="{BLUE}" stroke-width="2"/></g>'
                f'<text class="gl" x="{x:.1f}" y="{y + r + 14:.1f}" text-anchor="middle">{escape(n["label"])}</text>')
    return out
