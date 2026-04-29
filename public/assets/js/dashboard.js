const CFG = {
  API: (window.location.protocol === 'file:' || window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.hostname === '0.0.0.0')
    ? 'http://localhost:8000/api'
    : `${window.location.origin}/api`,
  TOKEN_KEY: 'agridata_token',
  USER_KEY:  'agridata_user',
};

let STATE = {
  user: null,
  demoMode: false,
  currentPage: 'dashboard',
  charts: {},
  data: {
    exploitations: [],
    parcelles: [],
    rendements: [],
    meteo: [],
    sol: [],
    intrants: [],
    alertes: [],
  },
  collecteTab: 'rendements',
  selectedExploitationId: null,
};

/* ================================================================
   DEMO DATA
================================================================ */
const DEMO = {
  user: { id: 1, first_name: 'Jean', last_name: 'Dupont', email: 'jean@exemple.fr', role: 'agriculteur', tenant_id: 1 },
  exploitations: [
    { id: 1, owner_id: 1, tenant_id: 1, name: 'Ferme du Soleil', region: 'Centre-Cameroun', total_area: 45.5, area_unit: 'hectares', main_crops: 'Maïs, Plantain, Manioc',
      parcelles: [
        { id: 1, name: 'Parcelle A1', area: 12.5, area_unit: 'hectares', crop_type: 'Maïs' },
        { id: 2, name: 'Parcelle B2', area: 18, area_unit: 'hectares', crop_type: 'Plantain' },
        { id: 3, name: 'Parcelle C3', area: 15, area_unit: 'hectares', crop_type: 'Manioc' },
      ]},
    { id: 2, owner_id: 1, tenant_id: 1, name: 'Plantation Nord', region: 'Adamaoua', total_area: 28, area_unit: 'hectares', main_crops: 'Sorgho, Mil',
      parcelles: [
        { id: 4, name: 'Parcelle N1', area: 14, area_unit: 'hectares', crop_type: 'Sorgho' },
        { id: 5, name: 'Parcelle N2', area: 14, area_unit: 'hectares', crop_type: 'Mil' },
      ]},
  ],
  rendements: [
    { id: 1, parcelle_id: 1, exploitation_id: 1, date_recolte: '2026-04-15', quantity: 850, unit: 'kg', crop_type: 'Maïs', quality_rating: 4 },
    { id: 2, parcelle_id: 2, exploitation_id: 1, date_recolte: '2026-04-12', quantity: 1200, unit: 'kg', crop_type: 'Plantain', quality_rating: 5 },
    { id: 3, parcelle_id: 3, exploitation_id: 1, date_recolte: '2026-03-28', quantity: 650, unit: 'kg', crop_type: 'Manioc', quality_rating: 3 },
    { id: 4, parcelle_id: 1, exploitation_id: 1, date_recolte: '2026-03-20', quantity: 720, unit: 'kg', crop_type: 'Maïs', quality_rating: 4 },
    { id: 5, parcelle_id: 4, exploitation_id: 2, date_recolte: '2026-04-10', quantity: 480, unit: 'kg', crop_type: 'Sorgho', quality_rating: 4 },
    { id: 6, parcelle_id: 5, exploitation_id: 2, date_recolte: '2026-04-05', quantity: 310, unit: 'kg', crop_type: 'Mil', quality_rating: 3 },
  ],
  meteo: [
    { id: 1, exploitation_id: 1, date_observation: '2026-04-28', temperature_min: 18, temperature_max: 32, temperature_avg: 25, precipitation: 12, humidity: 78, wind_speed: 8 },
    { id: 2, exploitation_id: 1, date_observation: '2026-04-27', temperature_min: 17, temperature_max: 31, temperature_avg: 24, precipitation: 8,  humidity: 74, wind_speed: 10 },
    { id: 3, exploitation_id: 1, date_observation: '2026-04-26', temperature_min: 19, temperature_max: 33, temperature_avg: 26, precipitation: 0,  humidity: 68, wind_speed: 6 },
    { id: 4, exploitation_id: 1, date_observation: '2026-04-25', temperature_min: 16, temperature_max: 29, temperature_avg: 23, precipitation: 25, humidity: 85, wind_speed: 14 },
    { id: 5, exploitation_id: 1, date_observation: '2026-04-24', temperature_min: 18, temperature_max: 30, temperature_avg: 24, precipitation: 5,  humidity: 72, wind_speed: 7 },
    { id: 6, exploitation_id: 1, date_observation: '2026-04-23', temperature_min: 20, temperature_max: 34, temperature_avg: 27, precipitation: 0,  humidity: 65, wind_speed: 5 },
    { id: 7, exploitation_id: 1, date_observation: '2026-04-22', temperature_min: 17, temperature_max: 31, temperature_avg: 24, precipitation: 18, humidity: 82, wind_speed: 12 },
  ],
  sol: [
    { id: 1, parcelle_id: 1, exploitation_id: 1, date_analyse: '2026-04-01', ph: 6.8, azote: 2.1, phosphore: 45, potassium: 180, matiere_organique: 3.2, notes: 'Sol en bonne condition' },
    { id: 2, parcelle_id: 2, exploitation_id: 1, date_analyse: '2026-03-15', ph: 7.2, azote: 1.8, phosphore: 38, potassium: 165, matiere_organique: 2.9, notes: '' },
    { id: 3, parcelle_id: 3, exploitation_id: 1, date_analyse: '2026-02-20', ph: 6.5, azote: 2.5, phosphore: 52, potassium: 195, matiere_organique: 3.5, notes: 'Léger amendement recommandé' },
  ],
  intrants: [
    { id: 1, exploitation_id: 1, parcelle_id: 1, type: 'engrais',   name: 'NPK 20-10-10',   quantity: 50, unit: 'kg', date_application: '2026-04-10', cost: 35000, effectiveness: 85 },
    { id: 2, exploitation_id: 1, parcelle_id: 2, type: 'pesticide', name: 'Deltamethrine',   quantity: 2,  unit: 'L',  date_application: '2026-04-05', cost: 8500,  effectiveness: 90 },
    { id: 3, exploitation_id: 2, parcelle_id: 4, type: 'engrais',   name: 'Urée 46%',        quantity: 30, unit: 'kg', date_application: '2026-04-18', cost: 18000, effectiveness: 78 },
    { id: 4, exploitation_id: 1, parcelle_id: 3, type: 'herbicide', name: 'Glyphosate 360', quantity: 3,  unit: 'L',  date_application: '2026-03-28', cost: 12000, effectiveness: 88 },
  ],
  alertes: [
    { id: 1, exploitation_id: 1, type: 'meteo_extreme',    severity: 'warning',  title: 'Risque de sécheresse',    description: 'Aucune précipitation prévue pendant 7 jours. Irrigation fortement recommandée pour les cultures de Maïs.', is_read: false, created_at: '2026-04-28T08:00:00' },
    { id: 2, exploitation_id: 1, type: 'sol_degrade',      severity: 'info',     title: 'pH sol à surveiller',     description: 'Le pH de la Parcelle C3 est légèrement acide (6.5). Un chaulage est recommandé avant la prochaine saison.', is_read: false, created_at: '2026-04-25T10:30:00' },
    { id: 3, exploitation_id: 2, type: 'anomalie_rendement', severity: 'critical', title: 'Rendement en baisse',   description: 'Le rendement de la Parcelle N1 est 30% inférieur à la moyenne saisonnière. Inspection terrain recommandée.', is_read: true, created_at: '2026-04-20T14:00:00' },
  ],
};

