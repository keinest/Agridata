document.getElementById('loginForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.classList.add('hidden');

    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tenant_id: 1,
                email,
                password,
            })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Identifiants invalides');
        }

        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        alert('Connexion réussie, redirection vers le dashboard...');
        window.location.href = '/pages/dashboard.html';
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.classList.remove('hidden');
    }
});