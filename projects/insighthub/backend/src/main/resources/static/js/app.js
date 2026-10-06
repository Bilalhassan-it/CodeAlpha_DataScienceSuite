const API = location.port === '8080' ? '' : 'http://localhost:8080';
const $ = s => document.querySelector(s);
const fmt = n => Number(n).toLocaleString(undefined, { maximumFractionDigits: 0 });
const money = n => '$' + fmt(n);
const PAL = ['#0F3460', '#818CF8', '#38BDF8', '#34D399', '#FBBF24', '#F87171', '#A78BFA', '#FB923C'];
const TITLES = {
  overview: ['Executive Overview', 'Revenue, profitability and demand signals across all regions'],
  explorer: ['Sales Explorer', 'Slice and search individual orders'],
  forecast: ['Forecast Lab', 'Trend + seasonality model powered by the Python analytics service'],
  sql: ['SQL Studio', 'Ad-hoc read-only analysis on the live database']
};
let days = 90, page = 0, pages = 1, view = 'overview', charts = {}, loaded = {};

async function api(path, opt) {
  const r = await fetch(API + path, opt);
  const d = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(d.error || r.statusText);
  return d;
}
function toast(m) { const t = $('#toast'); t.textContent = m; t.classList.add('show'); setTimeout(() => t.classList.remove('show'), 3200); }
function draw(id, cfg) {
  if (charts[id]) charts[id].destroy();
  cfg.options = { responsive: true, maintainAspectRatio: false, ...(cfg.options || {}) };
  charts[id] = new Chart($('#' + id), cfg);
}
const esc = s => String(s ?? '').replace(/[&<>]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c]));

/* ---------- status ---------- */
async function checkStatus() {
  try {
    const h = await api('/api/health');
    $('#statusDot').className = 'dot ok'; $('#statusText').textContent = 'Backend online';
    $('#statusMeta').textContent = fmt(h.rows) + ' rows indexed';
  } catch { $('#statusDot').className = 'dot bad'; $('#statusText').textContent = 'Backend offline'; }
}

/* ---------- overview ---------- */
async function loadOverview() {
  try {
    const d = await api('/api/dashboard/overview?days=' + days);
    const k = d.kpis, p = d.prev;
    const defs = [['Revenue', 'revenue', money], ['Profit', 'profit', money], ['Orders', 'orders', fmt], ['Avg Order Value', 'aov', money], ['Customers', 'customers', fmt]];
    $('#kpiGrid').innerHTML = defs.map(([l, key, f]) => {
      const g = p[key] ? (k[key] - p[key]) / p[key] * 100 : 0;
      return `<div class="kpi"><span>${l}</span><strong>${f(k[key])}</strong><em class="${g >= 0 ? 'up' : 'down'}">${g >= 0 ? '▲' : '▼'} ${Math.abs(g).toFixed(1)}% vs prev</em></div>`;
    }).join('');
    $('#trendSub').textContent = 'Monthly performance · last ' + days + ' days';
    draw('trendChart', { type: 'line', data: { labels: d.trend.map(x => x.period), datasets: [
      { label: 'Revenue', data: d.trend.map(x => x.revenue), borderColor: '#0F3460', backgroundColor: 'rgba(15,52,96,.08)', fill: true, tension: .35 },
      { label: 'Profit', data: d.trend.map(x => x.profit), borderColor: '#818CF8', tension: .35 }] }, options: { plugins: { legend: { display: false } } } });
    const dn = (id, arr) => draw(id, { type: 'doughnut', data: { labels: arr.map(x => x.label), datasets: [{ data: arr.map(x => x.amount), backgroundColor: PAL }] }, options: { plugins: { legend: { position: 'bottom', labels: { boxWidth: 10 } } } } });
    dn('categoryChart', d.category); dn('channelChart', d.channel);
    draw('regionChart', { type: 'bar', data: { labels: d.region.map(x => x.label), datasets: [{ data: d.region.map(x => x.amount), backgroundColor: '#0F3460', borderRadius: 6 }] }, options: { plugins: { legend: { display: false } } } });
    draw('productChart', { type: 'bar', data: { labels: d.product.map(x => x.label), datasets: [{ data: d.product.map(x => x.amount), backgroundColor: '#818CF8', borderRadius: 6 }] }, options: { indexAxis: 'y', plugins: { legend: { display: false } } } });
    $('#segmentTable tbody').innerHTML = d.segments.map(s => {
      const lvl = s.risk > .55 ? ['High', 'b-high'] : s.risk > .45 ? ['Medium', 'b-med'] : ['Low', 'b-low'];
      return `<tr><td>${esc(s.segment)}</td><td class="num">${money(s.revenue)}</td><td class="num">${fmt(s.customers)}</td><td class="num">${(s.risk * 100).toFixed(0)}%</td><td><span class="bar"><i style="width:${s.risk * 100}%"></i></span><span class="badge ${lvl[1]}">${lvl[0]}</span></td></tr>`;
    }).join('');
  } catch (e) { toast('Overview failed: ' + e.message); }
}

