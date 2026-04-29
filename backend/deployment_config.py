"""
Configuration pour déploiement sur Render/Railway/PythonAnywhere
"""
import os

if os.environ.get("RENDER") or os.environ.get("RAILWAY_ENVIRONMENT"):
    from app.config import Settings
    
    class ProductionSettings(Settings):
        CORS_ORIGINS = [
            "https://agridata.onrender.com",
            "https://agridata-py.railway.app",
            "https://your-vercel-domain.vercel.app"
        ]
        
        
        DEBUG = False
        LOG_LEVEL = "INFO"


if os.environ.get("RENDER"):
    """
    Render.yml pour déploiement:
    
services:
  - type: web
    name: agridata-backend
    runtime: python
    runtimeVersion: '3.11'
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn --worker-class uvicorn.workers.UvicornWorker --workers 4 app.main:app
    envVars:
      - key: PYTHON_VERSION
        value: 3.11
      - key: RUNTIME_VERSION
        value: '3.11'
    
  - type: mysql
    name: agridata-db
    version: '8.0'
    plan: starter
    
  - type: static site
    name: agridata-frontend
    buildCommand: echo "Static content"
    routes:
      - path: /
        destination: /index.html
"""
    pass


if os.environ.get("RAILWAY_ENVIRONMENT"):
    """
    railway.json pour déploiement:
    
{
  "build": {
    "builder": "nixpacks"
  },
  "deploy": {
    "startCommand": "gunicorn --worker-class uvicorn.workers.UvicornWorker app.main:app",
    "restartPolicyMaxRetries": 5
  }
}

Environment Variables sur Railway:
- DB_HOST: mysql (internal service)
- DB_PORT: 3306
- DB_USER: tontine_user
- DB_PASSWORD: (auto-generated)
- DB_NAME: agridata_db
- SECRET_KEY: (generate secure key)
"""
    pass


if False:  # Enable when deploying to PythonAnywhere
    """
    Configuration PythonAnywhere:
    
    1. Login à pythonanywhere.com
    2. Upload code via Web tab
    3. Add custom web app
    4. Source code: /home/username/mysite/backend
    5. WSGI file: /home/username/mysite/backend/wsgi.py
    6. Virtualenv: /home/username/.virtualenvs/agridata
    
    Contenu wsgi.py:
    """
    
    import sys
    path = '/home/username/mysite/backend'
    if path not in sys.path:
        sys.path.append(path)
    
    from app.main import app as application