const api = {
  token: localStorage.getItem(CFG.TOKEN_KEY),
  headers() {
    return { 'Content-Type': 'application/json', 'Authorization': `Bearer ${this.token}` };
  },
  async request(path, options = {}) {
    const r = await fetch(`${CFG.API}${path}`, {
      method: options.method || 'GET',
      headers: this.headers(),
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
    const payload = await r.json().catch(() => null);
    if (r.status === 401) {
      logout();
      throw new Error(payload?.detail || 'Session expirée');
    }
    if (!r.ok) {
      throw new Error(payload?.detail || payload?.message || 'Erreur API');
    }
    return payload;
  },
  async get(path) {
    return this.request(path);
  },
  async post(path, data) {
    return this.request(path, { method: 'POST', body: data });
  },
  async put(path, data) {
    return this.request(path, { method: 'PUT', body: data });
  },
  async del(path) {
    await this.request(path, { method: 'DELETE' });
    return true;
  },
};

async function init() {
  const token = localStorage.getItem(CFG.TOKEN_KEY);
  if (!token) { window.location.href = 'index.html'; return; }

  // Try to get user from API, fall back to stored user or demo
  let user = null;
  try {
    user = await api.get('/auth/me');
    if (user && user.id) {
      STATE.user = user;
      localStorage.setItem(CFG.USER_KEY, JSON.stringify(user));
    } else { throw new Error('Bad response'); }
  } catch {
    const stored = localStorage.getItem(CFG.USER_KEY);
    if (stored) { STATE.user = JSON.parse(stored); }
    else { STATE.user = DEMO.user; STATE.demoMode = true; }
  }

  if (!STATE.user) { STATE.user = DEMO.user; STATE.demoMode = true; }

  setupUI();
  await loadAllData();
  showPage('dashboard');
}

function setupUI() {
  const u = STATE.user;
  const initials = `${u.first_name?.[0]||''}${u.last_name?.[0]||''}`.toUpperCase() || '??';
  const fullname = `${u.first_name||''} ${u.last_name||''}`.trim();
  const roleLabel = { admin: 'Administrateur', consultant: 'Consultant', agriculteur: 'Agriculteur' }[u.role] || u.role;

  ['sidebar-avatar', 'topbar-avatar'].forEach(id => { const el = document.getElementById(id); if (el) el.textContent = initials; });
  document.getElementById('sidebar-name').textContent = fullname;
  document.getElementById('sidebar-role').textContent = roleLabel;
  document.getElementById('topbar-name').textContent = fullname;
  document.getElementById('topbar-role').textContent = roleLabel;

  const date = new Date();
  document.getElementById('topbar-date').textContent = date.toLocaleDateString('fr-FR', { weekday: 'short', day: 'numeric', month: 'short' });

  if (STATE.demoMode) document.getElementById('demo-pill').style.display = 'inline-flex';

  // Admin sees all nav items; already rendered for all roles
}

async function loadAllData() {
  if (STATE.demoMode) {
    STATE.data.exploitations = DEMO.exploitations;
    STATE.data.rendements = DEMO.rendements;
    STATE.data.meteo = DEMO.meteo;
    STATE.data.sol = DEMO.sol;
    STATE.data.intrants = DEMO.intrants;
    STATE.data.alertes = DEMO.alertes;
    STATE.data.parcelles = DEMO.exploitations.flatMap(e => (e.parcelles||[]).map(p => ({ ...p, exploitation_id: e.id })));
    updateAlertBadge();
    return;
  }
  try {
    const [expls, rends, meteo, sol, intrants] = await Promise.all([
      api.get('/exploitations/'),
      api.get('/data/rendements/'),
      api.get('/data/meteo/'),
      api.get('/data/sol/'),
      api.get('/data/intrants/'),
    ]);
    STATE.data.exploitations = expls || [];
    STATE.data.rendements = rends || [];
    STATE.data.meteo = meteo || [];
    STATE.data.sol = sol || [];
    STATE.data.intrants = intrants || [];
    STATE.data.parcelles = STATE.data.exploitations.flatMap(e => (e.parcelles||[]).map(p => ({ ...p, exploitation_id: e.id })));
    STATE.data.alertes = DEMO.alertes; // alertes endpoint not implemented in API yet
  } catch {
    STATE.demoMode = true;
    Object.assign(STATE.data, { exploitations: DEMO.exploitations, rendements: DEMO.rendements, meteo: DEMO.meteo, sol: DEMO.sol, intrants: DEMO.intrants, alertes: DEMO.alertes });
    STATE.data.parcelles = DEMO.exploitations.flatMap(e => (e.parcelles||[]).map(p => ({ ...p, exploitation_id: e.id })));
  }
  updateAlertBadge();
}

function updateAlertBadge() {
  const unread = STATE.data.alertes.filter(a => !a.is_read).length;
  const badge = document.getElementById('alertes-count');
  const dot = document.getElementById('notif-dot');
  if (unread > 0) {
    badge.textContent = unread; badge.style.display = 'inline';
    dot.style.display = 'block';
  } else {
    badge.style.display = 'none'; dot.style.display = 'none';
  }
}

function logout() {
  localStorage.removeItem(CFG.TOKEN_KEY);
  localStorage.removeItem(CFG.USER_KEY);
  window.location.href = 'index.html';
}

/* ================================================================
   NAVIGATION
================================================================ */
function showPage(page) {
  STATE.currentPage = page;
  document.querySelectorAll('.nav-item').forEach(el => {
    el.classList.toggle('active', el.dataset.page === page);
  });
  const TITLES = {
    dashboard: 'Tableau de bord', exploitations: 'Exploitations', parcelles: 'Parcelles',
    collecte: 'Collecte de Données', meteo: 'Météo & Climat', analyses: 'Analyses',
    alertes: 'Alertes', rapports: 'Rapports', profil: 'Mon Profil',
  };
  document.getElementById('topbar-title').textContent = TITLES[page] || page;

  const area = document.getElementById('content-area');
  area.innerHTML = '<div class="loading-spinner"><div class="spinner"></div></div>';

  // Close sidebar on mobile
  if (window.innerWidth <= 768) closeSidebar();

  setTimeout(() => {
    const renders = {
      dashboard: renderDashboard, exploitations: renderExploitations,
      parcelles: renderParcelles, collecte: renderCollecte,
      meteo: renderMeteo, analyses: renderAnalyses,
      alertes: renderAlertes, rapports: renderRapports,
      profil: renderProfil,
    };
    if (renders[page]) renders[page]();
  }, 80);
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
  document.getElementById('sidebar-overlay').classList.toggle('open');
}
function closeSidebar() {
  document.getElementById('sidebar').classList.remove('open');
  document.getElementById('sidebar-overlay').classList.remove('open');
}

/* ================================================================
   CHART HELPER
================================================================ */
function mkChart(id, config) {
  if (STATE.charts[id]) { STATE.charts[id].destroy(); delete STATE.charts[id]; }
  const el = document.getElementById(id);
  if (el) { STATE.charts[id] = new Chart(el, config); }
}

/* ================================================================
   PAGE: DASHBOARD
================================================================ */
function renderDashboard() {
  const u = STATE.user;
  const exploitations = STATE.data.exploitations;
  const rendements = STATE.data.rendements;
  const alertesUnread = STATE.data.alertes.filter(a => !a.is_read).length;
  const parcelles = STATE.data.parcelles;
  const avgYield = rendements.length ? (rendements.reduce((s,r) => s + r.quantity, 0) / rendements.length).toFixed(0) : 0;
  const totalRend = rendements.reduce((s,r) => s + r.quantity, 0);
  const latestMeteo = STATE.data.meteo[0] || {};
  const firstName = u.first_name || 'Agriculteur';

  const recentRends = [...rendements].sort((a,b) => b.date_recolte > a.date_recolte ? 1 : -1).slice(0, 5);

  document.getElementById('content-area').innerHTML = `
    <div class="page-header">
      <h1>Bonjour, ${firstName} 👋</h1>
      <p>${new Date().toLocaleDateString('fr-FR', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })}${STATE.demoMode ? ' — <span style="color:var(--orange)">Mode démonstration actif</span>' : ''}</p>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-icon green"><i class="fas fa-tractor"></i></div>
        <div class="stat-info">
          <div class="stat-value">${exploitations.length}</div>
          <div class="stat-label">Exploitations</div>
          <div class="stat-change up"><i class="fas fa-arrow-up"></i> actives</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange"><i class="fas fa-map-marked-alt"></i></div>
        <div class="stat-info">
          <div class="stat-value">${parcelles.length}</div>
          <div class="stat-label">Parcelles totales</div>
          <div class="stat-change up">${exploitations.reduce((s,e)=>(s+(e.total_area||0)),0).toFixed(1)} ha</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue"><i class="fas fa-weight-hanging"></i></div>
        <div class="stat-info">
          <div class="stat-value">${avgYield} <small style="font-size:0.9rem;font-weight:400">kg</small></div>
          <div class="stat-label">Rendement moyen</div>
          <div class="stat-change up">${totalRend.toLocaleString('fr-FR')} kg total</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon red"><i class="fas fa-exclamation-circle"></i></div>
        <div class="stat-info">
          <div class="stat-value" style="color:${alertesUnread>0?'var(--red)':'var(--primary)'}">${alertesUnread}</div>
          <div class="stat-label">Alertes actives</div>
          <div class="stat-change ${alertesUnread>0?'down':'up'}">${STATE.data.alertes.length} au total</div>
        </div>
      </div>
    </div>

    <div class="charts-row">
      <div class="card">
        <div class="card-header">
          <h3><i class="fas fa-chart-line" style="color:var(--primary);margin-right:6px"></i>Évolution des Rendements</h3>
          <span class="badge badge-green">6 mois</span>
        </div>
        <canvas id="chart-yield" height="100"></canvas>
      </div>
      <div class="card">
        <div class="card-header">
          <h3><i class="fas fa-seedling" style="color:var(--primary);margin-right:6px"></i>Répartition Cultures</h3>
        </div>
        <canvas id="chart-crops" height="160"></canvas>
      </div>
    </div>

    <div class="bottom-row">
      <div class="card">
        <div class="card-header">
          <h3>Dernières Collectes</h3>
          <button class="btn btn-sm btn-outline" onclick="showPage('collecte')"><i class="fas fa-arrow-right"></i> Voir tout</button>
        </div>
        <div class="table-wrap">
          <table>
            <thead><tr><th>Culture</th><th>Parcelle</th><th>Qté</th><th>Date</th><th>Qualité</th></tr></thead>
            <tbody>
              ${recentRends.length ? recentRends.map(r => {
                const p = STATE.data.parcelles.find(p => p.id === r.parcelle_id);
                return `<tr>
                  <td><span class="badge badge-green">${r.crop_type||'—'}</span></td>
                  <td>${p ? p.name : `#${r.parcelle_id}`}</td>
                  <td><strong>${r.quantity} ${r.unit}</strong></td>
                  <td>${formatDate(r.date_recolte)}</td>
                  <td>${'★'.repeat(r.quality_rating||0)}${'☆'.repeat(5-(r.quality_rating||0))}</td>
                </tr>`;
              }).join('') : '<tr><td colspan="5" style="text-align:center;color:var(--text-3);padding:2rem">Aucune collecte enregistrée</td></tr>'}
            </tbody>
          </table>
        </div>
      </div>
      <div class="card">
        <div class="card-header">
          <h3>Actions Rapides</h3>
        </div>
        <div class="quick-actions">
          <div class="action-btn" onclick="openCollecteModal('rendements')">
            <div class="a-icon" style="background:rgba(31,111,67,0.1);color:var(--primary)"><i class="fas fa-plus"></i></div>
            <div class="a-label">Saisir Rendement</div>
          </div>
          <div class="action-btn" onclick="openCollecteModal('meteo')">
            <div class="a-icon" style="background:rgba(58,143,214,0.1);color:var(--blue)"><i class="fas fa-cloud-sun"></i></div>
            <div class="a-label">Enregistrer Météo</div>
          </div>
          <div class="action-btn" onclick="openCollecteModal('sol')">
            <div class="a-icon" style="background:rgba(139,92,246,0.1);color:var(--purple)"><i class="fas fa-vial"></i></div>
            <div class="a-label">Analyse Sol</div>
          </div>
          <div class="action-btn" onclick="showPage('alertes')">
            <div class="a-icon" style="background:rgba(224,82,82,0.1);color:var(--red)"><i class="fas fa-bell"></i></div>
            <div class="a-label">Voir Alertes ${alertesUnread>0?`<span class="badge badge-red">${alertesUnread}</span>`:''}</div>
          </div>
          <div class="action-btn" onclick="showAddExploitation()">
            <div class="a-icon" style="background:rgba(232,129,60,0.1);color:var(--orange)"><i class="fas fa-tractor"></i></div>
            <div class="a-label">Nouvelle Exploitation</div>
          </div>
          <div class="action-btn" onclick="showPage('analyses')">
            <div class="a-icon" style="background:rgba(212,230,92,0.25);color:var(--primary)"><i class="fas fa-chart-bar"></i></div>
            <div class="a-label">Analyses</div>
          </div>
        </div>

        ${latestMeteo.temperature_avg ? `
        <div style="margin-top:1.2rem; padding-top:1rem; border-top:1px solid var(--border)">
          <div class="text-xs text-muted fw-700" style="text-transform:uppercase;letter-spacing:.06em;margin-bottom:.6rem">Météo aujourd'hui — Ferme du Soleil</div>
          <div style="display:flex;gap:1rem;flex-wrap:wrap">
            <div style="display:flex;align-items:center;gap:5px"><i class="fas fa-thermometer-half" style="color:var(--orange)"></i><span class="text-sm"><strong>${latestMeteo.temperature_avg}°C</strong></span></div>
            <div style="display:flex;align-items:center;gap:5px"><i class="fas fa-tint" style="color:var(--blue)"></i><span class="text-sm"><strong>${latestMeteo.humidity}%</strong></span></div>
            <div style="display:flex;align-items:center;gap:5px"><i class="fas fa-cloud-rain" style="color:var(--blue)"></i><span class="text-sm"><strong>${latestMeteo.precipitation} mm</strong></span></div>
          </div>
        </div>` : ''}
      </div>
    </div>
  `;

  // Charts
  const months = ['Nov', 'Déc', 'Jan', 'Fév', 'Mar', 'Avr'];
  mkChart('chart-yield', {
    type: 'line',
    data: {
      labels: months,
      datasets: [{
        label: 'Rendement total (kg)',
        data: [1800, 2100, 1650, 2400, 1970, rendements.reduce((s,r)=>s+r.quantity,0)],
        borderColor: '#1f6f43', backgroundColor: 'rgba(31,111,67,0.08)',
        tension: 0.4, fill: true, pointBackgroundColor: '#1f6f43', pointRadius: 4,
      }],
    },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { color: '#e8f0eb' } }, x: { grid: { display: false } } } },
  });

  // Crop distribution
  const cropMap = {};
  STATE.data.rendements.forEach(r => { cropMap[r.crop_type||'Autre'] = (cropMap[r.crop_type||'Autre']||0) + r.quantity; });
  const crops = Object.keys(cropMap);
  const colors = ['#1f6f43','#d4e65c','#3a8fd6','#e8813c','#8b5cf6','#e05252'];
  mkChart('chart-crops', {
    type: 'doughnut',
    data: { labels: crops, datasets: [{ data: crops.map(c=>cropMap[c]), backgroundColor: colors.slice(0,crops.length), borderWidth: 0 }] },
    options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { padding: 14, font: { size: 11 } } } }, cutout: '65%' },
  });
}

