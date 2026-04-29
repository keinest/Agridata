"""Shared API dependencies."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.application.auth_service import AuthService, AuthorizationService
from app.database import get_db
from app.infrastructure.models import Exploitation, Parcelle, User

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """Read the bearer token from the Authorization header."""
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        return AuthService.get_user_from_token(db, credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


def get_accessible_exploitation(
    db: Session,
    current_user: User,
    exploitation_id: int,
) -> Exploitation:
    """Ensure the current user can access the requested exploitation."""
    exploitation = db.query(Exploitation).filter(
        Exploitation.id == exploitation_id,
        Exploitation.tenant_id == current_user.tenant_id,
    ).first()

    if not exploitation:
        raise HTTPException(status_code=404, detail="Exploitation not found")

    if not AuthorizationService.can_access_exploitation(current_user, exploitation):
        raise HTTPException(status_code=403, detail="Access denied")

    return exploitation


def get_accessible_parcelle(
    db: Session,
    current_user: User,
    parcelle_id: int,
) -> Parcelle:
    """Ensure the current user can access the requested plot."""
    parcelle = db.query(Parcelle).filter(
        Parcelle.id == parcelle_id,
        Parcelle.tenant_id == current_user.tenant_id,
    ).first()

    if not parcelle:
        raise HTTPException(status_code=404, detail="Parcelle not found")

    if not AuthorizationService.can_access_exploitation(current_user, parcelle.exploitation):
        raise HTTPException(status_code=403, detail="Access denied")

    return parcelle
