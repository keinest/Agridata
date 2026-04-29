"""
WSGI file pour PythonAnywhere
Copier ce fichier à la racine du backend lors du déploiement sur PythonAnywhere
"""

import sys
import os

# Add backend to path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

# Set environment variables
os.environ.setdefault('DEBUG', 'False')

# Import FastAPI app
from app.main import app

# Create WSGI application
application = app

# For testing locally
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