/* ================================================================
   PAGE: EXPLOITATIONS
================================================================ */
function renderExploitations() {
  const expls = STATE.data.exploitations;
  document.getElementById('content-area').innerHTML = `
    <div class="flex-between mb-15">
      <div class="page-header" style="margin-bottom:0">
        <h1>Exploitations</h1>
        <p>${expls.length} exploitation${expls.length>1?'s':''} enregistrée${expls.length>1?'s':''}</p>
      </div>
      <button class="btn btn-primary" onclick="showAddExploitation()"><i class="fas fa-plus"></i> Nouvelle exploitation</button>
    </div>
    <div class="exploitations-grid" id="expls-grid">
      ${expls.length ? expls.map(e => renderExplCard(e)).join('') : `
        <div class="empty-state">
          <div class="empty-icon"><i class="fas fa-tractor"></i></div>
          <p>Aucune exploitation enregistrée.<br>Créez votre première exploitation.</p>
        </div>`}
    </div>`;
}

function renderExplCard(e) {
  const parcelles = e.parcelles || STATE.data.parcelles.filter(p => p.exploitation_id === e.id);
  const crops = (e.main_crops || '').split(',').map(c=>c.trim()).filter(Boolean);
  return `<div class="expl-card">
    <div class="expl-header">
      <div>
        <div class="expl-name">${e.name}</div>
        <div class="expl-region"><i class="fas fa-map-pin" style="font-size:.7rem"></i> ${e.region || 'Région non définie'}</div>
      </div>
      <span class="badge badge-green">Active</span>
    </div>
    <div class="expl-meta">
      <div class="expl-meta-item"><i class="fas fa-ruler-combined"></i> ${e.total_area||'—'} ${e.area_unit||'ha'}</div>
      <div class="expl-meta-item"><i class="fas fa-map"></i> ${parcelles.length} parcelle${parcelles.length>1?'s':''}</div>
    </div>
    <div class="expl-crops">${crops.map(c=>`<span class="crop-chip">${c}</span>`).join('')}</div>
    <div class="expl-footer">
      <button class="btn btn-sm btn-outline" onclick="viewExploitation(${e.id})"><i class="fas fa-eye"></i> Détails</button>
      <button class="btn btn-sm btn-outline" onclick="showEditExploitation(${e.id})"><i class="fas fa-edit"></i></button>
      <button class="btn btn-sm btn-danger" onclick="deleteExploitation(${e.id})"><i class="fas fa-trash"></i></button>
    </div>
  </div>`;
}

function viewExploitation(id) {
  const e = STATE.data.exploitations.find(x => x.id === id);
  if (!e) return;
  const parcelles = e.parcelles || STATE.data.parcelles.filter(p => p.exploitation_id === id);
  const rends = STATE.data.rendements.filter(r => r.exploitation_id === id);
  const avgQ = rends.length ? (rends.reduce((s,r)=>s+r.quantity,0)/rends.length).toFixed(0) : '—';
  showModal(`Détails — ${e.name}`, `
    <div class="profile-section">
      <h4>Informations générales</h4>
      <div class="form-grid" style="grid-template-columns:1fr 1fr;gap:.7rem">
        ${infoRow('Région', e.region)} ${infoRow('Surface', `${e.total_area||'—'} ${e.area_unit}`)}
        ${infoRow('Cultures', e.main_crops)} ${infoRow('Rendement moyen', avgQ !== '—' ? avgQ+' kg' : '—')}
      </div>
    </div>
    <div class="profile-section">
      <h4>Parcelles (${parcelles.length})</h4>
      ${parcelles.length ? `<div class="table-wrap"><table>
        <thead><tr><th>Nom</th><th>Surface</th><th>Culture</th></tr></thead>
        <tbody>${parcelles.map(p=>`<tr><td>${p.name}</td><td>${p.area||'—'} ${p.area_unit||'ha'}</td><td><span class="badge badge-green">${p.crop_type||'—'}</span></td></tr>`).join('')}</tbody>
      </table></div>` : '<p class="text-muted text-sm">Aucune parcelle</p>'}
    </div>
    ${e.description ? `<div class="profile-section"><h4>Description</h4><p class="text-sm text-muted">${e.description}</p></div>` : ''}
    <div class="form-actions"><button class="btn btn-outline" onclick="hideModal()">Fermer</button><button class="btn btn-primary" onclick="showPage('parcelles');hideModal()"><i class="fas fa-map"></i> Voir parcelles</button></div>
  `, true);
}

function infoRow(label, val) {
  return `<div><div class="text-xs text-muted">${label}</div><div class="text-sm fw-700">${val||'—'}</div></div>`;
}

function showAddExploitation() {
  showModal('Nouvelle exploitation', getExploitationForm(null));
}

