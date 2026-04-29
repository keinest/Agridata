"""Authentication and Authorization Service"""
from datetime import datetime, timedelta
from typing import Any, Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.config import settings
from app.infrastructure.models import User
from app.domain.exceptions import InvalidCredentialsError, UserNotFoundError, UnauthorizedError

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Authentication and authorization service"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
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
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> dict:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            raise UnauthorizedError("Invalid token")
    
    @staticmethod
    def authenticate_user(db: Session, tenant_id: int, email: str, password: str) -> User:
        """Authenticate user with email and password"""
        user = db.query(User).filter(
            User.tenant_id == tenant_id,
            User.email == email,
            User.active == True
        ).first()
        
        if not user:
            raise InvalidCredentialsError("Invalid email or password")
        
        if not AuthService.verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")

        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def create_user(db: Session, tenant_id: int, email: str, password: str, first_name: str, last_name: str) -> User:
        """Create new user"""
        # Check if user already exists in this tenant
        existing_user = db.query(User).filter(
            User.tenant_id == tenant_id,
            User.email == email
        ).first()
        
        if existing_user:
            raise ValueError("User already exists in this tenant")
        
        # Create user
        user = User(
            tenant_id=tenant_id,
            email=email,
            password_hash=AuthService.hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role="agriculteur"
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def extract_identity(payload: dict[str, Any]) -> tuple[int, int]:
        """Normalize user identity fields from token claims."""
        try:
            user_id = int(payload.get("sub"))
            tenant_id = int(payload.get("tenant_id"))
        except (TypeError, ValueError):
            raise UnauthorizedError("Invalid token")

        return user_id, tenant_id

    @staticmethod
    def get_user_from_payload(db: Session, payload: dict[str, Any]) -> User:
        """Get user directly from decoded JWT claims."""
        user_id, tenant_id = AuthService.extract_identity(payload)

        user = db.query(User).filter(
            User.id == user_id,
            User.tenant_id == tenant_id,
            User.active == True
        ).first()

        if not user:
            raise UserNotFoundError("User not found")

        return user
    
    @staticmethod
    def get_user_from_token(db: Session, token: str) -> User:
        """Get user from JWT token"""
        payload = AuthService.verify_token(token)
        return AuthService.get_user_from_payload(db, payload)


class AuthorizationService:
    """Authorization service for role-based access control"""
    
    # Define permissions by role
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
        """Check if user has permission"""
        if user.role not in AuthorizationService.ROLE_PERMISSIONS:
            return False
        
        return AuthorizationService.ROLE_PERMISSIONS[user.role].get(permission, False)
    
    @staticmethod
    def can_access_exploitation(user: User, exploitation) -> bool:
        """Check if user can access exploitation"""
        if user.role == "admin":
            return True
        if user.role == "consultant":
            return user.tenant_id == exploitation.tenant_id
        if user.role == "agriculteur":
            return user.id == exploitation.owner_id
        return False
