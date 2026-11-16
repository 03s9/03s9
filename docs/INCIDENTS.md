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

## 2026-11-16 — Dashboard 404 (workflow `snake` falhou) e PR #5 fechado sem merge

**Sintoma:** `output/dashboard.svg` -> 404; run `snake` de 01:13 com `failure`.
Os badges animados não apareceram (README ainda com shields.io).

**Causa raiz 1:** o passo `dashboard` rodava DEPOIS do `Platane/snk`, que roda em Docker
como root e cria `dist/` com dono root. O script (usuário `runner`) não podia gravar:
`PermissionError: [Errno 13] Permission denied: 'dist/dashboard.svg'`.
Como o deploy só roda se todos os passos passam, nem snake nem dashboard foram atualizados.

**Causa raiz 2:** o PR #5 (`feat/animated-badges`) foi **fechado sem merge** às 01:11
e a branch remota apagada; o código dos badges nunca entrou na `main`.

**Correção:** `mkdir -p dist` + geração do dashboard ANTES do snk (dir de dono runner;
o container root consegue escrever nele). Badges reenviados em novo PR.

**Verificar:**
```bash
curl -s -o /dev/null -w '%{http_code}\n' https://raw.githubusercontent.com/03s9/03s9/output/dashboard.svg
```

## 2026-11-16 — Fim da dependência da branch `output`

**Por que a `output` não podia ser apagada:** o README apontava para
`raw.githubusercontent.com/03s9/03s9/output/*.svg`. Apagar a branch = 404 nas imagens
(causa do primeiro incidente acima).

**Mudança estrutural:** o workflow `snake.yml` agora gera os SVGs e faz commit direto em
`assets/generated/` na `main` (só quando há diferença). O README usa caminhos relativos
(`assets/generated/*.svg`). A branch `output` deixa de ser usada e pode ser apagada
**depois** que o workflow rodar com sucesso na `main`.

**Trade-off:** o bot cria commits `chore: update generated assets` na `main` (no máximo 1 por dia).
**Risco:** se a `main` for protegida contra push direto, o passo de commit falha.
