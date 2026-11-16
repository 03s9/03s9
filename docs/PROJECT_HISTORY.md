# Perfil 03s9 — Histórico e guia de front-end

Documento do que foi construído no repositório `03s9/03s9` (README de perfil + site em GitHub Pages),
com ênfase no front-end. Serve de base para criar skills reutilizáveis (ver seção 9).

- Perfil: https://github.com/03s9
- Site de teste (Pages): https://03s9.github.io/03s9/
- Autor do perfil: Vitor Góngora. Construído em sessão com Claude Code (Sonnet 5.5, com delegação a Fable e Opus via MCP).

---

## 1. Resumo

| Entrega | Onde | Tecnologia |
|---|---|---|
| Banner OUTLOUD (rosa/creme/azul) com a Hermes | `assets/header.svg` | SVG, imagem PNG embutida (data URI) + filtro SVG |
| Cards bento (Foco / Stack / Agora) | `assets/bento.svg` | SVG |
| Cena "céu estrelado" com 11 badges flutuando | `assets/badges-sky.svg` | SVG + CSS animations, gerado por script |
| Dashboard (linguagens, números, salvos) | `assets/generated/dashboard.svg` | SVG gerado por Python + GitHub Actions |
| Seção pessoal (AniList + Last.fm) | `assets/generated/anilist.svg`, `music.svg` | SVG gerado por `scripts/gen_personal.py` (capas embutidas, capas flutuando, vinil girando) |
| Bonsai pixel art do histórico | `assets/generated/bonsai*.{svg,png,gif}` | action de terceiros `egorthinks/git-bonsai` (fixada por SHA `665258c`), `commit: false` |
| Cena do bonsai (balança, pétalas, lua) | `assets/generated/bonsai-scene.svg` | `scripts/gen_bonsai_scene.py` recorta o PNG do git-bonsai e anima |
| Grafos de dados (repos×linguagens, salvos, gostos) | `assets/generated/graphs.svg` | `scripts/graphkit.py` (layout de forças) + `gen_graphs.py` |
| Constelação da stack (linhas + pulsos) | `assets/badges-sky.svg` | `scripts/gen_sky_badges.py` |
| Grafo interativo (arrastar, hover) | `docs/graph.js` | canvas + API do GitHub, Pages |
| Cobra de contribuições | `assets/generated/snake.svg` | `Platane/snk` + GitHub Actions |
| GIF ASCII | `assets/ascii-loop.gif` | GIF |
| Rodapé xadrez | `assets/footer.svg` | SVG com `<pattern>` |
| Site interativo | `docs/` | HTML + CSS + JS (canvas), sem build |

Linha do tempo (PRs em `03s9/03s9`): #1 design system OUTLOUD · #2 Hermes + GIF · #3 (merge acidental main→branch, sem arquivos) ·
#4 hotfix cobra 404 + doc · #5 badges (fechado sem merge) · #6 dashboard · #7 hotfix workflow · #8 badges (reabertura) ·
#9 assets gerados vão para a `main` · #10 céu de badges · #11 site Pages.

---

## 2. Design system OUTLOUD (tokens)

Fonte: `DESIGN_SYSTEM_PLAN.md` (plano validado). Proporção 60-30-10.

| Token | Hex | Papel |
|---|---|---|
| `brand-pink` | `#FC3B7F` | canvas (≈60%) |
| `brand-cream` | `#FEF1CF` | tipografia grande, superfícies de card/botão (≈30%) |
| `brand-blue` | `#0032A8` | accent: texto sobre creme, bordas, sombras (≈10%) |
| `navy` (extra do céu) | `#061A63` | topo do degradê do céu |

**Regras de contraste (calculadas, WCAG):**
- creme sobre rosa = **3,08:1** → só texto grande (≥ 18,66px bold) ou decorativo.
- azul sobre creme = **9,25:1** (AAA) → texto pequeno e corpo.
- Nunca usar creme em texto pequeno sobre rosa (ex.: a dica "mova o mouse" foi movida para a faixa azul-marinho por isso).

**Tipografia:** pilha monoespaçada segura `'Courier New', ui-monospace, monospace`, peso 800–900 (estilo pixel/Y2K).
Fontes web não carregam dentro de SVG em `<img>`, então não adianta declarar `@font-face` externo.

