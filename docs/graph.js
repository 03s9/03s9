// Grafo interativo: repos públicos × linguagens (API do GitHub). Arraste os nós; passe o mouse para detalhes.
(() => {
  const cv = document.getElementById('graph'); if (!cv) return;
  const ctx = cv.getContext('2d'), tip = document.getElementById('graph-tip'), msg = document.getElementById('graph-msg');
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const C = { blue: '#0032A8', pink: '#FC3B7F', cream: '#FEF1CF' };
  let W, H, nodes = [], links = [], drag = null, hover = null, alpha = 1;

  function size() {
    const r = cv.getBoundingClientRect(), d = devicePixelRatio || 1;
    W = r.width; H = r.height; cv.width = W * d; cv.height = H * d; ctx.setTransform(d, 0, 0, d, 0, 0);
  }
  size(); addEventListener('resize', () => { size(); alpha = .6; if (reduce) { settle(); draw(); } });

  async function load() {
    const key = 'graph:v1', c = sessionStorage.getItem(key);
    if (c) return JSON.parse(c);
    const repos = (await (await fetch('https://api.github.com/users/03s9/repos?per_page=100')).json())
      .filter(r => !r.fork && r.name !== '03s9');
    const data = [];
    for (const r of repos) {
      const l = await (await fetch(r.languages_url)).json();
      if (Object.keys(l).length) data.push({ name: r.name, url: r.html_url, desc: r.description, langs: l });
    }
    sessionStorage.setItem(key, JSON.stringify(data)); return data;
  }

  function build(data) {
    const langs = {};
    for (const r of data) {
      const tot = Object.values(r.langs).reduce((a, b) => a + b, 0);
      nodes.push({ id: 'r:' + r.name, label: r.name, kind: 'repo', r: 9, url: r.url, info: r.desc || 'Repositório público', x: rnd(W), y: rnd(H), vx: 0, vy: 0 });
      for (const [k, v] of Object.entries(r.langs)) { langs[k] = (langs[k] || 0) + v; links.push({ a: 'r:' + r.name, b: 'l:' + k, w: v / tot }); }
    }
    for (const [k, v] of Object.entries(langs))
      nodes.push({ id: 'l:' + k, label: k, kind: 'lang', r: 13, info: `${(v / 1024).toFixed(1)} KB de código`, x: rnd(W), y: rnd(H), vx: 0, vy: 0 });
    const m = Object.fromEntries(nodes.map(n => [n.id, n]));
    links.forEach(l => { l.A = m[l.a]; l.B = m[l.b]; });
  }
  const rnd = m => m * (.25 + Math.random() * .5);

  function step() {
    for (let i = 0; i < nodes.length; i++) for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j]; let dx = a.x - b.x, dy = a.y - b.y, d2 = dx * dx + dy * dy + .01, d = Math.sqrt(d2);
      const f = 5200 / d2; a.vx += dx / d * f; a.vy += dy / d * f; b.vx -= dx / d * f; b.vy -= dy / d * f;
    }
    for (const l of links) {
      const dx = l.B.x - l.A.x, dy = l.B.y - l.A.y, d = Math.hypot(dx, dy) || 1, f = (d - 110) * .02;
      l.A.vx += dx / d * f; l.A.vy += dy / d * f; l.B.vx -= dx / d * f; l.B.vy -= dy / d * f;
    }
    for (const n of nodes) {
      if (n === drag) { n.vx = n.vy = 0; continue; }
      n.vx += (W / 2 - n.x) * .004; n.vy += (H / 2 - n.y) * .004;
      n.vx *= .85; n.vy *= .85; n.x += n.vx * alpha; n.y += n.vy * alpha;
      n.x = Math.min(W - 30, Math.max(30, n.x)); n.y = Math.min(H - 30, Math.max(30, n.y));
    }
    alpha = Math.max(.02, alpha * .995);
  }
  function settle() { alpha = 1; for (let i = 0; i < 400; i++) step(); }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    for (const l of links) {
      ctx.strokeStyle = 'rgba(254,241,207,.45)'; ctx.lineWidth = 1 + 2.5 * l.w;
      ctx.beginPath(); ctx.moveTo(l.A.x, l.A.y); ctx.lineTo(l.B.x, l.B.y); ctx.stroke();
    }
    ctx.font = '700 12px "Courier New",monospace'; ctx.textAlign = 'center';
    for (const n of nodes) {
      ctx.fillStyle = n.kind === 'lang' ? C.pink : C.blue; ctx.strokeStyle = C.cream; ctx.lineWidth = n === hover ? 4 : 2;
      ctx.beginPath(); ctx.arc(n.x, n.y, n.r + (n === hover ? 3 : 0), 0, 6.28); ctx.fill(); ctx.stroke();
      ctx.fillStyle = C.cream; ctx.fillText(n.label, n.x, n.y + n.r + 16);
    }
  }
  function loop() { if (!reduce) { step(); draw(); requestAnimationFrame(loop); } }

  function at(e) {
    const r = cv.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
    return { x, y, n: nodes.find(n => Math.hypot(n.x - x, n.y - y) <= n.r + 6) };
  }
  cv.addEventListener('pointermove', e => {
    const p = at(e); hover = p.n || null; cv.style.cursor = hover ? (drag ? 'grabbing' : 'grab') : 'default';
    if (drag) { drag.x = p.x; drag.y = p.y; alpha = .5; }
    tip.hidden = !hover; if (hover) { tip.textContent = `${hover.label} — ${hover.info}`; tip.style.left = p.x + 14 + 'px'; tip.style.top = p.y + 14 + 'px'; }
    if (reduce) draw();
  });
  cv.addEventListener('pointerdown', e => { const p = at(e); if (p.n) { drag = p.n; cv.setPointerCapture(e.pointerId); } });
  cv.addEventListener('pointerup', () => { drag = null; });
  cv.addEventListener('dblclick', e => { const p = at(e); if (p.n && p.n.url) open(p.n.url, '_blank', 'noopener'); });

  load().then(d => { build(d); msg.textContent = `${nodes.length} nós · arraste · clique duplo abre o repositório`; if (reduce) { settle(); draw(); } else loop(); })
    .catch(() => { msg.textContent = 'Não foi possível carregar agora (limite da API do GitHub?).'; });
})();