/* ---------- explorer ---------- */
async function loadFilters() {
  const f = await api('/api/sales/filters');
  const fill = (id, arr) => $(id).insertAdjacentHTML('beforeend', arr.map(v => `<option>${esc(v)}</option>`).join(''));
  fill('#fRegion', f.regions); fill('#fCategory', f.categories); fill('#fChannel', f.channels);
}
async function loadOrders() {
  const qs = new URLSearchParams({ region: $('#fRegion').value, category: $('#fCategory').value, channel: $('#fChannel').value, q: $('#fSearch').value, page, size: 15 });
  try {
    const d = await api('/api/sales?' + qs);
    pages = d.pages || 1;
    $('#orderCount').textContent = fmt(d.total) + ' records';
    $('#ordersTable tbody').innerHTML = d.items.map(o => `<tr><td>${o.orderId}</td><td>${o.orderDate}</td><td>${o.region}</td><td>${o.country}</td><td>${o.category}</td><td>${o.product}</td><td>${o.channel}</td><td class="num">${o.units}</td><td class="num">${money(o.revenue)}</td><td class="num">${money(o.profit)}</td></tr>`).join('');
    $('#pageInfo').textContent = `Page ${page + 1} of ${pages}`;
    $('#prevPage').disabled = page === 0; $('#nextPage').disabled = page + 1 >= pages;
  } catch (e) { toast(e.message); }
}

/* ---------- forecast ---------- */
async function runForecast() {
  const btn = $('#runForecast'); btn.disabled = true; btn.textContent = 'Running…';
  try {
    const n = +$('#forecastPeriods').value, d = await api('/api/forecast?periods=' + n);
    const hl = d.history.map(h => h.period), fl = d.forecast.map(f => f.period), pad = arr => hl.map(() => null).concat(arr);
    const last = d.history[d.history.length - 1];
    const connect = (v) => hl.map((_, i) => i === hl.length - 1 ? v : null);
    draw('forecastChart', { type: 'line', data: { labels: hl.concat(fl), datasets: [
      { label: 'Actual', data: d.history.map(h => h.actual).concat(fl.map(() => null)), borderColor: '#0F3460', tension: .3 },
      { label: 'Fitted', data: d.history.map(h => h.fitted).concat(fl.map(() => null)), borderColor: '#94A3B8', borderDash: [4, 4], pointRadius: 0, tension: .3 },
      { label: 'Forecast', data: connect(last.actual).concat(d.forecast.map(f => f.value)), borderColor: '#818CF8', borderWidth: 3, tension: .3 },
      { label: 'Upper', data: pad(d.forecast.map(f => f.upper)), borderColor: 'transparent', backgroundColor: 'rgba(129,140,248,.18)', pointRadius: 0, fill: '+1' },
      { label: 'Lower', data: pad(d.forecast.map(f => f.lower)), borderColor: 'transparent', pointRadius: 0 }] },
      options: { plugins: { legend: { labels: { filter: i => !['Upper', 'Lower'].includes(i.text), boxWidth: 12 } } } } });
    const m = d.metrics;
    $('#modelMetrics').innerHTML = [['Engine', m.engine], ['R²', m.r2.toFixed(3)], ['MAPE', m.mape.toFixed(1) + '%'], ['RMSE', money(m.rmse)], ['Trend / month', money(m.slope)], ['Horizon', n + ' months']].map(([a, b]) => `<div class="metric"><span>${a}</span><strong>${b}</strong></div>`).join('');
    $('#anomalyTable tbody').innerHTML = d.anomalies.length ? d.anomalies.map(a => `<tr><td>${a.period}</td><td class="num">${money(a.actual)}</td><td class="num">${money(a.expected)}</td><td class="num ${a.deviation >= 0 ? 'up' : 'down'}">${a.deviation >= 0 ? '+' : ''}${money(a.deviation)}</td><td><span class="badge ${Math.abs(a.z) > 3 ? 'b-high' : 'b-med'}">${a.z.toFixed(2)}σ</span></td></tr>`).join('') : '<tr><td colspan="5">No anomalies detected 🎉</td></tr>';
  } catch (e) { toast(e.message); }
  btn.disabled = false; btn.textContent = 'Run model';
}