function showEditExploitation(id) {
  const e = STATE.data.exploitations.find(x => x.id === id);
  showModal('Modifier exploitation', getExploitationForm(e));
}

function getExploitationForm(e) {
  return `
    <form onsubmit="saveExploitation(event, ${e ? e.id : 'null'})">
      <div class="form-grid">
        <div class="form-group"><label>Nom *</label><input name="name" required value="${e?.name||''}" placeholder="Ex: Ferme du Soleil"></div>
        <div class="form-group"><label>Région</label><input name="region" value="${e?.region||''}" placeholder="Ex: Centre"></div>
        <div class="form-group"><label>Surface totale</label><input name="total_area" type="number" step="0.1" value="${e?.total_area||''}" placeholder="45.5"></div>
        <div class="form-group"><label>Unité</label>
          <select name="area_unit"><option ${e?.area_unit==='hectares'?'selected':''}>hectares</option><option ${e?.area_unit==='ares'?'selected':''}>ares</option><option ${e?.area_unit==='m2'?'selected':''}>m²</option></select>
        </div>
        <div class="form-group" style="grid-column:1/-1"><label>Cultures principales</label><input name="main_crops" value="${e?.main_crops||''}" placeholder="Ex: Maïs, Plantain, Manioc"></div>
        <div class="form-group" style="grid-column:1/-1"><label>Description</label><textarea name="description">${e?.description||''}</textarea></div>
      </div>
      <div class="form-actions">
        <button type="button" class="btn btn-outline" onclick="hideModal()">Annuler</button>
        <button type="submit" class="btn btn-primary"><i class="fas fa-save"></i> ${e ? 'Mettre à jour' : 'Créer'}</button>
      </div>
    </form>`;
}

async function saveExploitation(ev, id) {
  ev.preventDefault();
  const fd = new FormData(ev.target);
  const data = { name: fd.get('name'), region: fd.get('region'), total_area: parseFloat(fd.get('total_area'))||null, area_unit: fd.get('area_unit'), main_crops: fd.get('main_crops'), description: fd.get('description') };
  if (STATE.demoMode) {
    if (id) {
      const idx = STATE.data.exploitations.findIndex(e=>e.id===id);
      if (idx>=0) STATE.data.exploitations[idx] = { ...STATE.data.exploitations[idx], ...data };
    } else {
      const newId = Math.max(0,...STATE.data.exploitations.map(e=>e.id)) + 1;
      STATE.data.exploitations.push({ id: newId, owner_id: STATE.user.id, tenant_id: STATE.user.tenant_id, parcelles: [], ...data });
    }
    hideModal(); toast('Exploitation enregistrée', 'success'); renderExploitations(); return;
  }
  try {
    if (id) await api.put(`/exploitations/${id}`, data);
    else await api.post('/exploitations/', data);
    await loadAllData();
    hideModal(); toast('Exploitation enregistrée', 'success'); renderExploitations();
  } catch { toast('Erreur lors de la sauvegarde', 'error'); }
}

async function deleteExploitation(id) {
  if (!confirm('Supprimer cette exploitation ? Cette action est irréversible.')) return;
  if (STATE.demoMode) {
    STATE.data.exploitations = STATE.data.exploitations.filter(e=>e.id!==id);
    toast('Exploitation supprimée', 'success'); renderExploitations(); return;
  }
  await api.del(`/exploitations/${id}`);
  await loadAllData();
  toast('Exploitation supprimée', 'success'); renderExploitations();
}

/* ================================================================
   PAGE: PARCELLES
================================================================ */
function renderParcelles() {
  const expls = STATE.data.exploitations;
  const selId = STATE.selectedExploitationId || (expls[0]?.id);
  const parcelles = selId
    ? (expls.find(e=>e.id===selId)?.parcelles || STATE.data.parcelles.filter(p=>p.exploitation_id===selId))
    : STATE.data.parcelles;

  document.getElementById('content-area').innerHTML = `
    <div class="flex-between mb-15">
      <div class="page-header" style="margin-bottom:0">
        <h1>Parcelles</h1>
        <p>${parcelles.length} parcelle${parcelles.length>1?'s':''}</p>
      </div>
      <div class="flex-gap">
        <select class="btn btn-outline" onchange="filterParcellesByExpl(event)" style="padding:7px 12px">
          <option value="">Toutes les exploitations</option>
          ${expls.map(e=>`<option value="${e.id}" ${selId===e.id?'selected':''}>${e.name}</option>`).join('')}
        </select>
        <button class="btn btn-primary" onclick="showAddParcelle()"><i class="fas fa-plus"></i> Nouvelle parcelle</button>
      </div>
    </div>
    <div class="card">
      <div class="table-wrap">
        <table>
          <thead><tr><th>Nom</th><th>Exploitation</th><th>Surface</th><th>Culture</th><th>Rendements</th><th>Actions</th></tr></thead>
          <tbody>
            ${parcelles.length ? parcelles.map(p => {
              const expl = expls.find(e=>e.id===p.exploitation_id);
              const rends = STATE.data.rendements.filter(r=>r.parcelle_id===p.id);
              return `<tr>
                <td><strong>${p.name}</strong></td>
                <td><span class="text-muted">${expl?.name||'—'}</span></td>
                <td>${p.area||'—'} ${p.area_unit||'ha'}</td>
                <td><span class="badge badge-green">${p.crop_type||'—'}</span></td>
                <td><span class="badge badge-blue">${rends.length} enreg.</span></td>
                <td><div class="td-actions">
                  <button class="btn btn-icon btn-outline" onclick="showEditParcelle(${p.id})" title="Modifier"><i class="fas fa-edit"></i></button>
                  <button class="btn btn-icon btn-danger" onclick="deleteParcelle(${p.id})" title="Supprimer"><i class="fas fa-trash"></i></button>
                </div></td>
              </tr>`;
            }).join('') : '<tr><td colspan="6" style="text-align:center;color:var(--text-3);padding:2rem">Aucune parcelle trouvée</td></tr>'}
          </tbody>
        </table>
      </div>
    </div>`;
}

function filterParcellesByExpl(ev) {
  STATE.selectedExploitationId = ev.target.value ? parseInt(ev.target.value) : null;
  renderParcelles();
}

function showAddParcelle() {
  showModal('Nouvelle parcelle', getParcelleForm(null));
}
function showEditParcelle(id) {
  const p = STATE.data.parcelles.find(x=>x.id===id);
  showModal('Modifier parcelle', getParcelleForm(p));
}

function getParcelleForm(p) {
  const expls = STATE.data.exploitations;
  return `<form onsubmit="saveParcelle(event,${p?p.id:'null'})">
    <div class="form-grid">
      <div class="form-group"><label>Exploitation *</label>
        <select name="exploitation_id" required>
          ${expls.map(e=>`<option value="${e.id}" ${p?.exploitation_id===e.id?'selected':''}>${e.name}</option>`).join('')}
        </select>
      </div>
      <div class="form-group"><label>Nom parcelle *</label><input name="name" required value="${p?.name||''}" placeholder="Ex: Parcelle A1"></div>
      <div class="form-group"><label>Surface</label><input name="area" type="number" step="0.1" value="${p?.area||''}" placeholder="12.5"></div>
      <div class="form-group"><label>Unité</label>
        <select name="area_unit"><option>hectares</option><option>ares</option><option>m²</option></select>
      </div>
      <div class="form-group" style="grid-column:1/-1"><label>Type de culture</label>
        <select name="crop_type">
          <option value="">Sélectionner</option>
          ${['Maïs','Manioc','Plantain','Sorgho','Mil','Arachides','Tomate','Piment','Autre'].map(c=>`<option ${p?.crop_type===c?'selected':''}>${c}</option>`).join('')}
        </select>
      </div>
    </div>
    <div class="form-actions">
      <button type="button" class="btn btn-outline" onclick="hideModal()">Annuler</button>
      <button type="submit" class="btn btn-primary"><i class="fas fa-save"></i> ${p?'Mettre à jour':'Créer'}</button>
    </div>
  </form>`;
}

async function saveParcelle(ev, id) {
  ev.preventDefault();
  const fd = new FormData(ev.target);
  const expl_id = parseInt(fd.get('exploitation_id'));
  const data = { exploitation_id: expl_id, name: fd.get('name'), area: parseFloat(fd.get('area'))||null, area_unit: fd.get('area_unit'), crop_type: fd.get('crop_type')||null };

  if (STATE.demoMode) {
    if (id) {
      STATE.data.parcelles = STATE.data.parcelles.map(p => p.id===id ? {...p,...data} : p);
      const expl = STATE.data.exploitations.find(e=>e.id===expl_id);
      if (expl?.parcelles) expl.parcelles = expl.parcelles.map(p=>p.id===id?{...p,...data}:p);
    } else {
      const newId = Math.max(0,...STATE.data.parcelles.map(p=>p.id))+1;
      const newP = { id: newId, ...data };
      STATE.data.parcelles.push(newP);
      const expl = STATE.data.exploitations.find(e=>e.id===expl_id);
      if (expl) { expl.parcelles = expl.parcelles||[]; expl.parcelles.push(newP); }
    }
    hideModal(); toast('Parcelle enregistrée', 'success'); renderParcelles(); return;
  }
  try {
    if (id) await api.put(`/parcelles/${id}`, data);
    else await api.post('/parcelles/', data);
    await loadAllData();
    hideModal();
    toast('Parcelle enregistrée', 'success');
    renderParcelles();
  } catch (err) {
    toast(err.message || 'Erreur lors de la sauvegarde de la parcelle', 'error');
  }
}

