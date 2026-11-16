"""Compõe assets/generated/bonsai-scene.svg: bonsai (do git-bonsai) num cenário OUTLOUD.

Uso: python3 scripts/gen_bonsai_scene.py [bonsai.svg] [saida.svg]
O bonsai.svg embute um PNG 768x768 transparente; recortamos a árvore e a animamos (balanço + pétalas).
"""
import pathlib, random, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "assets/generated/bonsai.svg"
OUT = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "assets/generated/bonsai-scene.svg"
BLUE, CREAM, PINK, NAVY = "#0032A8", "#FEF1CF", "#FC3B7F", "#061A63"
W, H = 1000, 420
CROP = (200, 320, 370, 380)  # x, y, w, h dentro dos 768x768 (ajustado ao bonsai atual)
href = re.search(r'href="(data:image/png;base64,[^"]+)"', SRC.read_text()).group(1)
rnd = random.Random(11)

stars = "".join(
    f'<circle class="tw" style="animation-delay:-{rnd.uniform(0, 5):.1f}s;animation-duration:{rnd.uniform(3, 6):.1f}s" '
    f'cx="{rnd.randint(10, W - 10)}" cy="{rnd.randint(8, 250)}" r="{rnd.choice([1, 1, 1.5, 2])}" fill="{CREAM}"/>' for _ in range(60))
petals = "".join(
    f'<ellipse class="pt" cx="{x}" cy="-10" rx="5" ry="3" fill="{c}" '
    f'style="--dx:{dx}px;animation-duration:{d}s;animation-delay:-{dl:.1f}s"/>'
    for x, dx, d, dl, c in [(300, 140, 11, 0, PINK), (380, 120, 13, 4, CREAM), (470, 160, 12, 7, PINK), (560, 110, 14, 2, CREAM),
                            (640, 150, 10, 9, PINK), (720, 100, 15, 5, CREAM), (420, 130, 12, 10, PINK), (600, 170, 13, 1, PINK)])
label = "Bonsai em pixel art que cresce com o histórico do GitHub, balançando ao vento sob um céu estrelado"
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{label}">
<title>{label}</title>
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{NAVY}"/><stop offset=".6" stop-color="{BLUE}"/><stop offset="1" stop-color="{PINK}"/></linearGradient></defs>
<style>
.m{{font-family:'Courier New',ui-monospace,monospace;fill:{CREAM}}}
.tw{{animation:tw 4s ease-in-out infinite}}@keyframes tw{{50%{{opacity:.25}}}}
.sway{{transform-origin:560px 354px;animation:sw 6s ease-in-out infinite alternate}}
@keyframes sw{{from{{transform:rotate(-1.4deg)}}to{{transform:rotate(1.4deg)}}}}
.pt{{animation:pt 12s linear infinite}}
@keyframes pt{{0%{{transform:translate(0,0) rotate(0);opacity:0}}8%{{opacity:.9}}92%{{opacity:.9}}100%{{transform:translate(var(--dx),{H + 20}px) rotate(300deg);opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.tw,.sway,.pt{{animation:none}}.pt{{opacity:0}}}}
</style>
<rect width="{W}" height="{H}" rx="14" fill="url(#sky)"/>
{stars}
<circle cx="860" cy="92" r="40" fill="{CREAM}"/><circle cx="878" cy="80" r="40" fill="{NAVY}" opacity=".0"/>
<text class="m" x="48" y="92" font-size="30" font-weight="900" letter-spacing="3">BONSAI</text>
<text class="m" x="48" y="122" font-size="17" font-weight="700">cresce com o meu</text><text class="m" x="48" y="146" font-size="17" font-weight="700">histórico no GitHub</text>
<g class="sway"><svg x="380" y="20" width="360" height="350" viewBox="{CROP[0]} {CROP[1]} {CROP[2]} {CROP[3]}"><image width="768" height="768" style="image-rendering:pixelated" href="{href}"/></svg></g>
<rect x="318" y="362" width="494" height="18" rx="4" fill="{BLUE}"/><rect x="312" y="356" width="494" height="18" rx="4" fill="{CREAM}" stroke="{BLUE}" stroke-width="2.5"/>
{petals}
</svg>
'''
OUT.write_text(svg)
print("ok", OUT, f"{W}x{H}", len(svg) // 1024, "KB")
