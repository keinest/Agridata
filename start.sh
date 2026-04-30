#!/bin/bash
# Script de lancement rapide pour AgriData Platform

echo "🚀 AgriData Platform - Lancement rapide"
echo "========================================"

# Vérifier si les dépendances sont installées
if ! python3 -c "import flask, pydantic, passlib" 2>/dev/null; then
    echo "❌ Dépendances manquantes. Installez-les avec:"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Vérifier si la base de données est initialisée
if [ ! -f "data/tenants.json" ]; then
    echo "📊 Initialisation de la base de données..."
    PYTHONPATH=. python3 data/scripts/seed_database.py
fi

echo "✅ Prêt à démarrer!"
echo ""
echo "Choisissez le mode de lancement:"
echo "1) Développement (avec rechargement auto)"
echo "2) Production (gunicorn)"
echo "3) Test rapide (chargement seulement)"
echo ""

read -p "Votre choix [1-3]: " choice

case $choice in
    1)
        echo "🏃 Lancement en mode développement..."
        echo "   App: http://localhost:8000"
        echo "   API Docs: http://localhost:8000/api/docs"
        echo "   Ctrl+C pour arrêter"
        echo ""
        PYTHONPATH=. flask --app backend.app.main:app run --reload --host 0.0.0.0 --port 8000
        ;;
    2)
        echo "🏭 Lancement en mode production..."
        echo "   App: http://localhost:8000"
        echo "   Utilise 4 workers gunicorn"
        echo "   Ctrl+C pour arrêter"
        echo ""
        PYTHONPATH=. gunicorn "backend.app.main:app" --bind 0.0.0.0:8000 --workers 4
        ;;
    3)
        echo "🧪 Test de chargement..."
        PYTHONPATH=. python3 -c "
from backend.app.main import app
print('✅ Application chargée avec succès!')
print(f'📊 Routes enregistrées: {len(app.url_map._rules)}')
print('🔗 Endpoints disponibles:')
for rule in sorted(app.url_map._rules, key=lambda x: x.rule):
    if not rule.rule.startswith('/static'):
        methods = ','.join(rule.methods - {'HEAD', 'OPTIONS'})
        print(f'   {methods:8} {rule.rule}')
"
        ;;
    *)
        echo "❌ Choix invalide"
        exit 1
        ;;
esac