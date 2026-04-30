"""Rapports et génération de rapports routes."""
from flask import Blueprint, g, jsonify, request

from backend.app.api.dependencies import require_auth
from backend.app.database import db

rapports_bp = Blueprint("rapports", __name__)


@rapports_bp.get("/")
@require_auth
def list_rapports():
    user = g.current_user
    exploitation_id = request.args.get("exploitation_id", type=int)
    report_type = request.args.get("report_type")
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)

    if per_page > 100:
        per_page = 100

    filters = {"tenant_id": user.tenant_id}
    if exploitation_id:
        filters["exploitation_id"] = exploitation_id
    if report_type:
        filters["report_type"] = report_type

    rapports_data = db.query("rapports", filters)
    rapports_data = sorted(rapports_data, key=lambda x: x.get("created_at", ""), reverse=True)

    # Pagination
    total = len(rapports_data)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_data = rapports_data[start:end]

    return jsonify({
        "data": paginated_data,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    })


@rapports_bp.get("/<int:rapport_id>")
@require_auth
def get_rapport(rapport_id: int):
    user = g.current_user
    rapport = db.get_by_id("rapports", rapport_id)
    if not rapport or rapport.get("tenant_id") != user.tenant_id:
        return jsonify({"detail": "Rapport not found"}), 404
    return jsonify(rapport)


@rapports_bp.delete("/<int:rapport_id>")
@require_auth
def delete_rapport(rapport_id: int):
    user = g.current_user
    rapport = db.get_by_id("rapports", rapport_id)
    if not rapport or rapport.get("tenant_id") != user.tenant_id:
        return jsonify({"detail": "Rapport not found"}), 404
    db.delete("rapports", rapport_id)
    return jsonify({"detail": "Rapport deleted"})