/* ---------- SQL studio ---------- */
const SNIPPETS = {
  'Revenue by region': 'SELECT region, ROUND(SUM(revenue),2) AS revenue\nFROM sales_records\nGROUP BY region\nORDER BY revenue DESC;',
  'Top 10 products': 'SELECT product, SUM(units) AS units, ROUND(SUM(revenue),2) AS revenue\nFROM sales_records\nGROUP BY product\nORDER BY revenue DESC\nLIMIT 10;',
  'Monthly profit margin': "SELECT FORMATDATETIME(order_date,'yyyy-MM') AS month,\n       ROUND(SUM(profit)/SUM(revenue)*100,1) AS margin_pct\nFROM sales_records\nGROUP BY month\nORDER BY month;",
  'High churn customers': 'SELECT name, segment, churn_risk\nFROM customers\nWHERE churn_risk > 0.8\nORDER BY churn_risk DESC\nLIMIT 20;',
  'Channel x Category': 'SELECT channel, category, ROUND(SUM(revenue),2) AS revenue\nFROM sales_records\nGROUP BY channel, category\nORDER BY channel, revenue DESC;'
};
async function runSql() {
  try {
    const d = await api('/api/query', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ sql: $('#sqlInput').value }) });
    $('#sqlTable thead').innerHTML = '<tr>' + d.columns.map(c => `<th>${esc(c)}</th>`).join('') + '</tr>';
    $('#sqlTable tbody').innerHTML = d.rows.map(r => '<tr>' + r.map(v => `<td>${esc(v)}</td>`).join('') + '</tr>').join('');
    $('#sqlMeta').textContent = `${d.rows.length} rows · ${d.ms} ms`;
  } catch (e) { toast(e.message); $('#sqlMeta').textContent = 'Error: ' + e.message; }
}

/* ---------- navigation & wiring ---------- */
function show(v) {
  view = v;
  document.querySelectorAll('.nav-item').forEach(b => b.classList.toggle('active', b.dataset.view === v));
  document.querySelectorAll('.view').forEach(s => s.classList.toggle('active', s.id === 'view-' + v));
  $('#pageTitle').textContent = TITLES[v][0]; $('#pageSub').textContent = TITLES[v][1];
  if (loaded[v]) return; loaded[v] = true;
  if (v === 'explorer') loadFilters().then(loadOrders); else if (v === 'forecast') runForecast(); else if (v === 'sql') runSql();
}
document.querySelectorAll('.nav-item').forEach(b => b.onclick = () => show(b.dataset.view));
document.querySelectorAll('.range-btn').forEach(b => b.onclick = () => {
  document.querySelectorAll('.range-btn').forEach(x => x.classList.toggle('active', x === b));
  days = +b.dataset.days; loadOverview();
});
$('#refreshBtn').onclick = () => { checkStatus(); loadOverview(); if (view === 'explorer') loadOrders(); if (view === 'forecast') runForecast(); };
$('#applyFilters').onclick = () => { page = 0; loadOrders(); };
$('#fSearch').onkeydown = e => { if (e.key === 'Enter') { page = 0; loadOrders(); } };
$('#clearFilters').onclick = () => { ['#fRegion', '#fCategory', '#fChannel', '#fSearch'].forEach(s => $(s).value = ''); page = 0; loadOrders(); };
$('#prevPage').onclick = () => { page--; loadOrders(); };
$('#nextPage').onclick = () => { page++; loadOrders(); };
$('#runForecast').onclick = runForecast;
$('#runSql').onclick = runSql;
$('#sqlInput').onkeydown = e => { if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') runSql(); };
$('#snippetList').innerHTML = Object.keys(SNIPPETS).map(k => `<button class="snippet">${k}</button>`).join('');
document.querySelectorAll('.snippet').forEach(b => b.onclick = () => { $('#sqlInput').value = SNIPPETS[b.textContent]; runSql(); });

checkStatus(); loadOverview();
