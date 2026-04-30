document.getElementById('registerForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    const name = document.getElementById('name').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const errorDiv = document.getElementById('errorMessage');
    errorDiv.classList.add('hidden');

    if (password !== confirmPassword) {
        errorDiv.textContent = "Les mots de passe ne correspondent pas.";
        errorDiv.classList.remove('hidden');
        return;
    }

    try {
        const response = await fetch('/api/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Erreur lors de l'inscription");
        }

        alert('Compte créé avec succès ! Vous pouvez vous connecter.');
        window.location.href = 'login.html';
    } catch (error) {
        errorDiv.textContent = error.message;
        errorDiv.classList.remove('hidden');
    }
});