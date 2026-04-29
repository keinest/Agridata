# AgriData Platform

Application agricole full-stack avec :

- un backend `FastAPI` dans `backend/`
- une entrée Vercel Python dans `api/`
- un frontend statique prêt pour Vercel dans `public/`

## Structure utile

```text
project/
├── api/index.py                 # Entrée Vercel pour FastAPI
├── backend/
│   ├── app/                     # API FastAPI
│   ├── requirements.txt         # Dépendances backend locales
│   ├── .env.example             # Variables d'environnement
│   ├── database_init.sql        # Init MySQL
│   └── clean_db.sql
├── public/
│   ├── index.html               # Landing + auth
│   ├── dashboard.html           # Dashboard
│   └── assets/
│       ├── css/
│       └── js/
├── requirements.txt             # Dépendances runtime Vercel
├── vercel.json                  # Config Vercel
└── .python-version              # Version Python cible
```

## Corrections déjà appliquées

- parsing robuste de `DEBUG` et des variables d'environnement
- support de `DATABASE_URL` et fallback SQLite pour les tests locaux
- authentification Bearer corrigée sur `/api/auth/me`
- `PyMySQL` et `email-validator` ajoutés aux dépendances
- extraction du frontend vers des fichiers séparés dans `public/assets`
- ajout des routes CRUD pour les `parcelles`
- suppression des enregistrements de collecte branchée côté API
- script SQL corrigé pour être exécutable par MySQL

## Démarrage local

### 1. Backend

```bash
cd /home/blackblade/Téléchargements/project
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
cp backend/.env.example backend/.env
python3 -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

API locale :

- `http://localhost:8000/health`
- `http://localhost:8000/docs`

### 2. Frontend statique

```bash
cd /home/blackblade/Téléchargements/project/public
python3 -m http.server 3000
```

Frontend local :

- `http://localhost:3000`

### 3. Base de données MySQL

```bash
mysql -u root -p < /home/blackblade/Téléchargements/project/backend/database_init.sql
```

Compte démo créé par le SQL :

- email : `admin@agridata.app`
- mot de passe : le hash déjà présent dans la base

Pour un premier test réaliste, le plus simple est d'utiliser l'inscription depuis l'interface.

## Déploiement

Le guide complet est dans [docs/DEPLOY_VERCEL.md](/home/blackblade/Téléchargements/project/docs/DEPLOY_VERCEL.md).

En résumé :

1. pousser le projet sur GitHub
2. créer un projet Vercel à la racine du dépôt
3. configurer une base MySQL externe
4. renseigner les variables d'environnement Vercel
5. lancer un premier déploiement

## Variables d'environnement minimales

```env
SECRET_KEY=change-me
DATABASE_URL=mysql+pymysql://user:password@host:3306/agridata_db
CORS_ORIGINS=https://votre-domaine.vercel.app
```

Alternative si vous ne fournissez pas `DATABASE_URL` :

```env
DB_HOST=...
DB_PORT=3306
DB_USER=...
DB_PASSWORD=...
DB_NAME=agridata_db
```
