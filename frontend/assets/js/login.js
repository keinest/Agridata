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
            body: JSON.stringify({ email, password })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Identifiants invalides');
        }

        const data = await response.json();
        localStorage.setItem('access_token', data.access_token);
        window.location.href = 'dashboard.html';
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.classList.remove('hidden');
    }
});