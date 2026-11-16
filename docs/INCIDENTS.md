# Incidentes

## 2026-11-16 — Cobra de contribuições quebrada (404)

**Sintoma:** a seção "Atividade" do perfil mostrava só o alt text
("Cobra percorrendo e comendo o gráfico...") em vez da animação.

**Causa raiz:** a branch `output`, onde o workflow `snake.yml` publica
`snake.svg` e `snake-dark.svg`, foi deletada às 00:22:57 (junto com as
branches `feat/ascii-butterfly` e `feat/outloud-design-system`, já mergeadas).
O README referencia `raw.githubusercontent.com/03s9/03s9/output/snake.svg`;
sem a branch, a URL responde 404.
Evidência: `gh api repos/03s9/03s9/activity` -> `branch_deletion refs/heads/output`.

**O que NÃO foi a causa:** o workflow estava correto (run de 15/11 23:18 passou
e criou a branch); o banner/Hermes e o GIF carregam normalmente (200).

**Correção imediata:** `gh workflow run snake.yml` recriou a branch `output`.
`snake.svg` e `snake-dark.svg` voltaram a responder 200.

**Prevenção (este hotfix):**
- `snake.yml` agora também roda em push na `main` que altera o próprio workflow.
- Regra: **não apague a branch `output`** ao limpar branches mergeadas.
  Ela é gerada pelo bot e é necessária para a cobra.
- Se for apagada de novo: Actions > snake > Run workflow.

**Não resolvido:** o workflow ainda não regenera a cobra se a branch for
deletada fora de um push/cron; o cron diário (03:00 UTC) a recria em até 24h.

**Verificar:**
```bash
curl -s -o /dev/null -w '%{http_code}\n' https://raw.githubusercontent.com/03s9/03s9/output/snake.svg
```
