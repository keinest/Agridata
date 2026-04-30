"""Parcelles CRUD routes."""
from flask import Blueprint, g, jsonify, request

from backend.app.api.dependencies import (
    get_accessible_exploitation,
    get_accessible_parcelle,
    require_auth,
)
from backend.app.application.auth_service import AuthorizationService
from backend.app.database import db

parcelles_bp = Blueprint("parcelles", __name__)


@parcelles_bp.get("/")
@require_auth
def list_parcelles():
    user = g.current_user
    exploitation_id = request.args.get("exploitation_id", type=int)

    if exploitation_id:
        exploitation, err = get_accessible_exploitation(exploitation_id)
        if err:
            return err
        filters = {"exploitation_id": exploitation_id, "tenant_id": user.tenant_id}
    else:
        filters = {"tenant_id": user.tenant_id}

    parcelles_data = db.query("parcelles", filters)
    parcelles_data = sorted(parcelles_data, key=lambda x: x.get("name", ""))
    return jsonify(parcelles_data)


@parcelles_bp.post("/")
@require_auth
def create_parcelle():
    user = g.current_user
    body = request.get_json(silent=True) or {}

    exploitation_id = body.get("exploitation_id")
    if not exploitation_id:
        return jsonify({"detail": "'exploitation_id' is required"}), 400
    if not body.get("name"):
        return jsonify({"detail": "'name' is required"}), 400

    exploitation, err = get_accessible_exploitation(int(exploitation_id))
    if err:
        return err

    parcelle_data = {
        "tenant_id": user.tenant_id,
        "exploitation_id": exploitation.id,
        "name": body.get("name"),
        "area": body.get("area"),
        "area_unit": body.get("area_unit", "hectares"),
        "crop_type": body.get("crop_type"),
        "active": True,
    }
    result = db.insert("parcelles", parcelle_data)
    return jsonify(result), 201


@parcelles_bp.get("/<int:parcelle_id>")
@require_auth
def get_parcelle(parcelle_id: int):
    parcelle, err = get_accessible_parcelle(parcelle_id)
    if err:
        return err
    return jsonify(db.get_by_id("parcelles", parcelle_id))


@parcelles_bp.put("/<int:parcelle_id>")
@require_auth
def update_parcelle(parcelle_id: int):
    parcelle, err = get_accessible_parcelle(parcelle_id)
    if err:
        return err

    body = request.get_json(silent=True) or {}
    allowed_fields = ["name", "area", "area_unit", "crop_type", "exploitation_id"]
    updates = {k: v for k, v in body.items() if k in allowed_fields}
    updated = db.update("parcelles", parcelle_id, updates)
    if not updated:
        return jsonify({"detail": "Parcelle not found"}), 404
    return jsonify(updated)


@parcelles_bp.delete("/<int:parcelle_id>")
@require_auth
def delete_parcelle(parcelle_id: int):
    parcelle, err = get_accessible_parcelle(parcelle_id)
    if err:
        return err
    db.delete("parcelles", parcelle_id)
    return jsonify({"detail": "Parcelle deleted"})
