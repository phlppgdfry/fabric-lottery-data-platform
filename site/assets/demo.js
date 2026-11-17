// Three real runs of local/pipeline.py on 100,000 generated transactions, at 0%, 1% and 5% injected faults.
const $ = id => document.getElementById(id);
const runs = await (await fetch('assets/runs.json')).json();
const nf = n => Number(n).toLocaleString('en');
const REASONS = { duplicate_delivery: 'Duplicate delivery', missing_or_bad_timestamp: 'Missing or bad timestamp', non_positive_or_missing_amount: 'Amount missing, zero or negative', unknown_player: 'Unknown player key', unknown_game: 'Unknown game key', retail_without_known_location: 'Retail sale without known location' };

function render(rate) {
  const r = runs[rate], l = r.layers;
  document.querySelectorAll('#fb-rates button').forEach(b => b.setAttribute('aria-selected', b.dataset.r === rate));
  const box = (name, n, sub, cls = '') => `<div class="fb-layer ${cls}"><div class="fb-ln">${name}</div><div class="fb-n">${nf(n)}</div><div class="small dim">${sub}</div></div>`;
  const arrow = '<div class="fb-ar">→</div>';
  $('fb-med').innerHTML = box('Bronze', l.bronze_transactions, 'raw text + _ingested_at, _source', 'b') + arrow +
    box('Silver', l.silver_transactions, `typed, deduplicated · <b class="${l.rejected ? 'fb-bad' : ''}">${nf(l.rejected)} rejected</b>`, 's') + arrow +
    box('Gold', l.gold_fact_rows, `fact rows · ${r.orphan_fact_keys} orphan keys`, 'g');
  const max = Math.max(1, ...r.rejects_by_reason.map(x => x.rows));
  $('fb-rej').innerHTML = r.rejects_by_reason.length ? r.rejects_by_reason.map(x => `<div class="fb-bar"><span>${REASONS[x.reason] || x.reason}</span><i style="width:${x.rows / max * 100}%"></i><b class="mono">${nf(x.rows)}</b></div>`).join('')
    : '<p class="small dim">Clean input: nothing rejected. Bronze and Silver hold the same rows.</p>';
  $('fb-warn').innerHTML = `<span class="pill warn">review</span> ${nf(r.warnings.sale_on_inactive_game)} sales on games that are inactive <em>today</em>. The game dimension has no retirement date, so these cannot be judged yet: a slowly changing dimension is the fix. · <span class="pill ok">✓</span> ${nf(r.warnings.purchase_before_signup)} purchases before signup`;
  const d = r.dimensions, f = l.gold_fact_rows;
  const node = (x, y, t, n, fact) => `<g><rect x="${x - 70}" y="${y - 24}" width="140" height="48" rx="10" class="${fact ? 'fact' : 'dim'}"/><text x="${x}" y="${y - 4}" text-anchor="middle" class="t">${t}</text><text x="${x}" y="${y + 14}" text-anchor="middle" class="n">${nf(n)} rows</text></g>`;
  const line = (x, y) => `<line x1="230" y1="130" x2="${x}" y2="${y}" class="ln"/>`;
  $('fb-star').innerHTML = line(85, 45) + line(375, 45) + line(85, 215) + line(375, 215) +
    node(85, 45, 'dim_player', d.dim_player) + node(375, 45, 'dim_game', d.dim_game) + node(85, 215, 'dim_location', d.dim_location) + node(375, 215, 'dim_date', d.dim_date) + node(230, 130, 'fact_transaction', f, true);
  const m = r.monthly_revenue, W = 560, H = 190, mx = Math.max(...m.map(x => x.revenue)), bw = (W - 20) / m.length;
  $('fb-month').setAttribute('viewBox', `0 0 ${W} ${H}`);
  $('fb-month').innerHTML = m.map((x, i) => { const h = x.revenue / mx * (H - 40); return `<rect x="${10 + i * bw + 2}" y="${H - 22 - h}" width="${bw - 4}" height="${h}" rx="2" class="mb"><title>${x.month}: €${nf(Math.round(x.revenue))}</title></rect>${i % 3 === 0 ? `<text x="${10 + i * bw}" y="${H - 6}" class="ax">${x.month}</text>` : ''}`; }).join('');
  $('fb-games').innerHTML = '<tr><th>Game</th><th>Type</th><th class="num">Tickets</th><th class="num">Revenue</th><th class="num">Players</th></tr>' +
    r.top_games.map(g => `<tr><td>${g.game_name}${g.active ? '' : ' <span class="pill warn">inactive</span>'}</td><td>${g.game_type.replace('_', ' ')}</td><td class="num">${nf(g.tickets)}</td><td class="num">€${nf(Math.round(g.revenue))}</td><td class="num">${nf(g.players)}</td></tr>`).join('');
}
$('fb-rates').innerHTML = Object.keys(runs).map(r => `<button type="button" data-r="${r}">${r === '0' ? 'none' : (+r * 100) + '%'}</button>`).join('');
$('fb-rates').addEventListener('click', e => e.target.dataset.r && render(e.target.dataset.r));
render('0.01');
