"""Gera assets/bento-mobile.svg (600px) com o mesmo conteúdo do bento.svg em coluna única."""
import pathlib
from html import escape
B, C, P = "#0032A8", "#FEF1CF", "#FC3B7F"
cards = [("FOCO", ["Pipelines de dados e extração", "de documentos", "Motores nativos em Rust", "Agentes de IA e LLMs locais"]),
         ("STACK", ["Python · SQL · Polars · DuckDB", "Rust · Java · TypeScript", "FastAPI · Pydantic · Docker"]),
         ("AGORA", ["Explorando motores de dados nativos", "e mineração de papers do arXiv.", "Aberto a conversar sobre dados,", "backend e automação com IA."])]
y, body = 20, ""
for title, lines in cards:
    h = 74 + len(lines) * 28
    body += (f'<rect x="28" y="{y+8}" width="552" height="{h}" rx="8" fill="{B}"/>'
             f'<rect x="20" y="{y}" width="552" height="{h}" rx="8" fill="{C}" stroke="{B}" stroke-width="3"/>'
             f'<text x="44" y="{y+40}" class="h">{title}</text><rect x="44" y="{y+52}" width="48" height="4" fill="{B}"/>')
    body += "".join(f'<text x="44" y="{y+88+i*28}" class="t">&gt; {escape(l)}</text>' for i, l in enumerate(lines))
    y += h + 24
H = y
svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="600" height="{H}" viewBox="0 0 600 {H}" role="img" aria-label="Foco, stack e agora">'
       f'<title>Foco, stack e agora</title><style>.h{{font:900 26px \'Courier New\',ui-monospace,monospace;fill:{B};letter-spacing:2px}}'
       f'.t{{font:700 17px \'Courier New\',ui-monospace,monospace;fill:{B}}}</style><rect width="600" height="{H}" rx="12" fill="{P}"/>{body}</svg>\n')
(pathlib.Path(__file__).resolve().parent.parent / "assets/bento-mobile.svg").write_text(svg)
print("ok bento-mobile", H)
