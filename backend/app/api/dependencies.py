from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends
from app.application.auth_service import AuthService, AuthorizationService
from app.database import db
from app.infrastructure.models import Exploitation, Parcelle, User

security = HTTPBearer(auto_error=False)

def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        return AuthService.get_user_from_token(credentials.credentials)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc

def get_accessible_exploitation(
    current_user: User,
    exploitation_id: int,
) -> Exploitation:
    exploitation_data = db.get_by_id("exploitations", exploitation_id)
    if not exploitation_data or exploitation_data.get("tenant_id") != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Exploitation not found")

    exploitation = Exploitation(**exploitation_data)
    if not AuthorizationService.can_access_exploitation(current_user, exploitation):
        raise HTTPException(status_code=403, detail="Access denied")

    return exploitation

def get_accessible_parcelle(
    current_user: User,
    parcelle_id: int,
) -> Parcelle:
    parcelle_data = db.get_by_id("parcelles", parcelle_id)
    if not parcelle_data or parcelle_data.get("tenant_id") != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Parcelle not found")

    parcelle = Parcelle(**parcelle_data)
    exploitation = get_accessible_exploitation(current_user, parcelle.exploitation_id)
    return parcelle
