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

async function loadParcelles(exploitationId) {
    const select = document.getElementById('parcelleSelect');
    if (!exploitationId) {
        select.innerHTML = '<option value="">Choisissez une exploitation</option>';
        return;
    }
    select.innerHTML = '<option value="">Chargement...</option>';
    try {
        const res = await fetch(`/api/parcelles?exploitation_id=${exploitationId}`, { headers });
        if (!res.ok) throw new Error('Impossible de charger les parcelles');
        const data = await res.json();
        select.innerHTML = '<option value="">Choisissez une parcelle</option>' +
            (data.data || data).map(p => `<option value="${p.id}">${p.name || 'Parcelle #' + p.id}</option>`).join('');
    } catch (err) {
        select.innerHTML = '<option value="">Erreur de chargement</option>';
        console.error(err);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadExploitations();
    document.getElementById('exploitationSelect').addEventListener('change', (e) => {
        const explId = parseInt(e.target.value, 10);
        loadParcelles(explId);
    });
    document.getElementById('soilForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const parcelleId = parseInt(document.getElementById('parcelleSelect').value, 10);
        const ph = parseFloat(document.getElementById('ph').value);
        const moisture = parseFloat(document.getElementById('soilMoisture').value);
        const errorDiv = document.getElementById('errorMessage');
        errorDiv.classList.add('hidden');

        if (!parcelleId) {
            errorDiv.textContent = 'Veuillez sélectionner une parcelle.';
            errorDiv.classList.remove('hidden');
            return;
        }

        try {
            const res = await fetch('/api/data/sol/', {
                method: 'POST',
                headers,
                body: JSON.stringify({ parcelle_id: parcelleId, ph, moisture })
            });
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Erreur lors de l’enregistrement');
            }
            alert('Données sol ajoutées avec succès.');
            window.location.href = '/pages/dashboard.html';
        } catch (err) {
            errorDiv.textContent = err.message;
            errorDiv.classList.remove('hidden');
        }
    });
});