**Linguagem visual:** cards creme com borda azul 2,5–3px e **sombra deslocada sólida** (retângulo azul atrás, offset 3–8px),
cantos 8–10px, botões retangulares (`rx=4`), título com sublinhado curto azul.

---

## 3. O que o GitHub aceita no README (restrições que moldam o front-end)

| Recurso | Funciona? |
|---|---|
| `<script>`, `<style>`, `style=""`, `<iframe>` | **Não** (removidos pelo sanitizador) |
| JS dentro de SVG em `<img>` | **Não** |
| Hover/clique dentro de SVG em `<img>` | **Não** |
| CSS e SMIL **dentro** do SVG (em `<img>`) | **Sim** — é o que dá animação |
| Fontes externas / imagens externas dentro do SVG | **Não** carregam (data URI sim) |
| `<picture>` + `prefers-color-scheme` | Sim (tema claro/escuro) |
| GIF, WebP animado, `<video>` (upload do GitHub) | Sim |
| `<details>`, Mermaid, tabelas | Sim |
| JS/CSS/hover/canvas de verdade | Só em **GitHub Pages** (site à parte) |

Consequência: o README usa SVG com CSS animations; interatividade real mora no site Pages.

---

## 4. Técnicas de front-end (receitas)

### 4.1 Animação em SVG de README (CSS, respeitando reduced-motion)
```css
.fl{animation:fl 4s ease-in-out infinite}
@keyframes fl{50%{transform:translateY(-6px)}}
@media (prefers-reduced-motion:reduce){.fl{animation:none}}
```
- Efeito pedido para badges: **flutuar suave**, sem brilho nem pulso de cor. Durações e `animation-delay` negativos
  diferentes por badge (`3,6s + (i%4)*0,5s`, delay `-(i*0,7)s`) para não ficarem sincronizados.
- Nuvenzinhas deslizando em `translateX(±7px)` com `alternate`, atrás do badge.

### 4.2 Badge "pílula flutuante"
Pílula creme `rx=19` + retângulo azul deslocado (sombra) + ícone do **simple-icons (CC0)** escalado (`scale(1.0833)` num viewBox 24)
+ texto mono 14px/900. Largura = `20+26+10+len(label)*8,6+20+8`.

### 4.3 Embutir PNG no SVG e remover fundo branco
O PNG da Hermes tinha fundo branco **opaco**. Solução: embutir como data URI e aplicar um filtro que transforma luminância em alfa
e recolore para o azul da marca:
```xml
<filter id="knock" x="0" y="0" width="1" height="1" color-interpolation-filters="sRGB">
  <feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0.196  0 0 0 0 0.659  -1 0 0 0 1"/>
</filter>
<image filter="url(#knock)" x="684" y="30" width="291" height="360" href="data:image/png;base64,..."/>
```
Armadilha: sem `x=0 y=0 width=1 height=1` a região do filtro estoura 10% e pinta um **quadro azul** em volta.
No site Pages o equivalente simples é `mix-blend-mode: multiply` (deixa a imagem mais escura).

### 4.4 Tema claro/escuro no README
```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/x-dark.svg">
  <img alt="..." src="assets/x-light.svg" width="100%">
</picture>
```
Depois a paleta OUTLOUD passou a ser **única** (sem variantes), então os `<picture>` foram removidos.

### 4.5 Cena composta: céu + badges num único SVG
Pedido: "pássaros, estrelas cadentes e céu estrelado atrás das badges". Como o README não aceita CSS de fundo atrás de `<img>`,
a solução é **um SVG só** (1000×260) com tudo dentro (`scripts/gen_sky_badges.py`):
- Degradê vertical `navy → blue → pink`.
- 70 estrelas (círculos cream) com `opacity` variando (twinkle), posições determinísticas (`random.Random(7)`).
- 3 estrelas cadentes: grupo com linha de cauda em degradê, animado por `translate` com `--x/--y` e `opacity` (11–13 s, atrasos diferentes).
- 5 pássaros: caminho `M-9 0Q-4.5 -6 0 0Q4.5 -6 9 0`, voo horizontal lento (40–52 s) + bater de asa com `scaleY(1 → -0.6)`.
- Badges empilhados em linhas (empacotamento guloso, largura útil 920px, gap 14), centralizados por linha.
- **Armadilha de CSS inline:** ao juntar vários badges num SVG, as classes/keyframes colidem. Solução: keyframes únicos
  e **durações/atrasos por `style` inline** em cada grupo.
