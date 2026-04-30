"""Alertes et notifications routes."""
from flask import Blueprint, g, jsonify, request

from backend.app.api.dependencies import require_auth
from backend.app.database import db

alertes_bp = Blueprint("alertes", __name__)


@alertes_bp.get("/")
@require_auth
def list_alertes():
    user = g.current_user
    exploitation_id = request.args.get("exploitation_id", type=int)
    is_read = request.args.get("is_read", type=bool)

    filters = {"tenant_id": user.tenant_id}
    if exploitation_id:
        filters["exploitation_id"] = exploitation_id
    if is_read is not None:
        filters["is_read"] = is_read

    alertes_data = db.query("alertes", filters)
    return jsonify(sorted(alertes_data, key=lambda a: a.get("created_at", ""), reverse=True))


@alertes_bp.post("/")
@require_auth
def create_alerte():
    user = g.current_user
    body = request.get_json(silent=True) or {}

    exploitation_id = body.get("exploitation_id")
    if not exploitation_id:
        return jsonify({"detail": "'exploitation_id' is required"}), 400
    if not body.get("title"):
        return jsonify({"detail": "'title' is required"}), 400

    alerte_data = {
        "tenant_id": user.tenant_id,
        "exploitation_id": int(exploitation_id),
        "severity": body.get("severity", "warning"),
        "title": body.get("title"),
        "description": body.get("description"),
        "threshold_value": body.get("threshold_value"),
        "actual_value": body.get("actual_value"),
        "is_read": False,
    }
    result = db.insert("alertes", alerte_data)
    return jsonify(result), 201


@alertes_bp.put("/<int:alerte_id>/read")
@require_auth
def mark_alerte_read(alerte_id: int):
    user = g.current_user
    alerte = db.get_by_id("alertes", alerte_id)
    if not alerte or alerte.get("tenant_id") != user.tenant_id:
        return jsonify({"detail": "Alerte not found"}), 404

    updated = db.update("alertes", alerte_id, {"is_read": True, "acknowledged_at": db._get_current_timestamp()})
    if not updated:
        return jsonify({"detail": "Alerte not found"}), 404
    return jsonify(updated)


@alertes_bp.delete("/<int:alerte_id>")
@require_auth
def delete_alerte(alerte_id: int):
    user = g.current_user
    alerte = db.get_by_id("alertes", alerte_id)
    if not alerte or alerte.get("tenant_id") != user.tenant_id:
        return jsonify({"detail": "Alerte not found"}), 404
    db.delete("alertes", alerte_id)
    return jsonify({"detail": "Alerte deleted"})