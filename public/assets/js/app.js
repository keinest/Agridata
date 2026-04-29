const API_HOST = (function() {
  const localHosts = ['localhost', '127.0.0.1', '0.0.0.0'];
  if (window.location.protocol === 'file:' || window.location.origin === 'null' || window.location.hostname === '' || localHosts.includes(window.location.hostname)) {
    return 'http://localhost:8000';
  }
  return window.location.origin;
})();

const CFG = {
  API: `${API_HOST}/api`,
  TOKEN_KEY: 'agridata_token',
  USER_KEY: 'agridata_user',
};

async function apiRequest(path, options = {}) {
    const opts = {
        method: options.method || 'GET',
        headers: { 'Content-Type': 'application/json' },
    };
    if (options.token) {
        opts.headers.Authorization = `Bearer ${options.token}`;
    }
    if (options.body) opts.body = JSON.stringify(options.body);
    const response = await fetch(`${CFG.API}${path}`, opts);
    const payload = await response.json().catch(() => null);
    if (!response.ok) {
        const message = payload?.detail || payload?.message || response.statusText || 'Erreur de communication';
        throw new Error(message);
    }
    return payload;
}

async function authMe(token) {
    return await apiRequest('/auth/me', { token });
}

async function loginUser(email, password) {
    const payload = await apiRequest('/auth/login', {
        method: 'POST',
        body: { tenant_id: 1, email, password },
    });
    if (!payload?.access_token) {
        throw new Error('Réponse de connexion invalide');
    }
    localStorage.setItem(CFG.TOKEN_KEY, payload.access_token);
    const user = await authMe(payload.access_token);
    if (user) {
        localStorage.setItem(CFG.USER_KEY, JSON.stringify(user));
    }
    return user;
}

async function registerUser(fullName, email, password) {
    const parts = fullName.trim().split(/\s+/);
    const first_name = parts.shift() || fullName.trim();
    const last_name = parts.join(' ') || '';
    const payload = await apiRequest('/auth/register', {
        method: 'POST',
        body: { tenant_id: 1, email, password, first_name, last_name },
    });
    if (!payload?.access_token) {
        throw new Error('Réponse d\'inscription invalide');
    }
    localStorage.setItem(CFG.TOKEN_KEY, payload.access_token);
    const user = await authMe(payload.access_token);
    if (user) {
        localStorage.setItem(CFG.USER_KEY, JSON.stringify(user));
    }
    return user;
}

function showPage(pageId) 
{
    const pages = document.querySelectorAll('.page');
    pages.forEach(page => {
        page.classList.add('hidden');
    });
    const activePage = document.getElementById(pageId);
    if (activePage) {
        activePage.classList.remove('hidden');
    }
    // Nettoyer les messages des formulaires lors d'un changement de page
    const loginMsg = document.getElementById('loginMsg');
    const regMsg = document.getElementById('regMsg');
    if (loginMsg) { loginMsg.innerHTML = ''; loginMsg.className = 'msg'; }
    if (regMsg) { regMsg.innerHTML = ''; regMsg.className = 'msg'; }
    // reset formulaires si besoin
    if (pageId === 'loginPage') {
        const formLogin = document.getElementById('loginForm');
        if (formLogin) formLogin.reset();
    } else if (pageId === 'registerPage') {
        const formReg = document.getElementById('registerForm');
        if (formReg) formReg.reset();
    }
}

const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const email = document.getElementById('email').value.trim();
        const pwd = document.getElementById('password').value.trim();
        const msgDiv = document.getElementById('loginMsg');

        if (email === '' || pwd === '') {
            msgDiv.innerHTML = '<i class="fas fa-times-circle"></i> Veuillez remplir tous les champs.';
            msgDiv.className = 'msg msg-error';
            return;
        }
        if (!email.includes('@') || !email.includes('.')) {
            msgDiv.innerHTML = '<i class="fas fa-envelope-open-text"></i> Format d\'email invalide.';
            msgDiv.className = 'msg msg-error';
            return;
        }

        msgDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Vérification de vos informations...';
        msgDiv.className = 'msg msg-info';

        try {
            await loginUser(email, pwd);
            msgDiv.innerHTML = '<i class="fas fa-check-circle"></i> Connexion réussie ! Redirection vers le tableau de bord.';
            msgDiv.className = 'msg msg-success';
            setTimeout(() => { window.location.href = 'dashboard.html'; }, 900);
        } catch (err) {
            if (err.message && err.message.toLowerCase().includes('failed to fetch')) {
                msgDiv.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Backend inaccessible. Connexion en mode démo.';
                msgDiv.className = 'msg msg-warning';
                localStorage.setItem(CFG.TOKEN_KEY, 'demo-token');
                window.location.href = 'dashboard.html';
            } else {
                msgDiv.innerHTML = `<i class="fas fa-times-circle"></i> ${err.message}`;
                msgDiv.className = 'msg msg-error';
            }
        }
    });
}

const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('regEmail').value.trim();
        const pwd = document.getElementById('regPassword').value.trim();
        const msgDiv = document.getElementById('regMsg');

        if (name === '' || email === '' || pwd === '') {
            msgDiv.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Tous les champs sont obligatoires.';
            msgDiv.className = 'msg msg-error';
            return;
        }
        if (name.length < 2) {
            msgDiv.innerHTML = '<i class="fas fa-user-slash"></i> Nom complet trop court.';
            msgDiv.className = 'msg msg-error';
            return;
        }
        if (!email.includes('@') || email.length < 5) {
            msgDiv.innerHTML = '<i class="fas fa-at"></i> Email invalide (exemple: nom@domaine.fr)';
            msgDiv.className = 'msg msg-error';
            return;
        }
        if (pwd.length < 4) {
            msgDiv.innerHTML = '<i class="fas fa-lock"></i> Le mot de passe doit contenir au moins 4 caractères.';
            msgDiv.className = 'msg msg-error';
            return;
        }

        msgDiv.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Création de votre compte...';
        msgDiv.className = 'msg msg-info';

        try {
            await registerUser(name, email, pwd);
            msgDiv.innerHTML = `<i class="fas fa-check-double"></i> Compte créé avec succès ! Redirection vers le tableau de bord...`;
            msgDiv.className = 'msg msg-success';
            setTimeout(() => { window.location.href = 'dashboard.html'; }, 900);
        } catch (err) {
            if (err.message && err.message.toLowerCase().includes('failed to fetch')) {
                msgDiv.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Backend inaccessible. Inscription impossible pour le moment.';
                msgDiv.className = 'msg msg-error';
            } else {
                msgDiv.innerHTML = `<i class="fas fa-times-circle"></i> ${err.message}`;
                msgDiv.className = 'msg msg-error';
            }
        }
    });
}

window.addEventListener('DOMContentLoaded', () => {
    const existingToken = localStorage.getItem(CFG.TOKEN_KEY);
    if (existingToken) {
        window.location.href = 'dashboard.html';
        return;
    }
    showPage('landingPage');
    const allBtns = document.querySelectorAll('button');
    allBtns.forEach(btn => {
        if (!btn.classList.contains('no-effect')) {
            btn.style.cursor = 'pointer';
        }
    });
});