- Alt text lista a stack inteira (`aria-label` + `<title>`).

### 4.6 Banner e cards bento
- Camadas (do plano): canvas rosa → texto gigante `03S9` creme (150px/900) → ponto focal (Hermes sobre círculo creme `r=140`) → título/CTA.
- Botão "EXPLORAR REPOSITÓRIOS" no SVG **não é clicável**; o banner inteiro vai dentro de `<a href=...>` no README.
- Cards bento: 3 cards (FOCO, STACK, AGORA), texto azul ≥ 15px.
- Rodapé: `<pattern>` 60×30 com quadradinhos creme/azul sobre rosa, `aria-hidden`.

### 4.7 Dashboard gerado (SVG por script)
`scripts/gen_dashboard.py` (somente biblioteca padrão) consulta a API do GitHub e desenha 3 cards:
LINGUAGENS (bytes por linguagem dos repos **públicos, não-fork**), NÚMEROS (repos, estrelas, seguidores, contribuições 12m via GraphQL),
SALVOS (últimos 5 repos de terceiros com estrela, ignorando privados). Escapa XML com `html.escape`.
Sem serviço externo (o `github-readme-stats` público deu 503 e mostrava só um ícone de interrogação).

### 4.8 Site GitHub Pages (JS/CSS reais)
`docs/index.html`, `style.css`, `main.js` — estático, sem build (decisão YAGNI para um teste).
- Hero OUTLOUD responsivo (`clamp()` no texto gigante), Hermes com `mix-blend-mode:multiply`.
- **Céu em `<canvas>`**: estrelas piscam (seno) e **fogem do cursor** (repulsão a 90px, retornam com easing),
  estrelas cadentes aleatórias, pássaros com batida de asa; DPR-aware; `resize` recalcula.
- Badges DOM com `bob` + hover (`scale(1.12) rotate(-3deg)`).
- Repos públicos **ao vivo** via `fetch('https://api.github.com/users/03s9/repos')` (sem token: 60 req/h por IP; erro tratado).
- `prefers-reduced-motion`: desliga animações CSS e o JS não anima estrelas cadentes/pássaros.
- Foco visível (`:focus-visible`), `role="status"` no carregamento, alt em imagens.
- Publicação: Pages com origem `main` pasta `/docs` (+ `.nojekyll`).

---

## 5. Pipeline de assets gerados

`.github/workflows/snake.yml` (diário 03:00 UTC, em push que altera o próprio workflow e manual):
1. `actions/checkout@v4`
2. gera `dist/dashboard.svg` (**antes** do snk — ver armadilhas)
3. `Platane/snk@v3.5.0` gera `dist/snake.svg`
4. copia `dist/*.svg` para `assets/generated/` e faz commit/push do bot na `main` se houver diferença.

O README referencia caminhos **relativos** (`assets/generated/*.svg`). Antes disso, as imagens vinham da branch `output`
(deploy com `crazy-max/ghaction-github-pages`), o que causou o incidente 1.

---

## 6. Incidentes e lições (resumo; detalhes em `docs/INCIDENTS.md`)

| # | Sintoma | Causa | Correção / lição |
|---|---|---|---|
| 1 | Cobra com 404 | Branch `output` deletada na limpeza de branches | Assets gerados passaram para a `main` |
| 2 | Workflow `snake` vermelho, dashboard 404 | `snk` (Docker, root) criou `dist/` com dono root → `PermissionError` | Gerar o dashboard antes do snk |
| 3 | Badges não apareciam | PR #5 fechado sem merge e branch apagada | Reabrir (#8) |
| 4 | Run manual falhou: `rejected (fetch first)` | Dois runs simultâneos fizeram push na `main` | `concurrency` + `git pull --rebase` antes do push (feat/personal-section) |
| 5 | Quadro azul em volta da Hermes | Região padrão do filtro SVG (+10%) | `x=0 y=0 width=1 height=1` |
| 6 | Fundo branco da Hermes | PNG opaco | Filtro de luminância → alfa |
| 7 | Cards de stats com "?" | `github-readme-stats` público com 503 | Dashboard próprio |

---

## 7. Como verificar front-end sem navegador manual

- **Chrome headless** (confiável; o Quick Look corta SVGs largos e não aplica filtros como o navegador):
  ```bash
  "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu --hide-scrollbars \
    --window-size=1000,400 --screenshot=/tmp/x.png "file:///caminho/arquivo.svg"
  ```
