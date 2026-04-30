const token = localStorage.getItem('access_token');
if (!token) {
    window.location.href = '/pages/login.html';
}

const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
};

async function loadExploitations() {
    const select = document.getElementById('exploitationSelect');
    try {
        const res = await fetch('/api/exploitations', { headers });
        if (!res.ok) throw new Error('Impossible de charger les exploitations');
        const data = await res.json();
        select.innerHTML = '<option value="">Choisissez une exploitation</option>' +
            data.map(ex => `<option value="${ex.id}">${ex.name || 'Exploitation #' + ex.id}</option>`).join('');
    } catch (err) {
        select.innerHTML = '<option value="">Erreur de chargement</option>';
        console.error(err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadExploitations();
    document.getElementById('weatherForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const explId = parseInt(document.getElementById('exploitationSelect').value, 10);
        const temp = parseFloat(document.getElementById('temperature').value);
        const humidity = parseFloat(document.getElementById('humidity').value);
        const errorDiv = document.getElementById('errorMessage');
        errorDiv.classList.add('hidden');

        if (!explId) {
            errorDiv.textContent = 'Veuillez sélectionner une exploitation.';
            errorDiv.classList.remove('hidden');
            return;
        }

        try {
            const res = await fetch('/api/data/meteo/', {
                method: 'POST',
                headers,
                body: JSON.stringify({ exploitation_id: explId, temperature: temp, humidity })
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Erreur lors de l’enregistrement');
            }
            alert('Données météo ajoutées avec succès.');
            window.location.href = '/pages/dashboard.html';
        } catch (err) {
            errorDiv.textContent = err.message;
            errorDiv.classList.remove('hidden');
        }
    });
});
