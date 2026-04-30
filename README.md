# AgriData Platform

Plateforme de gestion agricole avec suivi des exploitations, parcelles, données météo et qualité des sols.

## Fonctionnalités

### ✅ Implémenté
- **Authentification JWT** : Login/register avec tokens d'accès et refresh
- **Gestion des exploitations** : CRUD des fermes/exploitations
- **Gestion des parcelles** : CRUD des parcelles avec liaison aux exploitations
- **Collecte de données** :
  - Rendements des cultures
  - Données météo (température, humidité, précipitations)
  - Qualité des sols (pH, nutriments)
  - Intrants utilisés
- **Système d'alertes** : Notifications et alertes personnalisables
- **Analytics & Dashboard** : Statistiques et métriques des exploitations
- **Rapports automatisés** : Génération de rapports périodiques
- **Export de données** : Export CSV des données collectées
- **Persistence JSON** : Base de données fichier JSON thread-safe

### 🚀 Nouvelles fonctionnalités ajoutées
- **Système d'alertes/notifications** avec marquage lu/non lu
- **Export CSV** pour analyse externe des données
- **Dashboard amélioré** avec métriques globales
- **Pagination** dans toutes les listes d'API
- **Validation d'entrée** robuste avec Pydantic

## Architecture

```
backend/
├── app/
│   ├── main.py              # Application Flask principale
│   ├── config.py            # Configuration Pydantic
│   ├── database.py          # Base de données JSON thread-safe
│   ├── infrastructure/
│   │   └── models.py        # Modèles Pydantic
│   ├── application/
│   │   └── auth_service.py  # Services métier (auth, autorisation)
│   └── api/                 # Blueprints Flask
│       ├── auth.py
│       ├── exploitations.py
│       ├── parcelles.py
│       ├── data_collection.py
│       ├── analytics.py
│       └── alertes.py       # 🆕 Nouveau
├── data/
│   ├── scripts/
│   │   └── seed_database.py # Script d'initialisation
│   └── seed/                # Données d'exemple JSON
public/                      # Frontend statique
```

## Installation & Lancement

### Prérequis
- Python 3.8+
- pip

### Installation
```bash
# Cloner le repo
git clone <repo-url>
cd agridata

# Installer les dépendances
pip install -r requirements.txt

# Initialiser la base de données
python data/scripts/seed_database.py
```

### Lancement
```bash
# Développement
python deploy.py  # Puis choisir option 1

# Production
python deploy.py  # Puis choisir option 2

# Ou directement :
PYTHONPATH=. flask --app backend.app.main:app run --reload --port 8000
```

## API Endpoints

### Authentification
- `POST /api/auth/login` - Connexion
- `POST /api/auth/register` - Inscription
- `POST /api/auth/refresh` - Rafraîchir token
- `GET /api/auth/me` - Profil utilisateur

### Exploitations
- `GET /api/exploitations/` - Lister (avec pagination)
- `POST /api/exploitations/` - Créer
- `GET /api/exploitations/<id>` - Détails
- `PUT /api/exploitations/<id>` - Modifier
- `DELETE /api/exploitations/<id>` - Supprimer

### Parcelles
- `GET /api/parcelles/` - Lister (avec pagination)
- `POST /api/parcelles/` - Créer
- `GET /api/parcelles/<id>` - Détails
- `PUT /api/parcelles/<id>` - Modifier
- `DELETE /api/parcelles/<id>` - Supprimer

### Collecte de données
- `POST /api/data/rendements/` - Ajouter rendement
- `GET /api/data/rendements/` - Lister rendements
- `POST /api/data/meteo/` - Ajouter données météo
- `POST /api/data/sol/` - Ajouter analyse sol
- `POST /api/data/intrants/` - Ajouter intrant
- `GET /api/data/export/<table>` - 🆕 Export CSV

### Alertes 🆕
- `GET /api/alertes/` - Lister alertes
- `POST /api/alertes/` - Créer alerte
- `PUT /api/alertes/<id>/read` - Marquer comme lu
- `DELETE /api/alertes/<id>` - Supprimer

### Analytics
- `GET /api/analytics/exploitations/stats` - Stats exploitation
- `GET /api/analytics/dashboard` - Dashboard global
- `POST /api/analytics/reports/generate` - 🆕 Générer rapport

### Rapports 🆕
- `GET /api/rapports/` - Lister rapports (avec pagination)
- `GET /api/rapports/<id>` - Détails rapport
- `DELETE /api/rapports/<id>` - Supprimer rapport

## Sécurité

- **JWT Tokens** avec expiration
- **Hashing des mots de passe** avec bcrypt
- **Validation d'entrée** avec Pydantic
- **CORS configuré**
- **SECRET_KEY générée automatiquement**
- **Contrôle d'accès** par tenant et rôle

## Performance

- **Base JSON thread-safe** avec verrouillage
- **Pagination** sur toutes les listes
- **Lazy loading** des données
- **Cache-friendly** structure de données

## Données d'exemple

Utilisateur admin créé :
- Email: `admin@demo.com`
- Mot de passe: `password123`

## Tests

```bash
# Test endpoint santé
curl http://localhost:8000/health

# Test login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"tenant_id": 1, "email": "admin@demo.com", "password": "password123"}'
```

## Déploiement

### Vercel (recommandé)
```bash
vercel deploy --prod
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD ["gunicorn", "backend.app.main:app", "--bind", "0.0.0.0:8000"]
```

## Contribution

1. Fork le projet
2. Créer une branche feature
3. Commiter les changements
4. Push et créer une PR

## Licence

MIT