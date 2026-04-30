// Vérifier le token
const token = localStorage.getItem('access_token');
if (!token) {
    window.location.href = '/pages/login.html';
}

const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
};

// Variables globales pour les graphiques
let weatherChart, soilChart;
let exploitations = [];

// Initialisation
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    fetchDashboardData();
    // Rafraîchir toutes les 10 secondes
    setInterval(fetchDashboardData, 10000);

    // Navigation
    document.getElementById('addDataBtn').addEventListener('click', toggleDataForm);
    document.getElementById('logoutBtn').addEventListener('click', logout);

    // Formulaire d'ajout
    document.getElementById('dataForm').addEventListener('submit', submitData);
    document.getElementById('dataType').addEventListener('change', toggleFields);
    document.getElementById('dataExploitation').addEventListener('change', (e) => {
        const selectedId = parseInt(e.target.value, 10);
        if (selectedId) {
            loadParcellesForExploitation(selectedId);
        }
    });
});

function initCharts() {
    const weatherCtx = document.getElementById('weatherChart').getContext('2d');
    weatherChart = new Chart(weatherCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'Température (°C)',
                    data: [],
                    borderColor: 'rgb(255, 99, 132)',
                    backgroundColor: 'rgba(255, 99, 132, 0.2)',
                    tension: 0.3
                },
                {
                    label: 'Humidité (%)',
                    data: [],
                    borderColor: 'rgb(54, 162, 235)',
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    tension: 0.3
                }
            ]
        }
    });

    const soilCtx = document.getElementById('soilChart').getContext('2d');
    soilChart = new Chart(soilCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [
                {
                    label: 'pH',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    backgroundColor: 'rgba(75, 192, 192, 0.2)',
                    tension: 0.3
                },
                {
                    label: 'Humidité sol (%)',
                    data: [],
                    borderColor: 'rgb(153, 102, 255)',
                    backgroundColor: 'rgba(153, 102, 255, 0.2)',
                    tension: 0.3
                }
            ]
        }
    });
}

async function fetchDashboardData() {
    console.log('Chargement des données du dashboard...');
    try {
        const [meRes, dashboardRes, weatherRes, soilRes] = await Promise.all([
            fetch('/api/auth/me', { headers }),
            fetch('/api/analytics/dashboard', { headers }),
            fetch('/api/analytics/weather', { headers }),
            fetch('/api/analytics/soil', { headers }),
        ]);

        console.log('Réponse /api/auth/me:', meRes.status, meRes.ok);
        console.log('Réponse /api/analytics/dashboard:', dashboardRes.status, dashboardRes.ok);
        console.log('Réponse /api/analytics/weather:', weatherRes.status, weatherRes.ok);
        console.log('Réponse /api/analytics/soil:', soilRes.status, soilRes.ok);

        if (!meRes.ok || !dashboardRes.ok) {
            throw new Error('Impossible de charger le dashboard');
        }

        const user = await meRes.json();
        const dashboardData = await dashboardRes.json();
        console.log('Utilisateur:', user);
        console.log('Données dashboard:', dashboardData);
        renderUserHeader(user);
        renderDashboardSummary(dashboardData);
        populateExploitationOptions(dashboardData.exploitations || []);

        if (weatherRes.ok) {
            const weatherData = await weatherRes.json();
            updateWeatherChart(weatherData);
            updateSummaryCards(weatherData);
        }
        if (soilRes.ok) {
            const soilData = await soilRes.json();
            updateSoilChart(soilData);
        }
    } catch (error) {
        console.error('Erreur de chargement des données:', error);
        if (error.message && error.message.includes('Impossible de charger le dashboard')) {
            window.location.href = '/pages/login.html';
        }
    }
}

function renderUserHeader(user) {
    const title = document.querySelector('main h1');
    if (title) {
        title.textContent = `Bienvenue ${user.first_name || user.email}`;
    }
}

function renderDashboardSummary(data) {
    const summary = data.summary || {};
    document.getElementById('currentTemp').textContent = `${summary.total_exploitations ?? '--'}`;
    document.getElementById('currentHumidity').textContent = `${summary.total_parcelles ?? '--'}`;
    document.getElementById('avgPh').textContent = `${summary.total_rendements ?? '--'}`;
}

function updateWeatherChart(data) {
    // Supposons data = [{timestamp, temperature, humidity}, ...]
    const labels = data.map(d => new Date(d.timestamp).toLocaleTimeString());
    weatherChart.data.labels = labels;
    weatherChart.data.datasets[0].data = data.map(d => d.temperature);
    weatherChart.data.datasets[1].data = data.map(d => d.humidity);
    weatherChart.update();
}

