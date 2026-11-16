// Terminal interativo: help, whoami, ls, cat gostos, now, contact, clear. Dados ao vivo (GitHub e AniList públicos).
(() => {
  const form = document.getElementById('term-form'); if (!form) return;
  const inp = document.getElementById('term-input'), out = document.getElementById('term-out');
  const hist = []; let hi = 0;
  const line = (t, cls = '') => { const d = document.createElement('div'); d.className = cls; d.textContent = t; out.append(d); out.scrollTop = out.scrollHeight; };
  const ANILIST = `query{User(name:"03s9"){statistics{anime{count episodesWatched minutesWatched}manga{count chaptersRead}}favourites{anime(perPage:5){nodes{title{romaji}}}manga(perPage:5){nodes{title{romaji}}}}}
    a:Page(perPage:5){mediaList(userName:"03s9",status:CURRENT,type:ANIME){progress media{title{romaji}}}}}`;
  const cmds = {
    help: () => ['comandos:', '  whoami        quem sou eu', '  ls            repositórios públicos', '  cat gostos    anime/mangá (AniList)',
      '  now           o que estou assistindo', '  contact       onde me achar', '  clear         limpa a tela'],
    whoami: () => ['Vitor Góngora (03s9)', 'data engineering · backend · AI tooling', 'Python · Rust · SQL · Java · TypeScript'],
    contact: () => ['linkedin: https://www.linkedin.com/in/vitor-g%C3%B3ngora-29243a386', 'github:   https://github.com/03s9'],
    clear: () => { out.textContent = ''; return []; },
    ls: async () => {
      const r = (await (await fetch('https://api.github.com/users/03s9/repos?per_page=100')).json()).filter(x => !x.fork && x.name !== '03s9');
      return r.map(x => `${x.name.padEnd(30)} ${x.language || '—'}`);
    },
    'cat gostos': async () => {
      const d = (await (await fetch('https://graphql.anilist.co', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query: ANILIST }) })).json()).data;
      const s = d.User.statistics, f = d.User.favourites;
      return [`anime: ${s.anime.count} títulos · ${s.anime.episodesWatched} episódios · ${Math.round(s.anime.minutesWatched / 60)} h`,
        `mangá: ${s.manga.count} títulos · ${s.manga.chaptersRead} capítulos`,
        'favoritos: ' + [...f.anime.nodes, ...f.manga.nodes].map(n => n.title.romaji).join(', ')];
    },
    now: async () => {
      const d = (await (await fetch('https://graphql.anilist.co', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ query: ANILIST }) })).json()).data;
      return d.a.mediaList.map(e => `assistindo: ${e.media.title.romaji} (ep ${e.progress})`);
    },
  };
  form.addEventListener('submit', async e => {
    e.preventDefault(); const c = inp.value.trim().toLowerCase(); inp.value = ''; if (!c) return;
    hist.push(c); hi = hist.length; line('$ ' + c, 'cmd');
    const fn = cmds[c];
    if (!fn) return line(`comando não encontrado: ${c} (tente help)`, 'err');
    try { for (const l of await fn()) line(l); } catch { line('erro ao buscar dados (limite da API?)', 'err'); }
  });
  inp.addEventListener('keydown', e => {
    if (e.key === 'ArrowUp' && hi > 0) { inp.value = hist[--hi]; e.preventDefault(); }
    if (e.key === 'ArrowDown' && hi < hist.length) { inp.value = hist[++hi] || ''; e.preventDefault(); }
  });
  line('digite "help" para ver os comandos', 'dim');
})();