async function deleteParcelle(id) {
  if (!confirm('Supprimer cette parcelle ?')) return;
  if (STATE.demoMode) {
    STATE.data.parcelles = STATE.data.parcelles.filter(p=>p.id!==id);
    STATE.data.exploitations.forEach(e => { if (e.parcelles) e.parcelles = e.parcelles.filter(p=>p.id!==id); });
    toast('Parcelle supprimée', 'success'); renderParcelles(); return;
  }
  try {
    await api.del(`/parcelles/${id}`);
    await loadAllData();
    toast('Parcelle supprimée', 'success');
    renderParcelles();
  } catch (err) {
    toast(err.message || 'Erreur lors de la suppression', 'error');
  }
}

/* ================================================================
   PAGE: COLLECTE DE DONNÉES
================================================================ */
function renderCollecte() {
  const tabs = ['rendements','meteo','sol','intrants'];
  const labels = ['Rendements','Météo','Qualité Sol','Intrants'];
  const icons = ['fa-weight-hanging','fa-cloud-sun','fa-vial','fa-box'];
  document.getElementById('content-area').innerHTML = `
    <div class="flex-between mb-15">
      <div class="page-header" style="margin-bottom:0"><h1>Collecte de Données</h1><p>Enregistrement et suivi des données agricoles</p></div>
      <button class="btn btn-primary" onclick="openCollecteModal(STATE.collecteTab)"><i class="fas fa-plus"></i> Nouvelle saisie</button>
    </div>
    <div class="tabs">
      ${tabs.map((t,i)=>`<button class="tab-btn ${STATE.collecteTab===t?'active':''}" onclick="switchCollecteTab('${t}')"><i class="fas ${icons[i]}" style="margin-right:5px"></i>${labels[i]}</button>`).join('')}
    </div>
    <div id="collecte-content"></div>`;
  renderCollecteTab();
}

function switchCollecteTab(tab) {
  STATE.collecteTab = tab;
  document.querySelectorAll('.tab-btn').forEach((b,i)=>{
    b.classList.toggle('active', ['rendements','meteo','sol','intrants'][i]===tab);
  });
  renderCollecteTab();
}

function renderCollecteTab() {
  const tab = STATE.collecteTab;
  const el = document.getElementById('collecte-content');
  if (!el) return;

  if (tab === 'rendements') {
    const data = STATE.data.rendements;
    el.innerHTML = `<div class="card"><div class="card-header"><h3>Rendements enregistrés (${data.length})</h3></div><div class="table-wrap"><table>
      <thead><tr><th>Date</th><th>Culture</th><th>Quantité</th><th>Parcelle</th><th>Qualité</th><th>Actions</th></tr></thead>
      <tbody>${data.length ? data.map(r=>{
        const p=STATE.data.parcelles.find(x=>x.id===r.parcelle_id);
        return `<tr><td>${formatDate(r.date_recolte)}</td><td><span class="badge badge-green">${r.crop_type||'—'}</span></td>
        <td><strong>${r.quantity} ${r.unit}</strong></td><td>${p?p.name:'#'+r.parcelle_id}</td>
        <td class="quality-stars">${'★'.repeat(r.quality_rating||0)}${'☆'.repeat(5-(r.quality_rating||0))}</td>
        <td><button class="btn btn-icon btn-danger" onclick="deleteCollecteItem('rendements',${r.id})"><i class="fas fa-trash"></i></button></td></tr>`;
      }).join('') : '<tr><td colspan="6" style="text-align:center;color:var(--text-3);padding:2rem">Aucun rendement</td></tr>'}
      </tbody></table></div></div>`;
  }
  else if (tab === 'meteo') {
    const data = STATE.data.meteo;
    el.innerHTML = `<div class="card"><div class="card-header"><h3>Données météo (${data.length})</h3></div><div class="table-wrap"><table>
      <thead><tr><th>Date</th><th>Exploitation</th><th>Temp. moy.</th><th>Min/Max</th><th>Précip.</th><th>Humidité</th><th>Actions</th></tr></thead>
      <tbody>${data.length ? data.map(m=>{
        const e=STATE.data.exploitations.find(x=>x.id===m.exploitation_id);
        return `<tr><td>${formatDate(m.date_observation)}</td><td>${e?e.name:'—'}</td>
        <td><strong>${m.temperature_avg||'—'}°C</strong></td><td class="text-muted">${m.temperature_min||'—'}° / ${m.temperature_max||'—'}°</td>
        <td><span class="badge badge-blue">${m.precipitation||0} mm</span></td><td>${m.humidity||'—'}%</td>
        <td><button class="btn btn-icon btn-danger" onclick="deleteCollecteItem('meteo',${m.id})"><i class="fas fa-trash"></i></button></td></tr>`;
      }).join('') : '<tr><td colspan="7" style="text-align:center;color:var(--text-3);padding:2rem">Aucune donnée météo</td></tr>'}
      </tbody></table></div></div>`;
  }
  else if (tab === 'sol') {
    const data = STATE.data.sol;
    el.innerHTML = `<div class="card"><div class="card-header"><h3>Analyses sol (${data.length})</h3></div><div class="table-wrap"><table>
      <thead><tr><th>Date</th><th>Parcelle</th><th>pH</th><th>Azote</th><th>Phosphore</th><th>Potassium</th><th>Actions</th></tr></thead>
      <tbody>${data.length ? data.map(s=>{
        const p=STATE.data.parcelles.find(x=>x.id===s.parcelle_id);
        const phColor = s.ph<6?'badge-orange':s.ph>7.5?'badge-purple':'badge-green';
        return `<tr><td>${formatDate(s.date_analyse)}</td><td>${p?p.name:'—'}</td>
        <td><span class="badge ${phColor}">${s.ph}</span></td>
        <td>${s.azote||'—'} g/kg</td><td>${s.phosphore||'—'} mg/kg</td><td>${s.potassium||'—'} mg/kg</td>
        <td><button class="btn btn-icon btn-danger" onclick="deleteCollecteItem('sol',${s.id})"><i class="fas fa-trash"></i></button></td></tr>`;
      }).join('') : '<tr><td colspan="7" style="text-align:center;color:var(--text-3);padding:2rem">Aucune analyse</td></tr>'}
      </tbody></table></div></div>`;
  }
  else if (tab === 'intrants') {
    const data = STATE.data.intrants;
    el.innerHTML = `<div class="card"><div class="card-header"><h3>Intrants enregistrés (${data.length})</h3></div><div class="table-wrap"><table>
      <thead><tr><th>Date</th><th>Exploitation</th><th>Type</th><th>Produit</th><th>Quantité</th><th>Coût</th><th>Actions</th></tr></thead>
      <tbody>${data.length ? data.map(i=>{
        const e=STATE.data.exploitations.find(x=>x.id===i.exploitation_id);
        const typeColors={'engrais':'badge-green','pesticide':'badge-red','herbicide':'badge-orange','fongicide':'badge-purple'};
        return `<tr><td>${formatDate(i.date_application)}</td><td>${e?e.name:'—'}</td>
        <td><span class="badge ${typeColors[i.type]||'badge-gray'}">${i.type}</span></td>
        <td><strong>${i.name}</strong></td><td>${i.quantity||'—'} ${i.unit||''}</td>
        <td>${i.cost ? (i.cost).toLocaleString('fr-FR')+' XAF' : '—'}</td>
        <td><button class="btn btn-icon btn-danger" onclick="deleteCollecteItem('intrants',${i.id})"><i class="fas fa-trash"></i></button></td></tr>`;
      }).join('') : '<tr><td colspan="7" style="text-align:center;color:var(--text-3);padding:2rem">Aucun intrant</td></tr>'}
      </tbody></table></div></div>`;
  }
}

function openCollecteModal(type) {
  STATE.collecteTab = type;
  const titles = { rendements: 'Saisir un rendement', meteo: 'Enregistrer météo', sol: 'Analyse de sol', intrants: 'Ajouter un intrant' };
  showModal(titles[type]||'Saisie', getCollecteForm(type));
}

