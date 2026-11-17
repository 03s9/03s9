"""Gera leetcode.svg (card LeetCode, paleta OUTLOUD). Só biblioteca padrão.

Uso: python3 scripts/gen_leetcode.py <leetcode_user> <arquivo_saida>
Fonte: GraphQL público leetcode.com/graphql. Snapshot (não é "ao vivo").
"""
import json, os, sys
from html import escape
from gen_personal import BLUE, CREAM, PINK, NAVY, card, get, wrap

Q = ('query($u:String!){matchedUser(username:$u){profile{ranking}submitStats{acSubmissionNum{difficulty count}}}'
     'allQuestionsCount{difficulty count}}')


def render(user, solved, total, ranking):
    s = solved["All"]
    inner = (f'<text x="44" y="128" class="n" style="font-size:54px">{s}</text>'
             f'<text x="44" y="152" class="l">RESOLVIDOS DE {total["All"]}</text>'
             f'<text x="44" y="176" class="l">RANKING #{ranking:,}</text>').replace(",", ".")
    for i, (k, lab, col) in enumerate([("Easy", "FÁCIL", BLUE), ("Medium", "MÉDIO", PINK), ("Hard", "DIFÍCIL", NAVY)]):
        y = 92 + i * 34
        w = max(4, round(560 * solved[k] / total[k] * 10)) if solved[k] else 0  # escala x10: barra legível
        w = max(4, round(460 * solved[k] / total[k])) if solved[k] else 0  # shortcut: min 4px p/ barra visível
        inner += (f'<text x="340" y="{y}" class="t">{lab}</text>'
                  f'<rect x="440" y="{y-14}" width="460" height="18" rx="4" fill="none" stroke="{BLUE}" stroke-width="2"/>'
                  f'<rect x="440" y="{y-14}" width="{w}" height="18" rx="4" fill="{col}"/>'
                  f'<text x="912" y="{y}" class="t">{solved[k]}/{total[k]}</text>')
    body = card(20, 20, 960, 210, f"LEETCODE · {user}", inner)
    return wrap(250, body, f"LeetCode de {user}: {s} problemas resolvidos de {total['All']}, ranking {ranking}")


def main(user, out):
    d = get("https://leetcode.com/graphql", json.dumps({"query": Q, "variables": {"u": user}}).encode(),
            {"Content-Type": "application/json", "Referer": "https://leetcode.com"})["data"]
    u = d["matchedUser"]
    solved = {x["difficulty"]: x["count"] for x in u["submitStats"]["acSubmissionNum"]}
    total = {x["difficulty"]: x["count"] for x in d["allQuestionsCount"]}
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    open(out, "w", encoding="utf-8").write(render(user, solved, total, u["profile"]["ranking"]))
    print("ok", out, solved)


if __name__ == "__main__":
    main(*sys.argv[1:3])
