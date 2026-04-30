"""Flask authentication decorators and dependency helpers."""
from functools import wraps

from flask import g, jsonify, request

from backend.app.application.auth_service import AuthService, AuthorizationService
from backend.app.database import db
from backend.app.domain.exceptions import UnauthorizedError
from backend.app.infrastructure.models import Exploitation, Parcelle


def _extract_token() -> str | None:
    auth_header = request.headers.get("Authorization", "")
    parts = auth_header.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def require_auth(f):
    """Decorator: validates JWT and sets g.current_user."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_token()
        if not token:
            return jsonify({"detail": "Not authenticated"}), 401
        try:
            user = AuthService.get_user_from_token(token)
        except Exception as exc:
            return jsonify({"detail": str(exc)}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated


def get_accessible_exploitation(exploitation_id: int):
    """Return Exploitation if current user may access it, else abort."""
    exploitation_data = db.get_by_id("exploitations", exploitation_id)
    if not exploitation_data:
        return None, (jsonify({"detail": "Exploitation not found"}), 404)
    exploitation = Exploitation(**exploitation_data)
    if exploitation.tenant_id != g.current_user.tenant_id:
        return None, (jsonify({"detail": "Access denied"}), 403)
    if not AuthorizationService.can_access_exploitation(g.current_user, exploitation):
        return None, (jsonify({"detail": "Access denied"}), 403)
    return exploitation, None


def get_accessible_parcelle(parcelle_id: int):
    """Return Parcelle if current user may access it, else abort."""
    parcelle_data = db.get_by_id("parcelles", parcelle_id)
    if not parcelle_data:
        return None, (jsonify({"detail": "Parcelle not found"}), 404)
    parcelle = Parcelle(**parcelle_data)
    exploitation, err = get_accessible_exploitation(parcelle.exploitation_id)
    if err:
        return None, err
    return parcelle, None