function getCollecteForm(type) {
  const expls = STATE.data.exploitations;
  const parcelles = STATE.data.parcelles;
  const today = new Date().toISOString().split('T')[0];

  if (type === 'rendements') return `<form onsubmit="saveCollecte(event,'rendements')">
    <div class="form-grid">
      <div class="form-group"><label>Parcelle *</label><select name="parcelle_id" required>
        ${parcelles.map(p=>`<option value="${p.id}">${p.name} (${STATE.data.exploitations.find(e=>e.id===p.exploitation_id)?.name||'—'})</option>`).join('')}
      </select></div>
      <div class="form-group"><label>Date récolte *</label><input name="date_recolte" type="date" required value="${today}"></div>
      <div class="form-group"><label>Quantité *</label><input name="quantity" type="number" step="0.1" required placeholder="850"></div>
      <div class="form-group"><label>Unité</label><select name="unit"><option>kg</option><option>tonnes</option><option>sacs</option><option>bottes</option></select></div>
      <div class="form-group"><label>Type de culture</label><select name="crop_type">
        ${['Maïs','Manioc','Plantain','Sorgho','Mil','Arachides','Tomate','Autre'].map(c=>`<option>${c}</option>`).join('')}
      </select></div>
      <div class="form-group"><label>Qualité (1-5)</label>
        <select name="quality_rating"><option value="">—</option>${[1,2,3,4,5].map(n=>`<option value="${n}">${n} ★</option>`).join('')}</select>
      </div>
      <div class="form-group" style="grid-column:1/-1"><label>Notes</label><textarea name="notes" placeholder="Observations..."></textarea></div>
    </div>
    <div class="form-actions"><button type="button" class="btn btn-outline" onclick="hideModal()">Annuler</button><button type="submit" class="btn btn-primary"><i class="fas fa-save"></i> Enregistrer</button></div>
  </form>`;

  if (type === 'meteo') return `<form onsubmit="saveCollecte(event,'meteo')">
    <div class="form-grid">
      <div class="form-group"><label>Exploitation *</label><select name="exploitation_id" required>
        ${expls.map(e=>`<option value="${e.id}">${e.name}</option>`).join('')}
      </select></div>
      <div class="form-group"><label>Date observation *</label><input name="date_observation" type="date" required value="${today}"></div>
      <div class="form-group"><label>Temp. min (°C)</label><input name="temperature_min" type="number" step="0.1" placeholder="18"></div>
      <div class="form-group"><label>Temp. max (°C)</label><input name="temperature_max" type="number" step="0.1" placeholder="32"></div>
      <div class="form-group"><label>Temp. moy. (°C)</label><input name="temperature_avg" type="number" step="0.1" placeholder="25"></div>
      <div class="form-group"><label>Précipitations (mm)</label><input name="precipitation" type="number" step="0.1" placeholder="12"></div>
      <div class="form-group"><label>Humidité (%)</label><input name="humidity" type="number" min="0" max="100" placeholder="78"></div>
      <div class="form-group"><label>Vitesse vent (km/h)</label><input name="wind_speed" type="number" step="0.1" placeholder="8"></div>
    </div>
    <div class="form-actions"><button type="button" class="btn btn-outline" onclick="hideModal()">Annuler</button><button type="submit" class="btn btn-primary"><i class="fas fa-save"></i> Enregistrer</button></div>
  </form>`;

  if (type === 'sol') return `<form onsubmit="saveCollecte(event,'sol')">
    <div class="form-grid">
      <div class="form-group"><label>Parcelle *</label><select name="parcelle_id" required>
        ${parcelles.map(p=>`<option value="${p.id}">${p.name}</option>`).join('')}
      </select></div>
      <div class="form-group"><label>Date analyse *</label><input name="date_analyse" type="date" required value="${today}"></div>
      <div class="form-group"><label>pH</label><input name="ph" type="number" step="0.1" min="0" max="14" placeholder="6.8"></div>
      <div class="form-group"><label>Azote (g/kg)</label><input name="azote" type="number" step="0.01" placeholder="2.1"></div>
      <div class="form-group"><label>Phosphore (mg/kg)</label><input name="phosphore" type="number" step="0.1" placeholder="45"></div>
      <div class="form-group"><label>Potassium (mg/kg)</label><input name="potassium" type="number" step="0.1" placeholder="180"></div>
      <div class="form-group"><label>Matière organique (%)</label><input name="matiere_organique" type="number" step="0.1" placeholder="3.2"></div>
      <div class="form-group" style="grid-column:1/-1"><label>Notes</label><textarea name="notes" placeholder="Recommandations..."></textarea></div>
    </div>
    <div class="form-actions"><button type="button" class="btn btn-outline" onclick="hideModal()">Annuler</button><button type="submit" class="btn btn-primary"><i class="fas fa-save"></i> Enregistrer</button></div>
  </form>`;

  if (type === 'intrants') return `<form onsubmit="saveCollecte(event,'intrants')">
    <div class="form-grid">
      <div class="form-group"><label>Exploitation *</label><select name="exploitation_id" required>
        ${expls.map(e=>`<option value="${e.id}">${e.name}</option>`).join('')}
      </select></div>
      <div class="form-group"><label>Parcelle</label><select name="parcelle_id">
        <option value="">Toute l'exploitation</option>
        ${parcelles.map(p=>`<option value="${p.id}">${p.name}</option>`).join('')}
      </select></div>
      <div class="form-group"><label>Type *</label><select name="type" required>
        <option>engrais</option><option>pesticide</option><option>herbicide</option><option>fongicide</option><option>autre</option>
      </select></div>
      <div class="form-group"><label>Nom produit *</label><input name="name" required placeholder="Ex: NPK 20-10-10"></div>
      <div class="form-group"><label>Quantité</label><input name="quantity" type="number" step="0.1" placeholder="50"></div>
      <div class="form-group"><label>Unité</label><select name="unit"><option>kg</option><option>L</option><option>sacs</option><option>g</option></select></div>
      <div class="form-group"><label>Date application</label><input name="date_application" type="date" value="${today}"></div>
      <div class="form-group"><label>Coût (XAF)</label><input name="cost" type="number" placeholder="35000"></div>
    </div>
    <div class="form-actions"><button type="button" class="btn btn-outline" onclick="hideModal()">Annuler</button><button type="submit" class="btn btn-primary"><i class="fas fa-save"></i> Enregistrer</button></div>
  </form>`;
}

async function saveCollecte(ev, type) {
  ev.preventDefault();
  const fd = new FormData(ev.target);
  const toNum = v => v ? parseFloat(v) : null;
  const toInt = v => v ? parseInt(v) : null;

  try {
    let newItem;
    if (type === 'rendements') {
      newItem = { id: Date.now(), parcelle_id: toInt(fd.get('parcelle_id')), exploitation_id: STATE.data.parcelles.find(p=>p.id===toInt(fd.get('parcelle_id')))?.exploitation_id, date_recolte: fd.get('date_recolte'), quantity: toNum(fd.get('quantity')), unit: fd.get('unit'), crop_type: fd.get('crop_type'), quality_rating: toInt(fd.get('quality_rating')), notes: fd.get('notes') };
      if (STATE.demoMode) STATE.data.rendements.unshift(newItem);
      else await api.post('/data/rendements/', newItem);
    } else if (type === 'meteo') {
      newItem = { id: Date.now(), exploitation_id: toInt(fd.get('exploitation_id')), date_observation: fd.get('date_observation'), temperature_min: toNum(fd.get('temperature_min')), temperature_max: toNum(fd.get('temperature_max')), temperature_avg: toNum(fd.get('temperature_avg')), precipitation: toNum(fd.get('precipitation')), humidity: toInt(fd.get('humidity')), wind_speed: toNum(fd.get('wind_speed')) };
      if (STATE.demoMode) STATE.data.meteo.unshift(newItem);
      else await api.post('/data/meteo/', newItem);
    } else if (type === 'sol') {
      newItem = { id: Date.now(), parcelle_id: toInt(fd.get('parcelle_id')), exploitation_id: STATE.data.parcelles.find(p=>p.id===toInt(fd.get('parcelle_id')))?.exploitation_id, date_analyse: fd.get('date_analyse'), ph: toNum(fd.get('ph')), azote: toNum(fd.get('azote')), phosphore: toNum(fd.get('phosphore')), potassium: toNum(fd.get('potassium')), matiere_organique: toNum(fd.get('matiere_organique')), notes: fd.get('notes') };
      if (STATE.demoMode) STATE.data.sol.unshift(newItem);
      else await api.post('/data/sol/', newItem);
    } else if (type === 'intrants') {
      newItem = { id: Date.now(), exploitation_id: toInt(fd.get('exploitation_id')), parcelle_id: toInt(fd.get('parcelle_id'))||null, type: fd.get('type'), name: fd.get('name'), quantity: toNum(fd.get('quantity')), unit: fd.get('unit'), date_application: fd.get('date_application'), cost: toNum(fd.get('cost')) };
      if (STATE.demoMode) STATE.data.intrants.unshift(newItem);
      else await api.post('/data/intrants/', newItem);
    }

    if (!STATE.demoMode) await loadAllData();
    hideModal();
    toast('Données enregistrées avec succès', 'success');
    if (document.getElementById('collecte-content')) renderCollecteTab();
  } catch (err) {
    toast(err.message || 'Erreur lors de l’enregistrement', 'error');
  }
}

async function deleteCollecteItem(type, id) {
  if (!confirm('Supprimer cet enregistrement ?')) return;
  try {
    if (STATE.demoMode) {
      STATE.data[type] = STATE.data[type].filter(x=>x.id!==id);
    } else {
      const routes = {
        rendements: `/data/rendements/${id}`,
        meteo: `/data/meteo/${id}`,
        sol: `/data/sol/${id}`,
        intrants: `/data/intrants/${id}`,
      };
      await api.del(routes[type]);
      await loadAllData();
    }
    toast('Supprimé', 'success');
    renderCollecteTab();
  } catch (err) {
    toast(err.message || 'Erreur lors de la suppression', 'error');
  }
}

