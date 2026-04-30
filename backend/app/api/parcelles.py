"""Parcelles CRUD routes."""
from flask import Blueprint, g, jsonify, request
from pydantic import BaseModel, ValidationError

from backend.app.api.dependencies import (
    get_accessible_exploitation,
    get_accessible_parcelle,
    require_auth,
)
from backend.app.application.auth_service import AuthorizationService
from backend.app.database import db

parcelles_bp = Blueprint("parcelles", __name__)


class ParcelleCreate(BaseModel):
    exploitation_id: int
    name: str
    area: float = None
    area_unit: str = "hectares"
    crop_type: str = None


class ParcelleUpdate(BaseModel):
    name: str = None
    area: float = None
    area_unit: str = None
    crop_type: str = None


@parcelles_bp.get("/")
@require_auth
def list_parcelles():
    user = g.current_user
    exploitation_id = request.args.get("exploitation_id", type=int)
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    if per_page > 100:
        per_page = 100

    if exploitation_id:
        exploitation, err = get_accessible_exploitation(exploitation_id)
        if err:
            return err
        filters = {"exploitation_id": exploitation_id, "tenant_id": user.tenant_id}
    else:
        filters = {"tenant_id": user.tenant_id}

    parcelles_data = db.query("parcelles", filters)
    parcelles_data = sorted(parcelles_data, key=lambda x: x.get("name", ""))

    # Pagination
    total = len(parcelles_data)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = parcelles_data[start:end]

    return jsonify({
        "data": paginated_data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    })


@parcelles_bp.post("/")
@require_auth
def create_parcelle():
    user = g.current_user
    body = request.get_json(silent=True) or {}

    try:
        parcelle_data = ParcelleCreate(**body)
    except ValidationError as e:
        return jsonify({"detail": "Invalid input data", "errors": e.errors()}), 400

    exploitation, err = get_accessible_exploitation(parcelle_data.exploitation_id)
    if err:
        return err

    data = {
        "tenant_id": user.tenant_id,
        "exploitation_id": exploitation.id,
        "name": parcelle_data.name,
        "area": parcelle_data.area,
        "area_unit": parcelle_data.area_unit,
        "crop_type": parcelle_data.crop_type,
        "active": True,
    }
    result = db.insert("parcelles", data)
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

    try:
        update_data = ParcelleUpdate(**body)
    except ValidationError as e:
        return jsonify({"detail": "Invalid input data", "errors": e.errors()}), 400

    updates = update_data.model_dump(exclude_unset=True)
    if not updates:
        return jsonify({"detail": "No valid fields to update"}), 400

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
