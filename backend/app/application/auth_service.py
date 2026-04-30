"""Authentication and authorization service for AgriData Platform."""
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

from jose import JWTError, jwt
from passlib.context import CryptContext

from backend.app.config import settings
from backend.app.database import db
from backend.app.domain.exceptions import (
    InvalidCredentialsError,
    UnauthorizedError,
    UserNotFoundError,
)
from backend.app.infrastructure.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


class AuthService:

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(
        data: Dict, expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + (
            expires_delta
            if expires_delta
            else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_refresh_token(data: Dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_token(token: str) -> Dict:
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            raise UnauthorizedError("Invalid token")

    @staticmethod
    def authenticate_user(
        tenant_id: int, email: str, password: str
    ) -> Tuple[User, str, str]:
        users = db.query("users", {"tenant_id": tenant_id, "email": email})
        if not users:
            raise InvalidCredentialsError("Invalid email or password")
        user_data = users[0]
        if not AuthService.verify_password(password, user_data.get("password_hash", "")):
            raise InvalidCredentialsError("Invalid email or password")
        # Update last login
        db.update("users", user_data["id"], {"last_login": datetime.utcnow().isoformat()})
        user = User(**user_data)
        access_token = AuthService.create_access_token(
            {"sub": str(user.id), "tenant_id": user.tenant_id, "role": user.role}
        )
        refresh_token = AuthService.create_refresh_token(
            {"sub": str(user.id), "tenant_id": user.tenant_id}
        )
        return user, access_token, refresh_token

    @staticmethod
    def create_user(
        tenant_id: int,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
    ) -> User:
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
            "active": True,
        }
        result = db.insert("users", user_data)
        return User(**result)

    @staticmethod
    def get_user_from_payload(payload: Dict) -> User:
        try:
            user_id = int(payload.get("sub"))
        except (TypeError, ValueError):
            raise UnauthorizedError("Invalid token payload")
        user_data = db.get_by_id("users", user_id)
        if not user_data or not user_data.get("active"):
            raise UserNotFoundError("User not found")
        return User(**user_data)

    @staticmethod
    def get_user_from_token(token: str) -> User:
        payload = AuthService.verify_token(token)
        return AuthService.get_user_from_payload(payload)


class AuthorizationService:

    ROLE_PERMISSIONS = {
        "admin": ["read", "write", "delete", "manage"],
        "consultant": ["read", "write"],
        "agriculteur": ["read", "write"],
    }

    @staticmethod
    def has_permission(user: User, permission: str) -> bool:
        perms = AuthorizationService.ROLE_PERMISSIONS.get(user.role or "agriculteur", [])
        return permission in perms

    @staticmethod
    def can_access_exploitation(user: User, exploitation: Any) -> bool:
        if user.role == "admin":
            return user.tenant_id == exploitation.tenant_id
        if user.role == "consultant":
            return user.tenant_id == exploitation.tenant_id
        # agriculteur: must own the exploitation
        return (
            user.tenant_id == exploitation.tenant_id
            and user.id == exploitation.owner_id
        )