/* ================================================================
   PAGE: MÉTÉO
================================================================ */
function renderMeteo() {
  const data = STATE.data.meteo.slice(0, 7);
  const latest = data[0] || {};
  const avgTemp = data.length ? (data.reduce((s,m)=>s+(m.temperature_avg||0),0)/data.length).toFixed(1) : '—';
  const totalPrecip = data.reduce((s,m)=>s+(m.precipitation||0),0).toFixed(1);
  const avgHumid = data.length ? (data.reduce((s,m)=>s+(m.humidity||0),0)/data.length).toFixed(0) : '—';

  document.getElementById('content-area').innerHTML = `
    <div class="flex-between mb-15">
      <div class="page-header" style="margin-bottom:0"><h1>Météo & Climat</h1><p>Données des 7 derniers jours</p></div>
      <button class="btn btn-primary" onclick="openCollecteModal('meteo')"><i class="fas fa-plus"></i> Enregistrer météo</button>
    </div>

    <div class="meteo-cards">
      <div class="card meteo-card">
        <div class="meteo-value" style="color:var(--orange)">${latest.temperature_avg||'—'}°</div>
        <div class="meteo-unit">Min ${latest.temperature_min||'—'}° / Max ${latest.temperature_max||'—'}°</div>
        <div class="meteo-label"><i class="fas fa-thermometer-half"></i> Température</div>
      </div>
      <div class="card meteo-card">
        <div class="meteo-value" style="color:var(--blue)">${latest.precipitation||0}</div>
        <div class="meteo-unit">mm aujourd'hui / ${totalPrecip} mm cette semaine</div>
        <div class="meteo-label"><i class="fas fa-cloud-rain"></i> Précipitations</div>
      </div>
      <div class="card meteo-card">
        <div class="meteo-value" style="color:var(--primary)">${latest.humidity||'—'}%</div>
        <div class="meteo-unit">Moy. ${avgHumid}% cette semaine</div>
        <div class="meteo-label"><i class="fas fa-tint"></i> Humidité</div>
      </div>
      <div class="card meteo-card">
        <div class="meteo-value" style="color:var(--text-2)">${latest.wind_speed||'—'}</div>
        <div class="meteo-unit">km/h</div>
        <div class="meteo-label"><i class="fas fa-wind"></i> Vent</div>
      </div>
    </div>

    <div class="charts-row">
      <div class="card"><div class="card-header"><h3>Températures (7 jours)</h3></div><canvas id="chart-temp" height="100"></canvas></div>
      <div class="card"><div class="card-header"><h3>Précipitations (7 jours)</h3></div><canvas id="chart-precip" height="100"></canvas></div>
    </div>

    <div class="card">
      <div class="card-header"><h3>Historique météo</h3></div>
      <div class="table-wrap"><table>
        <thead><tr><th>Date</th><th>Exploitation</th><th>Temp. moy.</th><th>Min</th><th>Max</th><th>Précip.</th><th>Humidité</th></tr></thead>
        <tbody>${data.length ? data.map(m=>{
          const e=STATE.data.exploitations.find(x=>x.id===m.exploitation_id);
          return `<tr><td>${formatDate(m.date_observation)}</td><td>${e?e.name:'—'}</td>
          <td><strong>${m.temperature_avg||'—'}°C</strong></td><td class="text-muted">${m.temperature_min||'—'}°</td><td class="text-muted">${m.temperature_max||'—'}°</td>
          <td><span class="badge badge-blue">${m.precipitation||0} mm</span></td><td>${m.humidity||'—'}%</td></tr>`;
        }).join('') : '<tr><td colspan="7" style="text-align:center;padding:2rem;color:var(--text-3)">Aucune donnée météo</td></tr>'}
        </tbody>
      </table></div>
    </div>`;

  const labels = data.map(m => formatDate(m.date_observation)).reverse();
  mkChart('chart-temp', {
    type: 'line',
    data: {
      labels,
      datasets: [
        { label: 'Max', data: data.map(m=>m.temperature_max).reverse(), borderColor: '#e8813c', tension: 0.4, pointRadius: 3 },
        { label: 'Moy', data: data.map(m=>m.temperature_avg).reverse(), borderColor: '#1f6f43', tension: 0.4, pointRadius: 3, backgroundColor: 'rgba(31,111,67,0.06)', fill: true },
        { label: 'Min', data: data.map(m=>m.temperature_min).reverse(), borderColor: '#3a8fd6', tension: 0.4, pointRadius: 3 },
      ],
    },
    options: { responsive: true, scales: { y: { grid: { color: '#e8f0eb' } }, x: { grid: { display: false } } }, plugins: { legend: { labels: { font: { size: 11 } } } } },
  });
  mkChart('chart-precip', {
    type: 'bar',
    data: { labels, datasets: [{ label: 'Précipitations (mm)', data: data.map(m=>m.precipitation||0).reverse(), backgroundColor: 'rgba(58,143,214,0.7)', borderRadius: 6 }] },
    options: { responsive: true, scales: { y: { beginAtZero: true, grid: { color: '#e8f0eb' } }, x: { grid: { display: false } } }, plugins: { legend: { display: false } } },
  });
}

/* ================================================================
   PAGE: ANALYSES
================================================================ */
function renderAnalyses() {
  const rends = STATE.data.rendements;
  const intrants = STATE.data.intrants;
  const totalCost = intrants.reduce((s,i)=>s+(i.cost||0),0);
  const avgYield = rends.length ? (rends.reduce((s,r)=>s+r.quantity,0)/rends.length).toFixed(0) : 0;

  // By parcelle
  const parcelleData = {};
  rends.forEach(r => {
    const p = STATE.data.parcelles.find(x=>x.id===r.parcelle_id);
    const key = p ? p.name : `#${r.parcelle_id}`;
    parcelleData[key] = (parcelleData[key]||0) + r.quantity;
  });

  // By crop
  const cropData = {};
  rends.forEach(r => { const k = r.crop_type||'Autre'; cropData[k] = (cropData[k]||0) + r.quantity; });

  document.getElementById('content-area').innerHTML = `
    <div class="page-header"><h1>Analyses & Statistiques</h1><p>Vue d'ensemble de vos performances agricoles</p></div>

    <div class="stats-grid mb-15">
      <div class="stat-card">
        <div class="stat-icon green"><i class="fas fa-chart-line"></i></div>
        <div class="stat-info"><div class="stat-value">${rends.length}</div><div class="stat-label">Collectes totales</div></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon blue"><i class="fas fa-balance-scale"></i></div>
        <div class="stat-info"><div class="stat-value">${avgYield} <small style="font-size:.9rem">kg</small></div><div class="stat-label">Rendement moyen</div></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon orange"><i class="fas fa-boxes"></i></div>
        <div class="stat-info"><div class="stat-value">${intrants.length}</div><div class="stat-label">Intrants utilisés</div></div>
      </div>
      <div class="stat-card">
        <div class="stat-icon purple"><i class="fas fa-money-bill"></i></div>
        <div class="stat-info"><div class="stat-value" style="font-size:1.3rem">${(totalCost/1000).toFixed(0)}k</div><div class="stat-label">Coût intrants (XAF)</div></div>
      </div>
    </div>

    <div class="charts-row">
      <div class="card"><div class="card-header"><h3>Rendements par parcelle</h3></div><canvas id="chart-by-parcelle" height="120"></canvas></div>
      <div class="card"><div class="card-header"><h3>Rendement par culture</h3></div><canvas id="chart-by-crop" height="120"></canvas></div>
    </div>

    <div class="card">
      <div class="card-header"><h3>Coûts intrants par type</h3></div>
      <canvas id="chart-intrants-cost" height="70"></canvas>
    </div>
  `;

  const parcKeys = Object.keys(parcelleData);
  mkChart('chart-by-parcelle', {
    type: 'bar',
    data: { labels: parcKeys, datasets: [{ label: 'Kg total', data: parcKeys.map(k=>parcelleData[k]), backgroundColor: parcKeys.map((_,i)=>['#1f6f43','#d4e65c','#3a8fd6','#e8813c','#8b5cf6','#e05252'][i%6]), borderRadius: 8 }] },
    options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, grid: { color: '#e8f0eb' } }, x: { grid: { display: false } } } },
  });

  const cropKeys = Object.keys(cropData);
  mkChart('chart-by-crop', {
    type: 'polarArea',
    data: { labels: cropKeys, datasets: [{ data: cropKeys.map(k=>cropData[k]), backgroundColor: ['#1f6f43','#d4e65c','#3a8fd6','#e8813c','#8b5cf6'].map(c=>c+'cc') }] },
    options: { responsive: true, plugins: { legend: { position: 'bottom', labels: { font: { size: 11 } } } } },
  });

  const typeCosts = {};
  intrants.forEach(i => { typeCosts[i.type] = (typeCosts[i.type]||0) + (i.cost||0); });
  const typeKeys = Object.keys(typeCosts);
  mkChart('chart-intrants-cost', {
    type: 'bar',
    data: { labels: typeKeys, datasets: [{ label: 'Coût XAF', data: typeKeys.map(k=>typeCosts[k]), backgroundColor: ['#1f6f43','#e8813c','#e05252','#8b5cf6'], borderRadius: 8 }] },
    options: { indexAxis: 'y', responsive: true, plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true, grid: { color: '#e8f0eb' } }, y: { grid: { display: false } } } },
  });
}

