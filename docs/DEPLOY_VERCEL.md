# Déploiement complet sur Vercel

Ce projet est maintenant structuré pour un déploiement Vercel monorepo simple :

- `public/` sert les fichiers statiques
- `api/index.py` expose le backend FastAPI
- `requirements.txt` racine contient uniquement les dépendances runtime

## 1. Préparer le dépôt

Depuis la racine du projet :

```bash
cd /home/blackblade/Téléchargements/project
```

Si besoin, initialisez Git puis poussez le code :

```bash
git init
git add .
git commit -m "Prepare AgriData for Vercel deployment"
git branch -M main
git remote add origin <URL_DU_REPO>
git push -u origin main
```

## 2. Préparer la base de données

Vercel ne fournit pas un MySQL local dans la fonction Python. Il faut une base externe :

- PlanetScale
- Railway MySQL
- Aiven MySQL
- Neon/Postgres seulement si vous adaptez le driver SQLAlchemy

Dans l'état actuel du projet, le chemin le plus simple est un MySQL compatible `PyMySQL`.

Créez la base puis exécutez :

```bash
mysql -u <user> -p -h <host> < /home/blackblade/Téléchargements/project/backend/database_init.sql
```

## 3. Variables d'environnement à définir dans Vercel

Ajoutez au minimum :

```env
SECRET_KEY=une-cle-longue-et-secrete
DATABASE_URL=mysql+pymysql://USER:PASSWORD@HOST:3306/agridata_db
CORS_ORIGINS=https://votre-projet.vercel.app
```

Variables utiles en plus :

```env
DEBUG=false
APP_NAME=AgriData Platform
APP_VERSION=1.0.0
LOG_LEVEL=INFO
```

Si vous ne voulez pas utiliser `DATABASE_URL`, vous pouvez définir :

```env
DB_HOST=...
DB_PORT=3306
DB_USER=...
DB_PASSWORD=...
DB_NAME=agridata_db
```

## 4. Déployer depuis le dashboard Vercel

1. Ouvrez `https://vercel.com/new`.
2. Connectez GitHub.
3. Importez le dépôt.
4. Vérifiez que la racine du projet est bien `/`.
5. Laissez Vercel détecter la configuration.
6. Ajoutez les variables d'environnement.
7. Lancez `Deploy`.

Après le premier déploiement :

1. ouvrez `https://<votre-projet>.vercel.app/`
2. testez `https://<votre-projet>.vercel.app/health`
3. testez `https://<votre-projet>.vercel.app/docs`

## 5. Déployer avec la CLI Vercel

Installation :

```bash
npm install -g vercel
```

Connexion :

```bash
vercel login
```

Premier déploiement preview :

```bash
cd /home/blackblade/Téléchargements/project
vercel
```

Déploiement production :

```bash
vercel --prod
```

Déploiement sans questions interactives :

```bash
vercel --yes
```

## 6. Vérifications après déploiement

Checklist :

1. `GET /health` retourne `healthy`
2. `GET /docs` charge bien Swagger
3. la page d'accueil charge le CSS et le JS depuis `/assets/...`
4. inscription d'un utilisateur fonctionne
5. création d'une exploitation fonctionne
6. création d'une parcelle fonctionne
7. ajout d'un rendement fonctionne

## 7. Commandes utiles en local avant déploiement

Backend :

```bash
python3 -m compileall backend/app api
```

Validation JS :

```bash
node --check public/assets/js/app.js
node --check public/assets/js/dashboard.js
```

Lancer l'app Vercel en local :

```bash
vercel dev
```

## 8. Points d'attention en production

- Le backend FastAPI tourne comme une fonction Python Vercel unique.
- Il faut garder `requirements.txt` racine léger pour ne pas gonfler le bundle.
- `public/` est la seule source statique servie par Vercel dans cette config.
- Les fichiers historiques dans `frontend/` peuvent rester comme référence, mais le déploiement utilise `public/`.
- Si vous changez de domaine final, mettez à jour `CORS_ORIGINS`.

## 9. Si le déploiement échoue

Vérifiez en priorité :

1. `DATABASE_URL` est bien au format `mysql+pymysql://...`
2. la base est accessible publiquement depuis Vercel
3. `SECRET_KEY` est défini
4. le projet est bien déployé depuis la racine
5. les logs Vercel ne montrent pas un problème de dépendance Python
