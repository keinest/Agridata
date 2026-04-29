from datetime import datetime, timedelta
from typing import Any, Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.config import settings
from app.infrastructure.models import User
from app.database import db
from app.domain.exceptions import InvalidCredentialsError, UserNotFoundError, UnauthorizedError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            raise UnauthorizedError("Invalid token")

    @staticmethod
    def authenticate_user(tenant_id: int, email: str, password: str) -> User:
        users = db.query("users", {"tenant_id": tenant_id, "email": email, "active": True})
        if not users:
            raise InvalidCredentialsError("Invalid email or password")

        user_data = users[0]
        if not AuthService.verify_password(password, user_data["password_hash"]):
            raise InvalidCredentialsError("Invalid email or password")

        user_data["last_login"] = datetime.utcnow().isoformat()
        db.update("users", user_data["id"], {"last_login": user_data["last_login"]})
        return User(**user_data)

    @staticmethod
    def create_user(tenant_id: int, email: str, password: str, first_name: str, last_name: str) -> User:
        existing_users = db.query("users", {"tenant_id": tenant_id, "email": email})
        if existing_users:
            raise ValueError("User already exists in this tenant")

        user_data = {
            "tenant_id": tenant_id,
            "email": email,
            "password_hash": AuthService.hash_password(password),
            "first_name": first_name,
            "last_name": last_name,
            "role": "agriculteur",
            "active": True
        }

        result = db.insert("users", user_data)
        return User(**result)

    @staticmethod
    def extract_identity(payload: dict[str, Any]) -> tuple[int, int]:
        try:
            user_id = int(payload.get("sub"))
            tenant_id = int(payload.get("tenant_id"))
        except (TypeError, ValueError):
            raise UnauthorizedError("Invalid token")

        return user_id, tenant_id

    @staticmethod
    def get_user_from_payload(payload: dict[str, Any]) -> User:
        user_id, tenant_id = AuthService.extract_identity(payload)

        user_data = db.get_by_id("users", user_id)
        if not user_data or user_data.get("tenant_id") != tenant_id or not user_data.get("active", True):
            raise UserNotFoundError("User not found")

        return User(**user_data)

    @staticmethod
    def get_user_from_token(token: str) -> User:
        payload = AuthService.verify_token(token)
        return AuthService.get_user_from_payload(payload)

class AuthorizationService:
    ROLE_PERMISSIONS = {
        "admin": {
            "read_all_exploitations": True,
            "write_all_exploitations": False,
            "manage_users": True,
            "view_audit_logs": True,
            "manage_alerts": True,
            "generate_reports": True,
        },
        "consultant": {
            "read_all_exploitations": True,
            "write_all_exploitations": False,
            "manage_users": False,
            "view_audit_logs": False,
            "manage_alerts": True,
            "generate_reports": True,
        },
        "agriculteur": {
            "read_all_exploitations": False,
            "write_all_exploitations": False,
            "manage_users": False,
            "view_audit_logs": False,
            "manage_alerts": True,
            "generate_reports": False,
        },
    }

    @staticmethod
    def has_permission(user: User, permission: str) -> bool:
        if user.role not in AuthorizationService.ROLE_PERMISSIONS:
            return False

        return AuthorizationService.ROLE_PERMISSIONS[user.role].get(permission, False)

    @staticmethod
    def can_access_exploitation(user: User, exploitation) -> bool:
        if user.role == "admin":
            return True
        if user.role == "consultant":
            return user.tenant_id == exploitation.tenant_id
        if user.role == "agriculteur":
            return user.id == exploitation.owner_id
        return False