/* ================================================================
   PAGE: ALERTES
================================================================ */
function renderAlertes() {
  const alertes = STATE.data.alertes;
  const unread = alertes.filter(a=>!a.is_read);
  const read = alertes.filter(a=>a.is_read);
  const severityConf = {
    critical: { color: 'badge-red',    icon: 'fa-circle-exclamation', bg: 'rgba(224,82,82,0.1)',    iconColor: 'var(--red)' },
    warning:  { color: 'badge-orange', icon: 'fa-triangle-exclamation', bg: 'rgba(232,129,60,0.1)', iconColor: 'var(--orange)' },
    info:     { color: 'badge-blue',   icon: 'fa-circle-info',        bg: 'rgba(58,143,214,0.1)',   iconColor: 'var(--blue)' },
  };

  function renderAlertItem(a) {
    const c = severityConf[a.severity] || severityConf.info;
    return `<div class="alert-item ${!a.is_read?'unread':''}" id="alert-${a.id}">
      <div class="alert-icon" style="background:${c.bg}"><i class="fas ${c.icon}" style="color:${c.iconColor}"></i></div>
      <div class="alert-content">
        <div class="alert-title">${a.title}</div>
        <div class="alert-desc">${a.description}</div>
        <div class="alert-time"><i class="fas fa-clock" style="margin-right:4px"></i>${formatDateTime(a.created_at)} — ${STATE.data.exploitations.find(e=>e.id===a.exploitation_id)?.name||'—'}</div>
      </div>
      <div style="display:flex;flex-direction:column;gap:6px;align-items:flex-end;flex-shrink:0">
        <span class="badge ${c.color}">${a.severity}</span>
        ${!a.is_read ? `<button class="btn btn-xs btn-outline" onclick="markAlertRead(${a.id})">Lu <i class="fas fa-check"></i></button>` : '<span class="text-xs text-muted"><i class="fas fa-check-double"></i> Lu</span>'}
      </div>
      ${!a.is_read ? '<div class="unread-dot"></div>' : ''}
    </div>`;
  }

  document.getElementById('content-area').innerHTML = `
    <div class="flex-between mb-15">
      <div class="page-header" style="margin-bottom:0"><h1>Alertes</h1><p>${unread.length} non lue${unread.length>1?'s':''} · ${alertes.length} au total</p></div>
      ${unread.length ? `<button class="btn btn-outline" onclick="markAllRead()"><i class="fas fa-check-double"></i> Tout marquer lu</button>` : ''}
    </div>

    ${unread.length ? `
    <div class="card mb-1">
      <div class="card-header"><h3 style="color:var(--red)"><i class="fas fa-bell" style="margin-right:6px"></i>Non lues (${unread.length})</h3></div>
      ${unread.map(renderAlertItem).join('')}
    </div>` : ''}

    <div class="card">
      <div class="card-header"><h3><i class="fas fa-history" style="margin-right:6px"></i>Toutes les alertes</h3></div>
      ${alertes.length ? alertes.map(renderAlertItem).join('') : '<div class="empty-state"><div class="empty-icon"><i class="fas fa-bell-slash"></i></div><p>Aucune alerte</p></div>'}
    </div>`;
}

function markAlertRead(id) {
  const a = STATE.data.alertes.find(x=>x.id===id);
  if (a) { a.is_read = true; }
  updateAlertBadge();
  renderAlertes();
  toast('Alerte marquée comme lue', 'success');
}
function markAllRead() {
  STATE.data.alertes.forEach(a => a.is_read = true);
  updateAlertBadge();
  renderAlertes();
  toast('Toutes les alertes marquées comme lues', 'success');
}

/* ================================================================
   PAGE: RAPPORTS
================================================================ */
function renderRapports() {
  const types = [
    { icon: 'fa-chart-bar', title: 'Rapport Mensuel', desc: 'Synthèse des rendements, météo et intrants du mois en cours', color: 'var(--primary)' },
    { icon: 'fa-calendar-alt', title: 'Rapport Annuel', desc: 'Bilan complet de la saison agricole avec comparaisons', color: 'var(--blue)' },
    { icon: 'fa-seedling', title: 'Rapport par Culture', desc: 'Performance détaillée par type de culture', color: 'var(--orange)' },
    { icon: 'fa-tractor', title: 'Rapport Exploitation', desc: 'Analyse complète par exploitation avec cartographie', color: 'var(--purple)' },
    { icon: 'fa-vial', title: 'Rapport Sol', desc: 'Historique des analyses et recommandations d\'amendement', color: 'var(--red)' },
    { icon: 'fa-file-export', title: 'Export données brutes', desc: 'Téléchargement CSV de toutes les données', color: 'var(--text-2)' },
  ];

  document.getElementById('content-area').innerHTML = `
    <div class="page-header"><h1>Rapports</h1><p>Générez et téléchargez vos rapports agricoles</p></div>
    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:1.2rem">
      ${types.map(t => `
        <div class="rapport-item" onclick="generateRapport('${t.title}')">
          <div class="rapport-icon" style="background:${t.color}18;color:${t.color}"><i class="fas ${t.icon}"></i></div>
          <div class="rapport-info">
            <div class="rapport-name">${t.title}</div>
            <div class="rapport-desc">${t.desc}</div>
          </div>
          <i class="fas fa-chevron-right text-muted"></i>
        </div>`).join('')}
    </div>

    <div class="card mt-1">
      <div class="card-header"><h3><i class="fas fa-history" style="margin-right:6px"></i>Rapports récents</h3></div>
      <div class="empty-state" style="padding:2rem">
        <div class="empty-icon" style="font-size:2rem"><i class="fas fa-file-alt"></i></div>
        <p>Aucun rapport généré pour le moment.<br>Cliquez sur un type de rapport ci-dessus pour commencer.</p>
      </div>
    </div>`;
}

function generateRapport(title) {
  toast(`Génération du "${title}" en cours...`, 'success');
  setTimeout(() => {
    const csvData = [
      ['Date','Culture','Parcelle','Quantité','Unité'],
      ...STATE.data.rendements.map(r => {
        const p = STATE.data.parcelles.find(x=>x.id===r.parcelle_id);
        return [r.date_recolte, r.crop_type||'—', p?.name||r.parcelle_id, r.quantity, r.unit];
      })
    ];
    if (title === 'Export données brutes') downloadCSV(csvData, 'agridata_export.csv');
    else toast(`Rapport "${title}" généré ! (fonctionnalité complète à connecter au backend)`, 'success');
  }, 800);
}

function downloadCSV(rows, filename) {
  const csv = rows.map(r => r.join(',')).join('\n');
  const blob = new Blob([csv], { type: 'text/csv' });
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob); a.download = filename; a.click();
  toast('Export CSV téléchargé', 'success');
}

/* ================================================================
   PAGE: PROFIL
================================================================ */
function showProfileModal() {
  const u = STATE.user;
  const initials = `${u.first_name?.[0]||''}${u.last_name?.[0]||''}`.toUpperCase();
  const roleLabel = { admin: 'Administrateur', consultant: 'Consultant', agriculteur: 'Agriculteur' }[u.role]||u.role;
  showModal('Mon profil', `
    <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1.5rem">
      <div class="avatar avatar-lg" style="width:56px;height:56px;font-size:1.3rem">${initials}</div>
      <div><div style="font-size:1.1rem;font-weight:700">${u.first_name} ${u.last_name}</div><div class="text-muted text-sm">${u.email}</div><span class="badge badge-green" style="margin-top:4px">${roleLabel}</span></div>
    </div>
    <div class="profile-section">
      <h4>Informations du compte</h4>
      <div class="form-grid" style="grid-template-columns:1fr 1fr;gap:.7rem">
        ${infoRow('Prénom',u.first_name)} ${infoRow('Nom',u.last_name)}
        ${infoRow('Email',u.email)} ${infoRow('Rôle',roleLabel)}
        ${infoRow('ID Organisation',u.tenant_id)} ${infoRow('Mode',STATE.demoMode?'Démonstration':'Production')}
      </div>
    </div>
    <div class="form-actions">
      <button class="btn btn-outline" onclick="hideModal()">Fermer</button>
      <button class="btn btn-danger" onclick="logout()"><i class="fas fa-sign-out-alt"></i> Déconnexion</button>
    </div>
  `);
}
function renderProfil() { showProfileModal(); showPage('dashboard'); }

/* ================================================================
   MODAL
================================================================ */
function showModal(title, content, large=false) {
  document.getElementById('modal-title').textContent = title;
  document.getElementById('modal-body').innerHTML = content;
  document.getElementById('modal-box').className = `modal-box${large?' modal-lg':''}`;
  document.getElementById('modal-overlay').classList.add('open');
}
function hideModal() {
  document.getElementById('modal-overlay').classList.remove('open');
}
document.getElementById('modal-overlay').addEventListener('click', function(e) {
  if (e.target === this) hideModal();
});

/* ================================================================
   TOAST
================================================================ */
function toast(msg, type='info') {
  const c = document.getElementById('toast-container');
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  const icons = { success: 'fa-check-circle', error: 'fa-times-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
  t.innerHTML = `<i class="fas ${icons[type]||'fa-info-circle'}"></i>${msg}`;
  c.appendChild(t);
  setTimeout(() => { t.style.animation = 'none'; t.style.opacity = '0'; t.style.transform = 'translateX(100%)'; t.style.transition = 'all .3s'; setTimeout(()=>t.remove(), 320); }, 3000);
}

/* ================================================================
   HELPERS
================================================================ */
function formatDate(d) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' });
}
function formatDateTime(d) {
  if (!d) return '—';
  return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' });
}

/* ================================================================
   START
================================================================ */
document.addEventListener('DOMContentLoaded', init);
