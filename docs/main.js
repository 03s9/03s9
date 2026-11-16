// Céu interativo (canvas) + repositórios públicos via API do GitHub.
(() => {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const cv = document.getElementById('sky'), ctx = cv.getContext('2d');
  let w, h, stars = [], shoot = [], birds = [], mouse = { x: -999, y: -999 };
  const rnd = (a, b) => a + Math.random() * (b - a);

  function resize() {
    const r = cv.getBoundingClientRect(), d = devicePixelRatio || 1;
    w = r.width; h = r.height; cv.width = w * d; cv.height = h * d; ctx.setTransform(d, 0, 0, d, 0, 0);
    stars = Array.from({ length: Math.round(w * h / 9000) }, () => {
      const x = rnd(0, w), y = rnd(0, h * .8);
      return { x, y, ox: x, oy: y, r: rnd(.6, 2), p: rnd(0, 6.28) };
    });
    birds = Array.from({ length: 5 }, (_, i) => ({ x: rnd(0, w), y: rnd(20, h * .45), v: rnd(.25, .6), s: rnd(.8, 1.3), p: i }));
  }
  addEventListener('resize', resize); resize();
  cv.parentElement.addEventListener('pointermove', e => {
    const r = cv.getBoundingClientRect(); mouse.x = e.clientX - r.left; mouse.y = e.clientY - r.top;
  });
  cv.parentElement.addEventListener('pointerleave', () => { mouse.x = mouse.y = -999; });

  function frame(t) {
    ctx.clearRect(0, 0, w, h);
    ctx.fillStyle = '#FEF1CF';
    for (const s of stars) {
      const dx = s.x - mouse.x, dy = s.y - mouse.y, d = Math.hypot(dx, dy);
      if (d < 90 && !reduce) { s.x += dx / d * 2.2; s.y += dy / d * 2.2; }
      s.x += (s.ox - s.x) * .04; s.y += (s.oy - s.y) * .04;
      ctx.globalAlpha = reduce ? .9 : .55 + .45 * Math.sin(t / 700 + s.p);
      ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, 6.28); ctx.fill();
    }
    ctx.globalAlpha = 1;
    if (!reduce) {
      if (Math.random() < .004) shoot.push({ x: rnd(0, w * .7), y: rnd(0, h * .3), life: 1 });
      for (const m of shoot) {
        ctx.strokeStyle = `rgba(254,241,207,${m.life})`; ctx.lineWidth = 2.5; ctx.lineCap = 'round';
        ctx.beginPath(); ctx.moveTo(m.x, m.y); ctx.lineTo(m.x - 70, m.y - 28); ctx.stroke();
        m.x += 9; m.y += 3.6; m.life -= .018;
      }
      shoot = shoot.filter(m => m.life > 0);
      ctx.strokeStyle = '#FEF1CF'; ctx.lineWidth = 2; ctx.lineCap = 'round';
      for (const b of birds) {
        b.x += b.v; if (b.x > w + 20) b.x = -20;
        const f = Math.sin(t / 140 + b.p * 2) * 6 * b.s;
        ctx.beginPath(); ctx.moveTo(b.x - 9 * b.s, b.y); ctx.quadraticCurveTo(b.x - 4.5 * b.s, b.y - f, b.x, b.y);
        ctx.quadraticCurveTo(b.x + 4.5 * b.s, b.y - f, b.x + 9 * b.s, b.y); ctx.stroke();
      }
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  // Repos públicos (dados ao vivo)
  const box = document.getElementById('repos'), st = document.getElementById('status');
  fetch('https://api.github.com/users/03s9/repos?per_page=100&sort=updated')
    .then(r => { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(list => {
      const repos = list.filter(r => !r.fork && r.name !== '03s9');
      st.textContent = `${repos.length} repositórios`;
      for (const r of repos) {
        const a = document.createElement('a'); a.className = 'card'; a.href = r.html_url;
        const h3 = document.createElement('h3'); h3.textContent = r.name;
        const p = document.createElement('p'); p.textContent = r.description || 'Sem descrição';
        const s = document.createElement('small'); s.textContent = r.language || '—';
        a.append(h3, p, s); box.append(a);
      }
    })
    .catch(() => { st.textContent = 'Não foi possível carregar agora (limite da API do GitHub?).'; });
})();
