// Vérifier le token
const token = localStorage.getItem('access_token');
if (!token) {
    window.location.href = 'login.html';
}

const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
};

// Variables globales pour les graphiques
let weatherChart, soilChart;

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
    try {
        const [weatherRes, soilRes] = await Promise.all([
            fetch('/api/analytics/weather?hours=24', { headers }),
            fetch('/api/analytics/soil?hours=24', { headers })
        ]);

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
    }
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
        document.getElementById('currentTemp').textContent = last.temperature.toFixed(1) + ' °C';
        document.getElementById('currentHumidity').textContent = last.humidity.toFixed(1) + ' %';
    }
    // Pour le pH moyen, on pourrait faire un appel supplémentaire ou le stocker dans le state
    // Ici on le laisse dynamique via l'API soil.
}

async function submitData(e) {
    e.preventDefault();
    const type = document.getElementById('dataType').value;
    let payload = { type };

    if (type === 'weather') {
        payload.temperature = parseFloat(document.getElementById('temperature').value);
        payload.humidity = parseFloat(document.getElementById('humidity').value);
    } else {
        payload.ph = parseFloat(document.getElementById('ph').value);
        payload.moisture = parseFloat(document.getElementById('soilMoisture').value);
    }

    try {
        const response = await fetch(`/api/data-collection/${type}`, {
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
}

function logout() {
    localStorage.removeItem('access_token');
    window.location.href = 'login.html';
}