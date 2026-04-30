"""Authentication routes: login, register, token refresh, profile."""
from datetime import timedelta

from flask import Blueprint, g, jsonify, request

from backend.app.api.dependencies import require_auth
from backend.app.application.auth_service import AuthService
from backend.app.config import settings
from backend.app.domain.exceptions import InvalidCredentialsError

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/login")
def login():
    body = request.get_json(silent=True) or {}
    tenant_id = body.get("tenant_id")
    email = body.get("email")
    password = body.get("password")

    if not all([tenant_id, email, password]):
        return jsonify({"detail": "tenant_id, email and password are required"}), 400

    try:
        user, access_token, refresh_token = AuthService.authenticate_user(
            int(tenant_id), email, password
        )
    except InvalidCredentialsError as exc:
        return jsonify({"detail": str(exc)}), 401
    except Exception as exc:
        return jsonify({"detail": str(exc)}), 401

    return jsonify(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
    )


@auth_bp.post("/register")
def register():
    body = request.get_json(silent=True) or {}
    tenant_id = body.get("tenant_id")
    email = body.get("email")
    password = body.get("password")
    first_name = body.get("first_name")
    last_name = body.get("last_name")

    if not all([tenant_id, email, password]):
        return jsonify({"detail": "tenant_id, email and password are required"}), 400

    try:
        user = AuthService.create_user(
            int(tenant_id), email, password, first_name, last_name
        )
    except ValueError as exc:
        return jsonify({"detail": str(exc)}), 400
    except Exception as exc:
        return jsonify({"detail": str(exc)}), 400

    access_token = AuthService.create_access_token(
        {
            "sub": str(user.id),
            "tenant_id": user.tenant_id,
            "role": user.role,
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = AuthService.create_refresh_token(
        {"sub": str(user.id), "tenant_id": user.tenant_id}
    )
    return (
        jsonify(
            {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
            }
        ),
        201,
    )


@auth_bp.post("/refresh")
def refresh():
    body = request.get_json(silent=True) or {}
    token = body.get("refresh_token")
    if not token:
        return jsonify({"detail": "refresh_token is required"}), 400

    try:
        payload = AuthService.verify_token(token)
        if payload.get("type") != "refresh":
            raise ValueError("Invalid refresh token")
        user = AuthService.get_user_from_payload(payload)
    except Exception as exc:
        return jsonify({"detail": "Invalid refresh token"}), 401

    access_token = AuthService.create_access_token(
        {"sub": str(user.id), "tenant_id": user.tenant_id, "role": user.role}
    )
    new_refresh_token = AuthService.create_refresh_token(
        {"sub": str(user.id), "tenant_id": user.tenant_id}
    )
    return jsonify(
        {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }
    )


@auth_bp.get("/me")
@require_auth
def get_me():
    user = g.current_user
    return jsonify(
        {
            "id": user.id,
            "tenant_id": user.tenant_id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "role": user.role,
            "avatar_url": user.avatar_url,
            "last_login": user.last_login,
            "created_at": user.created_at,
        }
    )