- Validar XML: `python3 -I -c "import xml.dom.minidom as m;m.parse('arquivo.svg')"`.
- Contraste: calcular luminância relativa (WCAG) em Python; conferidos 3,08:1 e 9,25:1.
- **Limite:** screenshot não avança animação (dois tempos deram a mesma imagem) nem simula mouse. Movimento e hover só se confirmam abrindo no navegador.

---

## 8. Estrutura final do repositório

```
.github/workflows/snake.yml     # gera dashboard + cobra, commit do bot
assets/
  header.svg bento.svg footer.svg ascii-loop.gif
  badges/*.svg                  # fonte dos 11 badges individuais
  badges-sky.svg                # cena composta (gerada)
  generated/                    # gerado pelo workflow (snake, dashboard)
docs/
  index.html style.css main.js hermes.png .nojekyll   # site Pages
  INCIDENTS.md PROJECT_HISTORY.md
scripts/gen_dashboard.py gen_sky_badges.py gen_personal.py graphkit.py gen_graphs.py gen_bonsai_scene.py
README.md
```
Observação: o `docs/` é também a raiz publicada pelo Pages (`INCIDENTS.md` fica acessível como texto).

---

## 9. Candidatas a skills (para criar depois)

1. **`github-readme-svg`** — restrições do sanitizador, o que funciona em `<img>`, estrutura de assets, `<picture>` claro/escuro, alt text. (Seção 3.)
2. **`readme-svg-animation`** — receitas CSS/SMIL: flutuar, twinkle, estrela cadente, pássaro; delays escalonados; `prefers-reduced-motion`; armadilhas de keyframes colidindo. (4.1, 4.5.)
3. **`brand-tokens-to-svg`** — transformar um design system (tokens + regras de contraste) em SVGs: cards com sombra sólida, botão, banner em camadas, cálculo de contraste. (2, 4.6.)
4. **`svg-scene-generator`** — gerar cenas SVG por script Python determinístico (empacotamento de itens, estrelas por seed, composição de partes). (4.5.)
5. **`svg-image-embed-knockout`** — embutir PNG (data URI), remover fundo por `feColorMatrix`, recolorir, evitar o quadro do filtro. (4.3.)
6. **`github-generated-assets-workflow`** — Actions que gera SVG e comita na `main` (bot), armadilha do Docker root, corrida de push, alternativa à branch de assets. (5, 6.)
7. **`github-pages-static-site`** — site `docs/` sem build, canvas interativo, fetch da API do GitHub, ligar Pages por API, `.nojekyll`. (4.8.)
8. **`headless-visual-check`** — protocolo de verificação por screenshot no Chrome headless e seus limites. (7.)

Cada skill deve incluir: gatilhos de uso, o exemplo mínimo funcional deste repositório, checklist de verificação e as armadilhas da seção 6.

---

## 10. Fora do que foi feito / não verificado

- Hover e interação do site (screenshot não simula).
- Movimento das animações do README renderizado no GitHub.
- Layout em celular.
- Opção A completa do plano (landing em React/Vite/Tailwind): trocada por um site estático de teste.
- Conteúdo de "foco / stack / agora" a partir do LinkedIn: leitura bloqueada (HTTP 999); textos atuais são suposições.
- Remoção da branch `output` (sem uso) ainda pendente.
- Seção pessoal: o Last.fm só foi testado com dados de mentira (sem chave local); a primeira prova real é o run do workflow.

### Nota: action de terceiros (git-bonsai)
Revisada em 2026-11-16 na versão `665258c` (v1.0.0): única rede é `api.github.com/graphql` com o token; `execSync` só roda `git`;
sem `eval`/download. Fixada por SHA (não `@v1`). Roda com `commit: "false"` porque o `git push` dela só faz retry, sem `pull --rebase`;
quem publica é o nosso passo de commit. Falha dela não bloqueia o resto (`continue-on-error`). Para atualizar a versão: reler o `dist/src/action.js` e trocar o SHA.

### Backup do README
Antes dos grafos e da cena do bonsai: tag git `readme-backup-2026-11-16` e cópia local em `/Users/03s9/03s9-profile-backups/`.
Para voltar: `git checkout readme-backup-2026-11-16 -- README.md` (ou copiar o arquivo do backup).