function updateSoilChart(data) {
    // data = [{timestamp, ph, moisture}, ...]
    soilChart.data.labels = data.map(d => new Date(d.timestamp).toLocaleTimeString());
    soilChart.data.datasets[0].data = data.map(d => d.ph);
    soilChart.data.datasets[1].data = data.map(d => d.moisture);
    soilChart.update();
}

function updateSummaryCards(weatherData) {
    if (weatherData.length > 0) {
        const last = weatherData[weatherData.length - 1];
        document.getElementById('currentTemp').textContent = last.temperature_avg ? last.temperature_avg.toFixed(1) + ' °C' : '-- °C';
        document.getElementById('currentHumidity').textContent = last.humidity ? last.humidity.toFixed(1) + ' %' : '-- %';
    }
    // Pour le pH moyen, on pourrait faire un appel supplémentaire ou le stocker dans le state
    // Ici on le laisse dynamique via l'API soil.
}

async function submitData(e) {
    e.preventDefault();
    const type = document.getElementById('dataType').value;
    let payload = { type };
    const exploitationId = parseInt(document.getElementById('dataExploitation').value, 10);
    const parcelleId = parseInt(document.getElementById('dataParcelle').value, 10);

    if (type === 'weather') {
        if (!exploitationId) {
            alert('Sélectionnez une exploitation avant d’ajouter des données météo.');
            return;
        }
        payload.temperature = parseFloat(document.getElementById('temperature').value);
        payload.humidity = parseFloat(document.getElementById('humidity').value);
        payload.exploitation_id = exploitationId;
    } else {
        if (!parcelleId) {
            alert('Sélectionnez une parcelle avant d’ajouter des données sol.');
            return;
        }
        payload.ph = parseFloat(document.getElementById('ph').value);
        payload.moisture = parseFloat(document.getElementById('soilMoisture').value);
        payload.parcelle_id = parcelleId;
    }

    try {
        const endpoint = type === 'weather' ? '/api/data/meteo/' : '/api/data/sol/';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers,
            body: JSON.stringify(payload)
        });
        if (!response.ok) throw new Error('Échec de l\'enregistrement');
        alert('Données ajoutées avec succès');
        document.getElementById('dataForm').reset();
        fetchDashboardData(); // rafraîchir immédiatement
    } catch (err) {
        alert(err.message);
    }
}

function toggleDataForm() {
    const section = document.getElementById('dataFormSection');
    section.classList.toggle('hidden');
    // Mettre à jour le style du lien sidebar
    this.classList.toggle('bg-green-700');
}

function toggleFields() {
    const type = document.getElementById('dataType').value;
    document.getElementById('weatherFields').classList.toggle('hidden', type !== 'weather');
    document.getElementById('soilFields').classList.toggle('hidden', type !== 'soil');
    document.getElementById('parcelleSelectWrapper').classList.toggle('hidden', type !== 'soil');
}

function populateExploitationOptions(options) {
    exploitations = options;
    const select = document.getElementById('dataExploitation');
    const parcelleSelect = document.getElementById('dataParcelle');
    if (!select) return;
    select.innerHTML = '<option value="">Choisissez une exploitation</option>' +
        options.map(ex => `<option value="${ex.id}">${ex.name || 'Exploitation #' + ex.id}</option>`).join('');
    if (parcelleSelect) {
        parcelleSelect.innerHTML = '<option value="">Choisissez une parcelle</option>';
    }
}

async function loadParcellesForExploitation(exploitationId) {
    const parcelleSelect = document.getElementById('dataParcelle');
    if (!parcelleSelect) return;
    parcelleSelect.innerHTML = '<option value="">Chargement...</option>';
    try {
        const res = await fetch(`/api/parcelles?exploitation_id=${exploitationId}`, { headers });
        if (!res.ok) throw new Error('Impossible de charger les parcelles');
        const data = await res.json();
        parcelleSelect.innerHTML = '<option value="">Choisissez une parcelle</option>' +
            (data.data || data).map(p => `<option value="${p.id}">${p.name || ('Parcelle #' + p.id)}</option>`).join('');
    } catch (err) {
        parcelleSelect.innerHTML = '<option value="">Erreur de chargement</option>';
        console.error(err);
    }
}

function logout() {
    localStorage.removeItem('access_token');
        window.location.href = '/';
}